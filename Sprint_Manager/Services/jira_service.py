import requests

class JiraService:
    def __init__(self, auth, headers, domain):
        self.auth = auth
        self.headers = headers
        self.domain = domain

    def get_comments_for_issue(self, issue_key):
        """Fetches all comments for a specific Jira issue."""
        try:
            url = f"{self.domain}/rest/api/3/issue/{issue_key}/comment"
            response = requests.get(url, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            return response.json().get('comments', [])
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error fetching comments for {issue_key}: {err}")
            return []

    # --- NEW METHODS FIXED ---
    
    def update_issue(self, issue_key, updates):
        """Updates fields of a specific Jira issue."""
        try:
            url = f"{self.domain}/rest/api/3/issue/{issue_key}"
            response = requests.put(url, headers=self.headers, json={"fields": updates}, auth=self.auth)
            response.raise_for_status()
            print(f"  [JiraService] Successfully updated issue {issue_key}.")
            return True
        except requests.exceptions.HTTPError as err:
            print(f"  [JiraService] HTTP Error updating issue {issue_key}: {err.response.text}")
            return False

    def add_comment(self, issue_key, comment_body):
        """Adds a comment to a specific Jira issue."""
        try:
            url = f"{self.domain}/rest/api/3/issue/{issue_key}/comment"
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": comment_body}]
                        }
                    ]
                }
            }
            response = requests.post(url, headers=self.headers, json=comment_data, auth=self.auth)
            response.raise_for_status()
            print(f"  [JiraService] Successfully added comment to {issue_key}.")
            return True
        except requests.exceptions.HTTPError as err:
            print(f"  [JiraService] HTTP Error adding comment to {issue_key}: {err.response.text}")
            return False

    def assign_issue(self, issue_key, account_id):
        """Assigns a Jira issue to a specific user."""
        try:
            url = f"{self.domain}/rest/api/3/issue/{issue_key}/assignee"
            assignment_data = {"accountId": account_id} 
            response = requests.put(url, headers=self.headers, json=assignment_data, auth=self.auth)
            response.raise_for_status()
            print(f"  [JiraService] Successfully assigned {issue_key} to {account_id}.")
            return True
        except requests.exceptions.HTTPError as err:
            print(f"  [JiraService] HTTP Error assigning issue {issue_key}: {err.response.text}")
            return False