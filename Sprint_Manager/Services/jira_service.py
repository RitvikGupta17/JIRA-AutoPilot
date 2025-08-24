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