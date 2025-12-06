# ✈️ JIRA AutoPilot

> **Stop managing Jira. Let Jira manage itself.**

**JIRA AutoPilot** is an industry-grade, multi-agent system that transforms your static Jira board into a living, breathing project team. It doesn't just *read* tickets—it **understands, assigns, monitors, and closes** them.

Powered by **Google Gemini 2.0 Flash** and a custom **Event-Driven Architecture**, this system acts as a Triage Specialist, a Scrum Master, a QA Engineer, and a Developer Guide—all running autonomously 24/7.

-----

## 🧠 The Autonomous Agents

The system is composed of four specialized agents that communicate via a central **Message Broker**.

### 1\. 🚦 The Triage Agent (The Gatekeeper)

  * **Role:** Autonomous Intake & Assignment.
  * **Capabilities:**
      * Scans the backlog for unassigned work.
      * **LLM Analysis:** Reads the ticket to understand if it's a "Frontend Bug" or a "Backend Feature."
      * **Smart Assignment:** Queries the Knowledge Base to find the best developer based on skill set (e.g., "React Expert") and current workload.
      * **Action:** Auto-assigns the ticket and updates priority/labels in Jira.

### 2\. 👨‍💻 The Developer Assistant (The Wingman)

  * **Role:** Proactive Support & Code Monitoring.
  * **Capabilities:**
      * **Git Integration (Simulated):** Monitors active tickets (`In Progress`) for code commits.
      * **Nudge Theory:** If a ticket is active for 48h with no code, it autonomously comments: *"No code activity detected. Are you stuck?"*
      * **Blocker Detection:** Analyzes developer comments using NLP. If a dev says *"I'm stuck on the API,"* it flags the ticket as **BLOCKED** and alerts the Scrum Master.

### 3\. 🕵️ The Scrum Master (The Strategist)

  * **Role:** Risk Management & Escalation.
  * **Capabilities:**
      * **Velocity Prediction:** Compares current burn-down rate vs. historical team velocity to predict sprint failure risks.
      * **Scope Creep Police:** Detects tickets added *after* the sprint started and flags them.
      * **Workload Balancing:** Identifies overworked team members and suggests reassignments.
      * **Escalation:** Receives "BLOCKER" signals from other agents and autonomously escalates high-priority issues.

### 4\. 📦 The QA & Release Agent (The Closer)

  * **Role:** Quality Control & Documentation.
  * **Capabilities:**
      * **Bottleneck Detection:** Warns if too many tickets are piling up in "In Review."
      * **Auto-Documentation:** Reads all "Done" tickets and uses Generative AI to write a professional **`RELEASE_NOTES.md`** file, categorized by Features and Bug Fixes.

-----

## 🛠️ Technology Stack

  * **Core:** Python 3.9+
  * **Intelligence:** Google Gemini 2.0 Flash (via `google-generativeai`)
  * **Integration:** Jira REST API v3
  * **Database:** SQLite (Knowledge Base & Sprint History)
  * **Communication:** In-Memory Message Broker (Publisher/Subscriber Pattern)
  * **Reporting:** Markdown-to-HTML Email Engine

-----

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.8+** installed.
2.  A **Jira Cloud** account.
3.  A **Google Gemini API Key** (Free tier works).

### 1\. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/jira-autopilot.git
cd jira-autopilot

# Install dependencies
pip install -r requirements.txt
```

### 2\. Configuration (`.env`)

Create a `.env` file in the root directory:

```ini
# Jira Configuration
JIRA_DOMAIN="https://your-domain.atlassian.net"
JIRA_EMAIL="your-email@example.com"
API_TOKEN="your-atlassian-api-token"
BOARD_ID="123"  # Check your Jira URL: .../boards/123

# AI Configuration
GEMINI_API_KEY="your-google-gemini-key"

# Email Reporting (Optional)
SENDER_EMAIL="bot@gmail.com"
SENDER_PASSWORD="your-app-password"
RECIPIENT_EMAIL="manager@company.com"
```

### 3\. Knowledge Base Setup

Open `Sprint_Manager/knowledge_base.py` and update line \~40 with your **Real Jira Account ID** (found in your Jira Profile URL).

```python
MY_JIRA_ID = "557058:be45a9..." # <--- CRITICAL: Paste your real ID here
```

### 4\. Jira Project Setup

Ensure your Jira Board uses these **exact** column statuses (Case Sensitive):

| Column | Status Name |
| :--- | :--- |
| Backlog | `To Do` |
| In Dev | `In Progress` |
| QA | `In Review` |
| Done | `Done` |

-----

## ▶️ How to Run

1.  **Start your Sprint** in Jira (Backlog -\> "Start Sprint").
2.  Run the AutoPilot:

<!-- end list -->

```bash
python3 main.py
```

### What happens next?

1.  **Console:** You will see agents waking up, scanning tickets, and making decisions.
2.  **Jira:** You will see tickets moving, assignees changing, and comments appearing from "Jira AutoPilot."
3.  **Files:** A `RELEASE_NOTES.md` file will appear in your folder.
4.  **Email:** A beautifully formatted HTML report will arrive in your inbox.

-----

## 🔮 Project Structure

```text
jira-autopilot/
├── main.py                     # The Orchestrator (Entry Point)
├── .env                        # Secrets
├── requirements.txt            # Dependencies
├── data/
│   └── sprint_data.db          # The Brain (History & Profiles)
└── Sprint_Manager/
    ├── knowledge_base.py       # Database Interface
    ├── message_broker.py       # Inter-Agent Communication
    ├── Services/
    │   ├── git_service.py      # Simulated Code Monitor
    │   ├── jira_service.py     # Jira API Wrapper
    │   ├── llm_service.py      # Gemini AI Interface
    │   └── notification_service.py # HTML Email Engine
    └── Agents/
        ├── triage_agent.py             # The Gatekeeper
        ├── developer_assistant_agent.py # The Wingman
        ├── scrum_master_agent.py       # The Strategist
        └── QA_release_agent.py         # The Closer
```

-----

\<p align="center"\>
Generated with ❤️ by \<strong\>JIRA AutoPilot\</strong\>
\</p\>