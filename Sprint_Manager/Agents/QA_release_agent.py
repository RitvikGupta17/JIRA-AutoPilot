# Sprint_Manager/Agents/QA_release_agent.py
import requests
import os
from datetime import datetime
from .base_agent import BaseAgent
from ..Services.llm_service import LLMService # <-- NEW IMPORT

class QAReleaseAgent(BaseAgent):
    def __init__(self, jira_domain, jira_email, api_token):
        super().__init__(jira_domain, jira_email, api_token)
        self.llm_service = LLMService() # <-- Initialize LLM

    def _generate_release_notes(self, done_issues):
        """Uses LLM to write professional release notes from completed tickets."""
        if not done_issues:
            return "No completed issues to document."

        print(f"  [QA] Generating Release Notes for {len(done_issues)} items...")
        
        # Prepare data for LLM
        issue_summaries = [f"- {i['key']}: {i['fields']['summary']}" for i in done_issues]
        issue_text = "\n".join(issue_summaries)
        
        prompt = f"""
        You are a Technical Writer for a software team. 
        Take the following list of completed JIRA tickets and write a clean, professional Release Note in Markdown format.
        
        Categorize the items into:
        - 🚀 New Features
        - 🐛 Bug Fixes
        - 🔧 Improvements
        
        Ignore internal tasks if they don't look user-facing.
        Add a catchy title with today's date ({datetime.now().strftime('%Y-%m-%d')}).

        Tickets:
        {issue_text}

        Output only the Markdown content.
        """
        
        try:
            notes_content = self.llm_service.model.generate_content(prompt).text
            
            # Save to file
            filename = "RELEASE_NOTES.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(notes_content)
                
            print(f"  [QA] ✅ Successfully wrote {filename}")
            return f"✅ **RELEASE_NOTES.md** generated with {len(done_issues)} items."
        except Exception as e:
            print(f"  [QA] Error generating notes: {e}")
            return f"❌ Failed to generate release notes: {e}"

    def execute(self):
        """Monitors 'In Review' tickets and Generates Release Notes for 'Done' tickets."""
        print("\n--- 📦 QA & Release Agent (Automated Engineer) ---")
        report_lines = []

        # 1. Existing Logic: Check "In Review" (The bottleneck check)
        print("Perceiving tickets in QA/Review...")
        search_url = f"{self.jira_domain}/rest/api/3/search/jql"
        
        # We perform two searches: one for Review (Monitoring), one for Done (Documentation)
        jql_review = 'status = "In Review"'
        jql_done = 'status = "Done" AND updated >= -7d' # Done in the last week
        
        try:
            # A. Check "In Review"
            response = requests.post(search_url, headers=self.headers, json={"jql": jql_review, "fields": ["key", "summary"]}, auth=self.auth)
            response.raise_for_status()
            review_issues = response.json().get('issues', [])
            
            if review_issues:
                report_lines.append(f"**⚠️ QA Bottleneck Alert**: {len(review_issues)} tickets waiting in review:")
                for issue in review_issues:
                    report_lines.append(f"- {issue['key']}: {issue['fields']['summary']}")
            else:
                report_lines.append("✅ No tickets currently stalled in Review.")

            # B. Generate Release Notes (The New Feature)
            response_done = requests.post(search_url, headers=self.headers, json={"jql": jql_done, "fields": ["key", "summary"]}, auth=self.auth)
            done_issues = response_done.json().get('issues', [])
            
            if done_issues:
                # Trigger the autonomous writing process
                result_msg = self._generate_release_notes(done_issues)
                report_lines.append(f"\n{result_msg}")
            else:
                report_lines.append("No recently completed items for Release Notes.")

        except Exception as e:
            print(f"An error occurred: {e}")
            report_lines.append(f"An unexpected error occurred: {e}")
        
        return "\n".join(report_lines)