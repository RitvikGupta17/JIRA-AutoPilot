# Sprint_Manager/Agents/QA_release_agent.py
import requests
from .base_agent import BaseAgent

class QAReleaseAgent(BaseAgent):
    def execute(self):
        """Monitors tickets in review and returns a string report."""
        print("\n--- 📦 QA & Release Agent ---")
        print("Perceiving tickets ready for review...")
        report_lines = []

        search_url = f"{self.jira_domain}/rest/api/3/search/jql"
        data = { "jql": 'status = "In Review"', "fields": ["key", "summary"] }
        
        try:
            response = requests.post(search_url, headers=self.headers, json=data, auth=self.auth)
            response.raise_for_status()
            review_issues = response.json().get('issues', [])
            
            if review_issues:
                print(f"Found {len(review_issues)} tickets in review.")
                report_lines.append(f"**Found {len(review_issues)} tickets ready for QA review:**")
                for issue in review_issues:
                    line = f"- {issue['key']}: {issue['fields']['summary']}"
                    print(f"  {line}")
                    report_lines.append(line)
            else:
                print("No tickets are currently in review.")
                report_lines.append("No tickets are currently in review.")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            report_lines.append(f"HTTP Error encountered: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
        
        return "\n".join(report_lines)