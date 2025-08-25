import requests
from .base_agent import BaseAgent
from ..Services.jira_service import JiraService
from ..Services.llm_service import LLMService

class DeveloperAssistantAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token):
        super().__init__(jira_domain, jira_email, api_token)
        self.jira_service = JiraService(self.auth, self.headers, self.jira_domain)
        self.llm_service = LLMService()

    def _get_text_from_comment_body(self, body):
        """
        Extracts plain text from Jira's Atlassian Document Format (ADF).
        This is a simplified parser for basic text comments.
        """
        try:
            # Navigate through the nested structure to find the text
            return body['content'][0]['content'][0]['text']
        except (KeyError, IndexError):
            # Fallback for unexpected formats or empty comments
            return ""

    def execute(self):
        """The main execution loop for this agent."""
        print("\n--- Developer Assistant Agent ---")
        print("Perceiving assigned tasks...")
        
        search_url = f"{self.jira_domain}/rest/api/3/search"
        jql_query = 'assignee = currentUser() AND status != "Done"'
        params = {'jql': jql_query}

        try:
            response = requests.get(search_url, headers=self.headers, params=params, auth=self.auth)
            response.raise_for_status()
            issues = response.json().get('issues', [])
            print(f"Found {len(issues)} assigned issues.")

            for issue in issues:
                issue_key = issue['key']
                print(f"\nAnalyzing ticket: {issue_key} - {issue['fields']['summary']}")
                
                comments = self.jira_service.get_comments_for_issue(issue_key)
                if not comments:
                    print("  -> No comments found.")
                    continue
                
                # Get the body of the latest comment
                latest_comment_body = comments[-1]['body']
                # *** FIX: Use the helper function to extract plain text ***
                comment_text = self._get_text_from_comment_body(latest_comment_body)
                
                if not comment_text:
                    print("  -> Latest comment has no text content.")
                    continue

                print(f"  -> Latest Comment: \"{comment_text[:75]}...\"")

                # Reason about the comment using the LLM service
                analysis = self.llm_service.analyze_comment(comment_text)
                print(f"  -> LLM Analysis: {analysis}")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def publish_summary(self, broker):
        """Publishes a summary of its findings to the message broker."""
        summary_message = "Developer task perception complete. All assigned tickets have been analyzed."
        broker.publish(self.__class__.__name__, summary_message)