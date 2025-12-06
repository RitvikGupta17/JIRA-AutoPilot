import os
import google.generativeai as genai

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash') # Updated model

    def analyze_comment(self, comment_text):
        """Analyzes a developer's comment for sentiment and blockers."""
        prompt = f"""
        Analyze the following developer comment from a Jira ticket.
        Determine the sentiment (Positive, Neutral, Negative) and if the user is blocked.
        
        Response Format: "Sentiment: [Value], Blocked: [Yes/No]"

        Comment: "{comment_text}"
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error analyzing comment: {e}"

    # --- NEW METHOD FIXED ---
    def analyze_triage(self, issue_summary, issue_description):
        """Analyzes a new ticket for type, severity, and required specialization."""
        prompt = f"""
        You are an expert JIRA Triage Agent. Analyze the following new ticket and provide a structured JSON response.

        Ticket Summary: "{issue_summary}"
        Ticket Description: "{issue_description}"

        Determine the following:
        1.  **Issue Type**: Must be one of: 'Bug', 'Story', 'Task'.
        2.  **Priority**: Must be one of: 'High', 'Medium', 'Low'.
        3.  **Specialization**: The required technical skill. Must be one of: 'Frontend', 'Backend', 'DevOps', 'FullStack'.

        Provide ONLY the JSON object in your response.

        Example Output:
        {{
            "issue_type": "Story",
            "priority": "High",
            "specialization": "Frontend"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            # Clean up potential markdown formatting from LLM
            if json_text.startswith("```json"):
                json_text = json_text.strip("```json").strip()
            if json_text.endswith("```"):
                json_text = json_text.rstrip("```").strip()
                
            return json_text
        except Exception as e:
            return f"Error analyzing triage: {e}"