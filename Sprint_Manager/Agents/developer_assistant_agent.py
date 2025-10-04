# Sprint_Manager/Agents/developer_assistant_agent.py
import requests
from .base_agent import BaseAgent
from ..Services.jira_service import JiraService
from ..Services.llm_service import LLMService

class DeveloperAssistantAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token):
        super().__init__(jira_domain, jira_email, api_token)
        self.jira_service = JiraService(self.auth, self.headers, self.jira_domain)
        self.llm_service = LLMService()
        self.analyzed_issues_count = 0

    def _get_text_from_comment_body(self, body):
        full_text = []
        if 'content' in body and isinstance(body['content'], list):
            for block in body['content']:
                if 'content' in block and isinstance(block['content'], list):
                    for element in block['content']:
                        if element.get('type') == 'text' and 'text' in element:
                            full_text.append(element['text'])
        return " ".join(full_text)

    def execute(self):
        """Analyzes assigned tickets and returns a string report of the findings."""
        print("\n--- 👨‍💻 Developer Assistant Agent ---")
        print("Perceiving assigned tasks...")
        
        report_lines = [] # <-- Start building the report
        search_url = f"{self.jira_domain}/rest/api/3/search/jql"
        data = { "jql": 'assignee = currentUser() AND status != "Done"', "fields": ["key", "summary"] }

        try:
            response = requests.post(search_url, headers=self.headers, json=data, auth=self.auth)
            response.raise_for_status()
            issues = response.json().get('issues', [])
            self.analyzed_issues_count = len(issues)
            print(f"Found {self.analyzed_issues_count} assigned issues.")
            report_lines.append(f"Found {self.analyzed_issues_count} assigned issues:")

            for issue in issues:
                issue_key, summary = issue['key'], issue['fields']['summary']
                print(f"\nAnalyzing ticket: {issue_key} - {summary}")

                comments = self.jira_service.get_comments_for_issue(issue_key)
                if not comments:
                    print("  -> No comments found.")
                    report_lines.append(f"- {issue_key}: No comments found.")
                    continue

                comment_text = self._get_text_from_comment_body(comments[-1]['body'])
                if not comment_text.strip():
                    print("  -> Latest comment has no text content.")
                    report_lines.append(f"- {issue_key}: Latest comment has no text content.")
                    continue
                
                print(f"  -> Latest Comment: \"{comment_text}\"")
                analysis = self.llm_service.analyze_comment(comment_text)
                print(f"  -> 🤖 LLM Analysis: {analysis}")
                report_lines.append(f"- **{issue_key}**: {summary}\n  - **LLM Analysis**: {analysis}")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            report_lines.append(f"HTTP Error encountered: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
            
        return "\n".join(report_lines) # <-- Return the final report string