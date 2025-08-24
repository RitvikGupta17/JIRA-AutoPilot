import requests
from .base_agent import BaseAgent
# Import the new services
from ..Services.jira_service import JiraService
from ..Services.llm_service import LLMService

class DeveloperAssistantAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token):
        # Call the parent class's __init__
        super().__init__(jira_domain, jira_email, api_token)
        # Initialize the services
        self.jira_service = JiraService(self.auth, self.headers, self.jira_domain)
        self.llm_service = LLMService()

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
                
                # Get the latest comment
                latest_comment = comments[-1]['body']
                print(f"  -> Latest Comment: \"{latest_comment[:75]}...\"")

                # Reason about the comment using the LLM service
                analysis = self.llm_service.analyze_comment(latest_comment)
                print(f"  -> LLM Analysis: {analysis}")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")