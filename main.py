# main.py
import os
import requests
from dotenv import load_dotenv
from Sprint_Manager.Agents.developer_assistant_agent import DeveloperAssistantAgent
from Sprint_Manager.Agents.scrum_master_agent import ScrumMasterAgent
from Sprint_Manager.Agents.QA_release_agent import QAReleaseAgent
from Sprint_Manager.knowledge_base import KnowledgeBase
from Sprint_Manager.Services.notification_service import NotificationService

load_dotenv()

def get_active_sprint_id(domain, email, token, board_id):
    print("🔎 Attempting to find the active sprint...")
    url = f"{domain}/rest/agile/1.0/board/{board_id}/sprint"
    auth = (email, token)
    headers = {"Accept": "application/json"}
    params = {"state": "active"}
    try:
        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        sprints = response.json().get('values', [])
        if sprints:
            active_sprint = sprints[0]
            print(f"✅ Found active sprint: '{active_sprint['name']}' (ID: {active_sprint['id']})")
            return active_sprint['id']
        else:
            print("❌ No active sprint was found for the specified board.")
            return None
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error while finding sprint ID: {err}")
        return None

if __name__ == "__main__":
    print("\n--- 🚀 Starting JIRA AutoPilot ---")

    JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, BOARD_ID = (os.getenv(k) for k in ["JIRA_DOMAIN", "JIRA_EMAIL", "API_TOKEN", "BOARD_ID"])
    if not all([JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, BOARD_ID]):
        raise ValueError("One or more required Jira environment variables are not set.")

    SPRINT_ID = get_active_sprint_id(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, BOARD_ID)
    if not SPRINT_ID:
        print("\n--- 🛑 JIRA AutoPilot run halted ---"); exit()

    print("\n--- 🛠️ Initializing Components ---")
    kb = KnowledgeBase()
    
    print("\n--- 🤖 Initializing Agents ---")
    dev_agent = DeveloperAssistantAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN)
    scrum_master_agent = ScrumMasterAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, SPRINT_ID, kb)
    qa_agent = QAReleaseAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN)

    # --- Run Agent Execution & Compile Reports ---
    print("\n--- ▶️ Running Agent Execution ---")
    all_reports = {}
    all_reports['Developer Assistant Agent'] = dev_agent.execute()
    all_reports['Scrum Master Agent'] = scrum_master_agent.execute()
    all_reports['QA & Release Agent'] = qa_agent.execute()

    # --- Send Nightly Report ---
    print("\n--- 📧 Preparing Email Report ---")
    SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL = (os.getenv(k) for k in ["SENDER_EMAIL", "SENDER_PASSWORD", "RECIPIENT_EMAIL"])
    
    # Check if email variables are set before initializing
    if all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        notification_service = NotificationService(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL)
        notification_service.send_report(all_reports)
    else:
        print("Email credentials not fully configured in .env file. Skipping email report.")

    kb.close()
    print("\n--- ✅ JIRA AutoPilot run complete ---")