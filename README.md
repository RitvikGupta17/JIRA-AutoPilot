# JIRA AutoPilot ✈️

JIRA AutoPilot is an autonomous, multi-agent system designed to streamline agile project management within Jira. It uses intelligent agents to monitor sprint health, analyze developer tasks, and manage the QA/release pipeline, automating routine check-ins and providing insightful analytics.

---

## ✨ Features

* **Scrum Master Agent**: Monitors the overall health of the active sprint, tracking the status of all tickets.
* **Developer Assistant Agent**: Scans tickets assigned to the current user, analyzes comments using a Large Language Model (LLM) to detect blockers or negative sentiment.
* **QA & Release Agent**: Identifies tickets that are in the "In Review" status, preparing them for the next stage of the pipeline.
* **Message Broker**: A central communication channel allowing agents to publish their findings and subscribe to messages from other agents.
* **Knowledge Base**: A persistent database to store historical data about sprints, team velocity, and more.

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

* Python 3.8+
* A Jira Cloud instance with API access
* A Google Gemini API Key

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd jira-autopilot
    ```

2.  **Create and activate a virtual environment:**
    * On macOS/Linux:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    * On Windows:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure your environment variables:**
    * Create a file named `.env` in the root directory of the project.
    * Copy the contents of `.env.example` into it and fill in your credentials.

    **`.env` file contents:**
    ```
    JIRA_DOMAIN="[https://your-domain.atlassian.net](https://your-domain.atlassian.net)"
    JIRA_EMAIL="your-jira-email@example.com"
    API_TOKEN="your-jira-api-token"
    GEMINI_API_KEY="your-google-gemini-api-key"
    BOARD_ID="your-jira-board-id"
    SENDER_EMAIL="your-email@gmail.com"
    SENDER_PASSWORD="xxxx" # The 16-character password from Google
    RECIPIENT_EMAIL="scrum-master-email@example.com"
    ```
    *To find your `BOARD_ID`, go to your Jira board. The URL will look something like `.../boards/35`. The number at the end is your Board ID.*

### How to Run

Execute the main script to start the agents:
```sh
python main.py
```

#### **Step 1.2: Create a `.env.example` file**
This file serves as a template for the required environment variables. It's a best practice that helps new users understand what credentials they need to provide.

**Action:** Create a new file named `.env.example` in the root of your project.

**File: `ritvikgupta17/jira-autopilot/.env.example`**