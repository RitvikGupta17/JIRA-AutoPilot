# Sprint_Manager/Agents/scrum_master_agent.py
import requests
from .base_agent import BaseAgent
from datetime import date

class ScrumMasterAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token, sprint_id, kb):
        super().__init__(jira_domain, jira_email, api_token)
        self.sprint_id = sprint_id
        self.kb = kb

    def _record_sprint_health(self, sprint_issues):
        done_issues = sum(1 for issue in sprint_issues if issue['fields']['status']['name'].lower() == 'done')
        try:
            cursor = self.kb.conn.cursor()
            today = date.today().isoformat()
            cursor.execute('INSERT OR REPLACE INTO sprint_history (sprint_id, end_date, completed_points) VALUES (?, ?, ?)',
                           (self.sprint_id, today, done_issues))
            self.kb.conn.commit()
            print(f"  [DB] Knowledge Base updated for Sprint {self.sprint_id}. Completed issues: {done_issues}")
            return done_issues
        except Exception as e:
            print(f"  [DB] Error updating Knowledge Base: {e}")
            return 0

    def execute(self):
        """Monitors sprint health and returns a string report."""
        print("\n--- 🕵️ Scrum Master Agent ---")
        print(f"Perceiving health of Sprint ID: {self.sprint_id}...")
        report_lines = []

        sprint_url = f"{self.jira_domain}/rest/agile/1.0/sprint/{self.sprint_id}/issue"
        params = {'fields': 'summary,status'}

        try:
            response = requests.get(sprint_url, headers=self.headers, auth=self.auth, params=params)
            response.raise_for_status()
            sprint_issues = response.json().get('issues', [])
            
            total_issues = len(sprint_issues)
            print(f"Found {total_issues} total issues in the sprint.")
            report_lines.append(f"Found {total_issues} total issues in the sprint:")

            for issue in sprint_issues:
                status = issue['fields']['status']['name']
                line = f"- {issue['key']}: {issue['fields']['summary']} (Status: {status})"
                print(f"  {line}")
                report_lines.append(line)
            
            if sprint_issues:
                completed_count = self._record_sprint_health(sprint_issues)
                report_lines.append(f"\n**Total Completed Issues**: {completed_count}")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            report_lines.append(f"HTTP Error encountered: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
            
        return "\n".join(report_lines)