import requests
from .base_agent import BaseAgent

class QAReleaseAgent(BaseAgent):
    def perceive_tickets_for_review(self):
        """Monitors all tickets that are in the 'In Review' status."""
        print("\n--- QA & Release Agent ---")
        print("Perceiving tickets ready for review...")

        # JQL to find tickets in the "In Review" status
        jql_query = 'status = "In Review"'
        search_url = f"{self.jira_domain}/rest/api/3/search"
        params = {'jql': jql_query}

        try:
            response = requests.get(search_url, headers=self.headers, auth=self.auth, params=params)
            response.raise_for_status()
            review_issues = response.json().get('issues', [])
            
            if review_issues:
                print(f"Found {len(review_issues)} tickets in review.")
                for issue in review_issues:
                    print(f"- {issue['key']}: {issue['fields']['summary']}")
            else:
                print("No tickets are currently in review.")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def execute(self):
        """The main execution loop for this agent."""
        self.perceive_tickets_for_review()