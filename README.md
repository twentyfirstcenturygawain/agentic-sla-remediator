# Agentic SLA Incident Remediator

An event-driven autonomous orchestration engine built with FastAPI, Anthropic Claude 3.5 Sonnet, and Salesforce REST APIs. The system processes incoming customer service incidents, evaluates SLA thresholds using Claude's tool-calling capabilities, and executes programmatic remediation actions inside Salesforce without human intervention.

## Architectural Flow

1. **Incident Event Trigger**: FastAPI accepts incident metadata (`case_id`, `customer_tier`, `minutes_unanswered`, `issue_description`).
2. **Autonomous Evaluation**: Claude 3.5 Sonnet analyzes the incident against configured SLA policies.
3. **Structured Tool Call**: If remediation is warranted, Claude outputs a typed function invocation (`remediate_salesforce_case`).
4. **CRM Action Execution**: The backend executes custom actions in Salesforce via API to reassign, escalate, or append audit notes.

## Tech Stack

* **Backend Framework**: Python 3.9+, FastAPI, Uvicorn
* **AI Orchestration**: Anthropic API (`claude-3-5-sonnet-20241022`)
* **CRM Integration**: Salesforce REST API
* **Data Validation**: Pydantic v2

## Project Structure

agentic-sla-remediator/
├── agent.py          # Core FastAPI app, Claude tool-calling schema, and logic
├── index.html        # Frontend monitoring dashboard interface
├── requirements.txt  # Python dependencies
└── .env.example      # Template for required environment variables

## Quick Start & Local Development

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/twentyfirstcenturygawain/agentic-sla-remediator.git](https://github.com/twentyfirstcenturygawain/agentic-sla-remediator.git)
   cd agentic-sla-remediator
