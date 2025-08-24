class BaseAgent:
    def __init__(self, jira_domain, jira_email, api_token):
        self.jira_domain = jira_domain
        self.jira_email = jira_email
        self.api_token = api_token
        self.auth = (self.jira_email, self.api_token)
        self.headers = {"Accept": "application/json"}
        print(f"{self.__class__.__name__} initialized.")

    def execute(self):
        """A placeholder for the agent's main loop."""
        raise NotImplementedError("Each agent must implement the execute method.")