import os
from dotenv import load_dotenv
from Sprint_Manager.Agents.developer_assistant_agent import DeveloperAssistantAgent
from Sprint_Manager.Agents.scrum_master_agent import ScrumMasterAgent
# Import the new QAReleaseAgent
from Sprint_Manager.Agents.QA_release_agent import QAReleaseAgent
from Sprint_Manager.message_broker import MessageBroker
from Sprint_Manager.knowledge_base import KnowledgeBase

load_dotenv()

if __name__ == "__main__":
    print("--- Starting JIRA AutoPilot ---")

    JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    API_TOKEN = os.getenv("API_TOKEN")
    SPRINT_ID = 35 # Your Sprint ID

    if not all([JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN]):
        raise ValueError("One or more required environment variables are not set.")

    # Initialize components
    broker = MessageBroker()
    kb = KnowledgeBase() 

    # Initialize ALL Agents
    dev_agent = DeveloperAssistantAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN)
    scrum_master_agent = ScrumMasterAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, SPRINT_ID)
    qa_agent = QAReleaseAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN) # <-- Initialize QA Agent

    # --- Run the agents' main tasks ---
    dev_agent.execute()
    scrum_master_agent.execute()
    qa_agent.execute() # <-- Run the new agent

    # --- Test the message broker ---
    dev_agent.publish_summary(broker)
    message = broker.subscribe()
    if message:
        print(f"\nMain loop received message from {message['sender']}: {message['content']}")

    kb.close()
    print("\n--- JIRA AutoPilot run complete ---")