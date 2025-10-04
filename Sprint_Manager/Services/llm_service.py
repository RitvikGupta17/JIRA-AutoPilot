import os
import google.generativeai as genai

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        # --- FIX: Changed the model name to a stable version ---
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    def analyze_comment(self, comment_text):
        """Analyzes a developer's comment for sentiment and blockers."""
        prompt = f"""
        Analyze the following developer comment from a Jira ticket.
        Determine the sentiment (Positive, Neutral, Negative) and if the user is blocked.
        Provide your response as a simple one-line summary.

        Comment: "{comment_text}"

        Analysis:
        """
        try:
            response = self.model.generate_content(prompt)
            # Make sure to access the text part of the response correctly
            return response.text.strip()
        except Exception as e:
            return f"Error analyzing comment: {e}"