import requests
from .base_agent import BaseAgent

class ScrumMasterAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token, sprint_id):
        super().__init__(jira_domain, jira_email, api_token)
        self.sprint_id = sprint_id

    def perceive_sprint_health(self):
        """Monitors all tickets in the active sprint."""
        print("\n--- Scrum Master Agent ---")
        print(f"Perceiving health of Sprint ID: {self.sprint_id}...")

        # This is the Agile API endpoint, different from the standard search
        sprint_url = f"{self.jira_domain}/rest/agile/1.0/sprint/{self.sprint_id}/issue"

        try:
            response = requests.get(sprint_url, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            sprint_issues = response.json().get('issues', [])
            print(f"Found {len(sprint_issues)} total issues in the sprint.")

            for issue in sprint_issues:
                status = issue['fields']['status']['name']
                print(f"- {issue['key']}: {issue['fields']['summary']} (Status: {status})")

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def execute(self):
        """The main execution loop for this agent."""
        self.perceive_sprint_health()