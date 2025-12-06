# Sprint_Manager/Services/git_service.py
from datetime import datetime, timedelta
import random

class GitService:
    def __init__(self, jira_domain=None, api_key=None):
        """
        A simulated Git Service (e.g., GitHub/GitLab).
        In a real application, this would use a platform's API to check commits.
        """
        print("Git Service (Simulated) initialized.")

    def check_recent_activity(self, issue_key, lookback_days=2):
        """
        Simulates checking for code commits or PR activity linked to an issue key.
        Returns True if activity is recent (within lookback_days), False otherwise.
        """
        # --- Simulation Logic ---
        # 50% chance of no activity to simulate "stalled" work
        if random.random() < 0.5:
            # Simulate a recent commit time
            recent_time = datetime.now() - timedelta(hours=random.randint(1, 23))
            print(f"  [Git] Found recent simulated activity for {issue_key} at {recent_time.strftime('%Y-%m-%d %H:%M')}.")
            return True
        else:
            # Simulate no activity for the lookback period
            no_activity_time = datetime.now() - timedelta(days=lookback_days + random.randint(1, 3))
            print(f"  [Git] No recent simulated activity found for {issue_key}. Last check: {no_activity_time.strftime('%Y-%m-%d %H:%M')}.")
            return False