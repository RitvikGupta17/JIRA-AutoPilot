# Sprint_Manager/Agents/scrum_master_agent.py
import requests
import re
from datetime import datetime, date
from .base_agent import BaseAgent
from ..Services.jira_service import JiraService

class ScrumMasterAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token, sprint_id, kb, message_broker):
        super().__init__(jira_domain, jira_email, api_token)
        self.sprint_id = sprint_id
        self.kb = kb
        self.message_broker = message_broker
        self.jira_service = JiraService(self.auth, self.headers, self.jira_domain) # For autonomous action

    def _record_sprint_health(self, sprint_issues):
        """Records the number of completed issues into the Knowledge Base."""
        done_issues = sum(1 for issue in sprint_issues if issue['fields']['status']['name'].lower() == 'done')
        try:
            cursor = self.kb.conn.cursor()
            today = date.today().isoformat()
            # Note: We are not calculating team_velocity here, but storing completed_points for later calculation.
            cursor.execute('INSERT OR REPLACE INTO sprint_history (sprint_id, end_date, completed_points) VALUES (?, ?, ?)',
                           (self.sprint_id, today, done_issues))
            self.kb.conn.commit()
            print(f"  [DB] Knowledge Base updated for Sprint {self.sprint_id}. Completed issues: {done_issues}")
            return done_issues
        except Exception as e:
            print(f"  [DB] Error updating Knowledge Base: {e}")
            return 0

    def _handle_blocker_message(self, message):
        """Processes a blocker/no-code message and takes autonomous action (commenting)."""
        match = re.search(r'Issue ([\w-]+)', message['content'])
        if not match:
            return f"Error: Could not parse issue key from message."
        issue_key = match.group(1)
        
        comment_body = (
            f"🚨 **JIRA AutoPilot Alert ({message['sender']})** 🚨\n\n"
            f"An autonomous agent detected a high-priority issue on this ticket:\n"
            f"**{message['content']}**\n"
            f"Escalating for immediate review and action."
        )
        
        # Autonomous Action: Add a high-priority comment
        if self.jira_service.add_comment(issue_key, comment_body):
            # Optional: Add code here to update status to "Blocked" if your JIRA instance has it.
            return f"✅ AutoPilot Action: Added escalation comment to **{issue_key}**."
        else:
            return f"❌ AutoPilot Action Failed: Could not add comment to {issue_key}."


    # --- DATA-DRIVEN INTELLIGENCE: Velocity Risk & Scope Creep ---
    def _analyze_sprint_risk(self, completed_count, sprint_details, sprint_issues):
        """Predicts risk based on velocity AND detects Scope Creep."""
        report = []
        
        # Parse Sprint Dates
        start_str = sprint_details.get('startDate')
        end_str = sprint_details.get('endDate')
        
        if not start_str or not end_str:
            return ["⚠️ Could not calculate risk: Sprint dates missing."]

        try:
            # Handle JIRA's ISO format (split by '.' before parsing)
            start_date = datetime.strptime(start_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
            now = datetime.now()
        except ValueError:
             return ["⚠️ Could not calculate risk: Date format error."]

        # 1. SCOPE CREEP DETECTOR
        scope_creep_issues = []
        for issue in sprint_issues:
            created_str = issue['fields'].get('created')
            if created_str:
                try:
                    created_date = datetime.strptime(created_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    # Check if created date is after the sprint started
                    if created_date > start_date:
                        scope_creep_issues.append(issue['key'])
                except:
                    pass
        
        if scope_creep_issues:
            report.append(f"\n🚨 **SCOPE CREEP DETECTED**")
            report.append(f"**{len(scope_creep_issues)} tickets** were added after the sprint started!")
            report.append(f"Impacted Tickets: {', '.join(scope_creep_issues)}")

        # 2. Velocity Risk Calculation
        total_duration = (end_date - start_date).total_seconds()
        elapsed_duration = (now - start_date).total_seconds()
        if elapsed_duration < 0: elapsed_duration = 0
        progress_pct = elapsed_duration / total_duration if total_duration > 0 else 1.0
        
        avg_velocity = self.kb.get_average_velocity()
        expected_completion = avg_velocity * progress_pct
        
        report.append(f"\n**📊 Velocity Analysis** (Historical Avg: {avg_velocity:.1f})")
        
        if progress_pct > 0.0:
            if completed_count < (expected_completion * 0.7):
                report.append("🔴 **RISK LEVEL: HIGH**. Team is significantly behind pace.")
            elif completed_count < (expected_completion * 0.9):
                report.append("🟡 **RISK LEVEL: MEDIUM**. Team is slightly behind pace.")
            else:
                report.append("🟢 **RISK LEVEL: LOW**. Sprint is on track.")
        else:
            report.append("--- Risk analysis will begin once sprint progress is measurable. ---")
            
        return report

    # --- DATA-DRIVEN INTELLIGENCE: Workload Balancing ---
    def _analyze_workload_balance(self):
        """Analyzes team workload and suggests reassignments."""
        report = []
        developers = self.kb.get_all_developer_profiles() # [(id, name, load), ...]
        
        if not developers:
            return []

        report.append(f"\n**⚖️ Workload Balance Insights**")
        
        total_load = sum(d[2] for d in developers)
        avg_load = total_load / len(developers) if developers else 0
        
        overworked = []
        underworked = []
        
        # 1.5 item standard deviation for imbalance detection
        for dev_id, name, load in developers:
            if load > (avg_load + 1.5): 
                overworked.append((name, load))
            elif load < (avg_load - 1.5) and load < avg_load: 
                underworked.append((name, load))
                
        if overworked and underworked:
            report.append(f"- ⚠️ **Imbalance Detected**: Average load is {avg_load:.1f} items.")
            for ow in overworked:
                report.append(f"  - **{ow[0]}** is overloaded ({ow[1]} items).")
            for uw in underworked:
                report.append(f"  - **{uw[0]}** has capacity ({uw[1]} items).")
            
            report.append(f"- 💡 **Suggestion**: Consider moving a task from **{overworked[0][0]}** to **{underworked[0][0]}**.")
        elif not overworked and not underworked:
            report.append("- ✅ Team workload is well-balanced.")
        else:
            report.append(f"- Team workload analysis complete. Average load: {avg_load:.1f}")
            
        return report

    # --- DATA-DRIVEN INTELLIGENCE: Retrospective Insights ---
    def _generate_retrospective_insights(self, sprint_issues):
        """Generates quick wins and identifies potential bottlenecks."""
        report = []
        report.append(f"\n**🔍 Retrospective Insights**")
        
        # Identify "Quick Wins" (Done tickets)
        done_issues = [i for i in sprint_issues if i['fields']['status']['name'] == 'Done']
        if done_issues:
            report.append(f"- 🏆 **Completed Stories**: {len(done_issues)}")
            # List top 2
            for i in done_issues[:2]:
                report.append(f"  - {i['key']}: {i['fields']['summary']}")
        
        # Identify "Stuck" issues (In Progress but not Done)
        stuck_issues = [i for i in sprint_issues if i['fields']['status']['name'] in ['In Progress', 'In Review']]
        if stuck_issues:
            report.append(f"- 🚧 **Potential Bottlenecks** ({len(stuck_issues)} active):")
            for i in stuck_issues[:2]:
                report.append(f"  - {i['key']} is still active.")
        else:
             report.append(f"- No items currently appear stuck.")
                
        return report


    def execute(self):
        """Monitors sprint health, runs all data analysis, and handles inter-agent communication."""
        print("\n--- 🕵️ Scrum Master Agent (Data-Enhanced) ---")
        
        # 1. Fetch Sprint Details (Needed for Dates)
        sprint_info_url = f"{self.jira_domain}/rest/agile/1.0/sprint/{self.sprint_id}"
        try:
            r = requests.get(sprint_info_url, headers=self.headers, auth=self.auth)
            r.raise_for_status()
            sprint_details = r.json()
        except Exception as e:
            print(f"Warning: Could not fetch sprint details: {e}")
            sprint_details = {}

        report_lines = []

        # 2. Fetch Sprint Issues
        sprint_url = f"{self.jira_domain}/rest/agile/1.0/sprint/{self.sprint_id}/issue"
        # CRITICAL: We need 'created' for Scope Creep detection
        params = {'fields': 'summary,status,created'} 

        try:
            response = requests.get(sprint_url, headers=self.headers, auth=self.auth, params=params)
            response.raise_for_status()
            sprint_issues = response.json().get('issues', [])
            
            total_issues = len(sprint_issues)
            report_lines.append(f"**Sprint Health Report** (Total Issues: {total_issues})")

            # 3. Basic Status Listing
            for issue in sprint_issues:
                status = issue['fields']['status']['name']
                line = f"- {issue['key']}: {issue['fields']['summary']} (Status: {status})"
                report_lines.append(line)
            
            # 4. Record Health & Run Data Intelligence
            if sprint_issues:
                completed_count = self._record_sprint_health(sprint_issues)
                report_lines.append(f"\n**Total Completed Issues**: {completed_count}")
                
                # A. Risk & Scope Analysis
                risk_report = self._analyze_sprint_risk(completed_count, sprint_details, sprint_issues)
                report_lines.extend(risk_report)
                
                # B. Workload Balance
                balance_report = self._analyze_workload_balance()
                report_lines.extend(balance_report)
                
                # C. Retrospective Insights
                retro_report = self._generate_retrospective_insights(sprint_issues)
                report_lines.extend(retro_report)

            # 5. Inter-Agent Communication and Autonomous Actions
            print("\n  [Broker] Checking Message Broker for inter-agent communication...")
            broker_messages = []
            blocker_actions = [] 
            
            while True:
                message = self.message_broker.subscribe()
                if message:
                    if 'BLOCKER_DETECTED' in message['content'] or 'NO_CODE_ACTIVITY' in message['content']:
                        action_summary = self._handle_blocker_message(message)
                        blocker_actions.append(action_summary)
                    broker_messages.append(f"- **{message['sender']}**: {message['content']}")
                else:
                    break
            
            if broker_messages:
                report_lines.append("\n**Inter-Agent Communication:**")
                report_lines.extend(broker_messages)
            
            if blocker_actions:
                report_lines.append("\n**Autonomous Actions Taken:**")
                report_lines.extend(blocker_actions)

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            report_lines.append(f"HTTP Error encountered: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
            
        return "\n".join(report_lines)