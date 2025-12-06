# main.py
import os
import requests
from dotenv import load_dotenv

# --- Agent Imports ---
from Sprint_Manager.Agents.developer_assistant_agent import DeveloperAssistantAgent
from Sprint_Manager.Agents.scrum_master_agent import ScrumMasterAgent
from Sprint_Manager.Agents.QA_release_agent import QAReleaseAgent
from Sprint_Manager.Agents.triage_agent import TriageAgent # <-- NEW IMPORT

# --- Service & Infrastructure Imports ---
from Sprint_Manager.knowledge_base import KnowledgeBase
from Sprint_Manager.Services.notification_service import NotificationService
from Sprint_Manager.message_broker import MessageBroker

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
    print("\n========================================")
    print("   ✈️   JIRA AUTOPILOT - SYSTEM START   ")
    print("========================================\n")

    # 1. Environment Setup
    env_vars = ["JIRA_DOMAIN", "JIRA_EMAIL", "API_TOKEN", "BOARD_ID", "GEMINI_API_KEY"]
    if not all(os.getenv(k) for k in env_vars):
        print("❌ Error: Missing required environment variables. Check your .env file.")
        exit()

    JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    API_TOKEN = os.getenv("API_TOKEN")
    BOARD_ID = os.getenv("BOARD_ID")

    SPRINT_ID = get_active_sprint_id(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, BOARD_ID)
    if not SPRINT_ID:
        print("\n--- 🛑 JIRA AutoPilot run halted: No Active Sprint ---"); exit()

    # 2. Infrastructure Initialization
    print("\n--- 🛠️  Initializing Core Systems ---")
    kb = KnowledgeBase()      # Database for history & profiles
    broker = MessageBroker()  # Inter-agent communication
    
    # 3. Agent Initialization
    print("\n--- 🤖 Initializing Autonomous Agents ---")
    
    # The Triage Agent needs the KB to find the best developer
    triage_agent = TriageAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, kb)
    
    # The Developer Assistant needs the Broker to report blockers
    dev_agent = DeveloperAssistantAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, broker)
    
    # The Scrum Master needs the KB (history) and Broker (to receive alerts)
    scrum_master_agent = ScrumMasterAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN, SPRINT_ID, kb, broker)
    
    qa_agent = QAReleaseAgent(JIRA_DOMAIN, JIRA_EMAIL, API_TOKEN)

    # 4. Execution Loop
    print("\n--- ▶️  Executing Agent Workflows ---")
    all_reports = {}
    
    # Step A: Triage First (Assign new work so it can be monitored)
    all_reports['Triage Agent'] = triage_agent.execute()
    
    # Step B: Developer Assistant (Monitor work in progress & code activity)
    all_reports['Developer Assistant Agent'] = dev_agent.execute()
    
    # Step C: QA Agent (Check items ready for release)
    all_reports['QA & Release Agent'] = qa_agent.execute()
    
    # Step D: Scrum Master (Overall health & handling agent alerts)
    # This runs last to capture messages published by Dev Agent during Step B
    all_reports['Scrum Master Agent'] = scrum_master_agent.execute()

    # 5. Reporting
    print("\n--- 📧 Finalizing & Sending Report ---")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
    
    if all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        notification_service = NotificationService(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL)
        notification_service.send_report(all_reports)
    else:
        print("  [Info] Email credentials not configured. Skipping email report.")
        # Optional: Print report to console if email is skipped
        print("\n--- 📝 Console Report Dump ---")
        for agent, report in all_reports.items():
            print(f"\n[{agent}]\n{report}")

    kb.close()
    print("\n========================================")
    print("   ✅   JIRA AUTOPILOT - RUN COMPLETE   ")
    print("========================================")