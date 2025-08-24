import os
from dotenv import load_dotenv
from Sprint_Manager.Agents.developer_assistant_agent import DeveloperAssistantAgent

# Load environment variables from the .env file
load_dotenv()

if __name__ == "__main__":
    print("Starting JIRA AutoPilot...")

    # Securely load credentials from environment variables
    JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    API_TOKEN = os.getenv("API_TOKEN")

    # Check if all required variables are loaded
    if not all([JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN]):
        raise ValueError("One or more required environment variables are not set.")

    # Initialize the agent
    dev_agent = DeveloperAssistantAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN)

    # Run the agent's main task
    dev_agent.execute()

    print("JIRA-AutoPilot run complete.")