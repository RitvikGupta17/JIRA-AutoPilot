import os
import requests
from dotenv import load_dotenv

# Load your existing .env file
load_dotenv()

# --- Your Details ---
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("API_TOKEN")
BOARD_ID = 35  # From your URL

# --- API Request ---
url = f"{JIRA_DOMAIN}/rest/agile/1.0/board/{BOARD_ID}/sprint"
auth = (JIRA_EMAIL, API_TOKEN)
headers = {"Accept": "application/json"}
params = {"state": "active"} # We only want the active sprint

try:
    response = requests.get(url, headers=headers, auth=auth, params=params)
    response.raise_for_status()
    
    sprints = response.json().get('values', [])
    
    if sprints:
        active_sprint = sprints[0]
        sprint_id = active_sprint['id']
        sprint_name = active_sprint['name']
        
        print("\n--- Found Active Sprint! ---")
        print(f"   Name: {sprint_name}")
        print(f"   ID: {sprint_id}")
        print("\nUse this ID in your main.py file.")
    else:
        print("No active sprint was found for Board ID 35.")
        print("Please ensure you have started the sprint from the backlog view.")

except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}")