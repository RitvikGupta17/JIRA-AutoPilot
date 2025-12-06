# Sprint_Manager/Agents/triage_agent.py
import requests
import json
from .base_agent import BaseAgent
from ..Services.jira_service import JiraService
from ..Services.llm_service import LLMService

class TriageAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token, kb):
        super().__init__(jira_domain, jira_email, api_token)
        self.jira_service = JiraService(self.auth, self.headers, self.jira_domain)
        self.llm_service = LLMService()
        self.kb = kb

    def execute(self):
        """Scans for new 'To Do' tickets, performs LLM triage, and auto-assigns."""
        print("\n--- 🧠 Triage Agent (Autonomous) ---")
        print("Perceiving untriaged tickets in 'To Do' status...")
        report_lines = []
        triage_count = 0

        # JQL: Find issues in 'To Do' that are unassigned
        # Note: We fetch 'customfield_10002' assuming it is Story Points, 
        # but for triage, we primarily need summary and description.
        search_url = f"{self.jira_domain}/rest/api/3/search/jql"
        data = { 
            "jql": 'status = "To Do" AND assignee IS EMPTY', 
            "fields": ["key", "summary", "description", "priority"] 
        } 
        
        try:
            response = requests.post(search_url, headers=self.headers, json=data, auth=self.auth)
            response.raise_for_status()
            untriaged_issues = response.json().get('issues', [])
            
            if not untriaged_issues:
                print("  No untriaged tickets found.")
                return "No untriaged, unassigned tickets found in 'To Do'."

            report_lines.append(f"Found {len(untriaged_issues)} untriaged tickets. Starting autonomous triage...")

            for issue in untriaged_issues:
                key = issue['key']
                summary = issue['fields']['summary']
                description = issue['fields'].get('description', '')
                
                # Handling description if it's a complex ADF object (Atlassian Document Format)
                if isinstance(description, dict):
                     # Simplified extraction for ADF; in prod, use a proper parser
                    description = "Complex description content" 

                print(f"\n  Processing {key}: {summary}")

                # 1. LLM Analysis
                analysis_json = self.llm_service.analyze_triage(summary, str(description))
                try:
                    triage_data = json.loads(analysis_json)
                    print(f"    🤖 LLM Prediction: {triage_data}")
                except json.JSONDecodeError:
                    print(f"    ❌ Error decoding LLM JSON for {key}")
                    report_lines.append(f"- {key}: Failed to parse LLM triage data.")
                    continue

                specialization = triage_data.get('specialization', 'FullStack')
                predicted_priority = triage_data.get('priority', 'Medium')
                
                # 2. Update Ticket Priority & Labels via JIRA API
                # (Assuming 'labels' field can be used to store the specialization)
                update_payload = {
                    "priority": {"name": predicted_priority},
                    "labels": [specialization]
                }
                self.jira_service.update_issue(key, update_payload)
                report_lines.append(f"- **{key}**: Classified as **{specialization}**, Priority set to **{predicted_priority}**.")

                # 3. Intelligent Assignment via Knowledge Base
                best_dev = self.kb.get_best_assignee(specialization)
                
                if best_dev:
                    dev_id, dev_name, current_load = best_dev
                    
                    # Assign in Jira
                    if self.jira_service.assign_issue(key, dev_id):
                        # Update KB workload (Assuming +1 for a new task)
                        new_load = current_load + 1
                        self.kb.update_developer_workload(dev_id, new_load)
                        
                        action_msg = f"    ✅ Auto-Assigned to **{dev_name}** (Load: {current_load} -> {new_load})"
                        print(action_msg)
                        report_lines.append(action_msg)
                        
                        # Add a comment to the ticket notifying the user
                        comment = (
                            f"🤖 **JIRA AutoPilot Triage**\n\n"
                            f"This ticket has been automatically analyzed and assigned to **{dev_name}** "
                            f"based on their **{specialization}** expertise and current workload.\n"
                            f"**Predicted Priority:** {predicted_priority}"
                        )
                        self.jira_service.add_comment(key, comment)
                        triage_count += 1
                    else:
                        report_lines.append(f"    ❌ Failed to assign {key} to {dev_name} in Jira.")
                else:
                    report_lines.append(f"    ⚠️ No available developer found for specialization: {specialization}")

            report_lines.append(f"\n**Summary:** {triage_count} tickets autonomously triaged and assigned.")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            report_lines.append(f"HTTP Error encountered: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
        
        return "\n".join(report_lines)