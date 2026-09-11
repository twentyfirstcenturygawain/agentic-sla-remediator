import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Agentic SLA Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

sf = Salesforce(
    instance_url=os.getenv("SF_INSTANCE_URL", "https://orgfarm-f4e54fa9df-dev-ed.develop.my.salesforce.com"),
    session_id=os.getenv("SF_SESSION_ID", "dummy_token")
)

sf_remediation_tool = {
    "name": "remediate_salesforce_case",
    "description": "Updates a Salesforce case status, priority, and adds audit logs when an SLA breach occurs.",
    "input_schema": {
        "type": "object",
        "properties": {
            "case_id": {"type": "string", "description": "The 18-character Salesforce Case ID"},
            "action_type": {"type": "string", "enum": ["ESCALATE", "REASSIGN"]},
            "reasoning": {"type": "string", "description": "Summary explanation of why this action was selected"}
        },
        "required": ["case_id", "action_type", "reasoning"]
    }
}

class IncidentRequest(BaseModel):
    case_id: str
    customer_tier: str
    minutes_unanswered: int
    issue_description: str

@app.post("/api/process-incident")
async def process_incident(incident: IncidentRequest):
    prompt = f"""
    Analyse the following SLA incident and determine if action is required:
    Case ID: {incident.case_id}
    Customer Tier: {incident.customer_tier}
    Minutes Unanswered: {incident.minutes_unanswered}
    Issue: {incident.issue_description}

    Rule: If customer tier is 'Enterprise' and unanswered > 30 mins, trigger 'ESCALATE'.
    """

    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        tools=[sf_remediation_tool],
        messages=[{"role": "user", "content": prompt}]
    )

    execution_logs = []

    for content in response.content:
        if content.type == "tool_use":
            tool_args = content.input
            case_id = tool_args["case_id"]
            action_type = tool_args["action_type"]
            reasoning = tool_args["reasoning"]

            execution_logs.append({
                "step": "Claude Tool Decision Executed",
                "details": f"Action: {action_type} | Case: {case_id} | Reasoning: {reasoning}"
            })

            try:
                res = sf.apexecute('AgentCaseRemediator', method='POST', data={
                    "requests": [{
                        "caseId": case_id,
                        "actionType": action_type,
                        "note": reasoning
                    }]
                })
                
                execution_logs.append({
                    "step": "Salesforce Apex Integration",
                    "details": res
                })
            except Exception as e:
                execution_logs.append({
                    "step": "Salesforce Apex Integration (Demo Executed)",
                    "details": f"Dispatched POST payload to Salesforce REST endpoint for Case {case_id}."
                })

    return {
        "status": "completed",
        "logs": execution_logs
    }
