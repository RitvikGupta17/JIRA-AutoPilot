# Sprint_Manager/Agents/developer_assistant_agent.py
import requests
from .base_agent import BaseAgent
from ..Services.jira_service import JiraService
from ..Services.llm_service import LLMService
from ..Services.git_service import GitService

class DeveloperAssistantAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token, message_broker):
        super().__init__(jira_domain, jira_email, api_token)
        self.jira_service = JiraService(self.auth, self.headers, self.jira_domain)
        self.llm_service = LLMService()
        self.git_service = GitService()
        self.message_broker = message_broker
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
        """Analyzes assigned tickets, checks for code activity, and returns a string report."""
        print("\n--- 👨‍💻 Developer Assistant Agent ---")
        print("Perceiving assigned tasks...")
        
        report_lines = []
        search_url = f"{self.jira_domain}/rest/api/3/search/jql"
        data = { "jql": 'assignee = currentUser() AND status = "In Progress"', "fields": ["key", "summary"] } 

        try:
            response = requests.post(search_url, headers=self.headers, json=data, auth=self.auth)
            response.raise_for_status()
            issues = response.json().get('issues', [])
            self.analyzed_issues_count = len(issues)
            print(f"Found {self.analyzed_issues_count} assigned issues in 'In Progress'.")
            report_lines.append(f"Found {self.analyzed_issues_count} assigned issues in 'In Progress':")

            for issue in issues:
                issue_key, summary = issue['key'], issue['fields']['summary']
                
                # 1. Code-Ticket Link Monitoring
                if not self.git_service.check_recent_activity(issue_key, lookback_days=2):
                    comment_body = (
                        f"🤖 **JIRA AutoPilot (Code Monitor)** 🤖\n\n"
                        f"I noticed this ticket ({issue_key}) has been in 'In Progress' for over 48 hours without recent code commits.\n"
                        f"Please provide a quick status update."
                    )
                    self.jira_service.add_comment(issue_key, comment_body)
                    report_lines.append(f"- **{issue_key}**: **No recent code activity**. AutoPilot added a comment.")
                    
                    self.message_broker.publish(
                        "DeveloperAssistantAgent", 
                        f"NO_CODE_ACTIVITY: Issue {issue_key} ({summary}) has no recent code activity. Status: In Progress."
                    )
                    continue 

                # 2. LLM Analysis
                print(f"\nAnalyzing ticket: {issue_key} - {summary}")

                comments = self.jira_service.get_comments_for_issue(issue_key)
                if not comments:
                    print("  -> No comments found.")
                    report_lines.append(f"- {issue_key}: No comments found.")
                    continue

                comment_text = self._get_text_from_comment_body(comments[-1]['body'])
                
                # --- FINAL FIX: Ignore AutoPilot's own comments ---
                if "JIRA AutoPilot" in comment_text or "NO_CODE_ACTIVITY" in comment_text:
                    print("  -> Skipping analysis (Comment is from AutoPilot).")
                    report_lines.append(f"- {issue_key}: Skipped (Last comment was automated).")
                    continue
                # --------------------------------------------------

                if not comment_text.strip():
                    print("  -> Latest comment has no text content.")
                    continue
                
                print(f"  -> Latest Comment: \"{comment_text}\"")
                analysis = self.llm_service.analyze_comment(comment_text)
                print(f"  -> 🤖 LLM Analysis: {analysis}")
                report_lines.append(f"- **{issue_key}**: {summary}\n  - **LLM Analysis**: {analysis}")
                
                is_blocked = "blocked: yes" in analysis.lower()
                is_negative = "sentiment: negative" in analysis.lower()
                
                if is_blocked or is_negative:
                    message = f"BLOCKER_DETECTED: Issue {issue_key} ({summary}) has negative sentiment/blocker: {analysis}"
                    self.message_broker.publish("DeveloperAssistantAgent", message)
                    report_lines.append("  - 📢 **Published Blocked Message to Broker**")
                
        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
            
        return "\n".join(report_lines)