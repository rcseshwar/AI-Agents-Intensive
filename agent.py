
#####################################################################
###########     Enterprise Conference Management Agent    ###########
#####################################################################

import os
import json
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner

from google.adk.tools import google_search, ToolContext
from google.adk.tools.agent_tool import AgentTool

from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.agents.llm_agent import Agent

from google.adk.models.lite_llm import LiteLlm

from google.genai.types import Content, Part

from prompts import REQUEST_MEETUP_QUERY, ADD_GUEST_QUERY, Announcement_QUERY, EMAIL_QUERY, LINKEDIN_QUERY

session_service = InMemorySessionService()
load_dotenv()


openAIModel = LiteLlm(model=os.environ.get("OPENAI_MODEL"))
googleGenAIModel = os.environ.get("GOOGLE_GENAI_MODEL")

app_name = "EnterpriseConferenceManagementAgent"
user_id = "ECMA_ALPHA_USER"




######################
#     Data Stores     
######################

# GUEST_DATABASE[email] = name
GUEST_DATABASE = {}

GUEST_DATABASE['john.doe@email.com'] = 'John Doe'
GUEST_DATABASE['kai.trump@email.com'] = 'Kai Trump'


####################
#     Functions
####################

# Updat Session State
def update_session_state(
    tool_context: ToolContext, event_type: str, city: str, budget: int
) -> str:
  """Saves the extracted event parameters to the session state."""
  tool_context.state['event_type'] = event_type
  tool_context.state['city'] = city
  tool_context.state['budget'] = budget
  return "Session state has been updated with event parameters."

COMPLETION_PHRASE = "The plan is within the budget."

# Exit Loop
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the plan is approved and within budget."""
  print("  [Tool Call] Budget approved. Terminating loop.")
  tool_context.actions.escalate = True
  return "Budget approved. Finalizing plan."

# Sum Costs
def sum_costs(costs: list[float]) -> float:
  """Calculates the sum of a list of numbers."""
  return sum(costs)

# Add Guest
def add_guest(name: str, email: str) -> str:
  """Adds a guest's name and email to the event's guest list."""
  print(f"  [Tool Call] Adding guest '{name}' with email '{email}'.")
  GUEST_DATABASE[email] = name
  return f"Successfully added {name} to the guest list."

#Get Guest List
def get_guest_list(tool_context: ToolContext) -> str:
  """Retrieves the current list of all registered guests for the event."""
  print("  [Tool Call] Retrieving guest list.")
  if not GUEST_DATABASE:
    return "The guest list is currently empty."
  tool_context.state["guest_list"] = GUEST_DATABASE
  return json.dumps(GUEST_DATABASE)

# Email Draft
class EmailDraft(BaseModel):
  """A model to hold the components of a draft email."""
  subject: str = Field(description="The compelling subject line for the email.")
  body: str = Field(description="The full, well-formatted body of the email.")

# Send Email
def send_email(tool_context: ToolContext) -> str:
    """
    Simulates sending an email. It retrieves the structured EmailDraft object
    from the session state and formats a email.
    """
    print("  [Tool Call] Preparing to send emails...")

    guest_list = GUEST_DATABASE
    # Retrieve the structured EmailDraft object directly from the state
    email_draft = tool_context.state.get("email_draft")
    # print(f"[Tool call...] {email_draft}")
    # print(f"Type: {type(email_draft)}")

    if not guest_list:
        return "There are no guests on the list to email."

    print("\n--- SIMULATING EMAIL SEND ---")
    for email, name in guest_list.items():
        print(f"To: {name} <{email}>")
        print(f"Subject: {email_draft['subject']}")
        print("\nBody:\n" + email_draft["body"])
        print("-----------------------------")

    return f"Successfully prepared simulated emails for {len(guest_list)} guests."



###################
#     Wrappers
###################

# Google Search Agent
google_search_agent = Agent(
    name="Google_Search_Agent",
    model=googleGenAIModel,
    instruction="You are just a wrapper for the Google Search tool.",
    tools=[google_search]

)

# Google Search Tool
google_search_tool = AgentTool(agent=google_search_agent)




#################
#     Agents
#################

# LinkedIn Research
linkedin_research = Agent(
    name="linkedin_research",
    model=openAIModel,
    
    instruction="""
    You are a research assistant. You will be given a topic `{{current_plan}}` and you will research on it. Then you will provide a summary of the research.
    """,
    output_key="linkedinresearch_summary"
)

# LinkedIn Agent
linkedin_agent = Agent(
    model=openAIModel,
    name="linkedin_agent",
    description="An agent that generates LinkedIn posts",
    instruction="""
    You are a LinkedIn post generator. You will be given a topic with researched summary from "linkedinresearch_summary" output, and you will generate a LinkedIn post about it.
        The post should be professional, engaging, and relevant to the topic.
        The post should have a primary hook, not more than 60 characters.
        The post should have a line break after the hook.
        The post should have a post-hook that is either supporting the hook or completely inverse of the hook to grab attention.

        The post should be in a conversational tone and should be easy to read.
        There should be bullet points in the post to make it easy to read.
        There should be actionable items in the post to make it easy to follow.

        At the end of the post, there should be a question to engage the audience.
        Finally, ask the audience to share their thoughts in the comments. And to repost.
        Use emojis to make the post more engaging.
        Use hashtags to make the post more discoverable.
    """,
    output_key="linkedIn_post",
)

# Intake Agent
intake_agent = Agent(
    name="intake_agent",
    model=openAIModel,
    instruction="""
    From the user's query, identify the event type (e.g., 'Tech Talk on AI'), the city, and the budget. 
    Then, you MUST call the `update_session_state` tool.
    """,
    tools=[update_session_state]
)

# Venu Searching Agent
venue_search_agent = Agent(
    name="venue_search_agent",
    model=googleGenAIModel,
    
    instruction="""
    You are a venue scout. Find 3 potential venues for a {{event_type}} in {{city}}. For each venue, find an estimated rental cost.
    Output ONLY a JSON object with your findings, like this: {"venues": [{"name": "Venue A", "estimated_cost": 5000}]}
    """,
    tools=[google_search],
    output_key="venue_options"
)

# Catering Searching Agent
catering_search_agent = Agent(
    name="catering_search_agent",
    model=googleGenAIModel,
    
    instruction="""
    You are a catering scout. Find 3 catering companies suitable for a {{event_type}} in {{city}}. For each caterer, find an estimated cost.
    Output ONLY a JSON object with your findings, like this: {"caterers": [{"name": "Caterer A", "estimated_cost": 4000}]}
    """,
    tools=[google_search],
    output_key="catering_options"
)

# Entertainment Searching Agent
entertainment_search_agent = Agent(
    name="entertainment_search_agent",
    model=googleGenAIModel,
    
    instruction="""
    You are an entertainment scout. Find 3 entertainment options for a {{event_type}} in {{city}}. For each option, find an estimated booking fee.
    Output ONLY a JSON object with your findings, like this: {"entertainment": [{"name": "DJ A", "estimated_cost": 1500}]}
    """,
    tools=[google_search],
    output_key="entertainment_options"
)

# Initial Plan Synthesizer Agent
initial_plan_synthesizer_agent = Agent(
    name="initial_plan_synthesizer_agent",
    model=openAIModel,
    
    instruction="""
    You are an initial plan synthesizer. Combine the findings from {{venue_options}}, {{catering_options}}, and {{entertainment_options}} into a single JSON object.
    The final JSON must have the keys "venues", "caterers", and "entertainment". Output ONLY the JSON object.
    Example: {"venues": [...], "caterers": [...], "entertainment": [...]}
    """,
    output_key="current_plan"
)

# Account Agent
accountant_agent = Agent(
    name="accountant_agent",
    model=openAIModel,
    
    tools=[sum_costs],
    instruction=f"""
    You are a meticulous accountant. Your budget is {{budget}}. The current list of options is in {{current_plan}}.

    Your task is to create the most cost-effective plan and evaluate it:
    1. From the lists of 'venues', 'caterers', and 'entertainment', select ONLY the single cheapest option from each category.
    2. Create a "cheapest_plan" consisting of just these three items.
    3. Use the `sum_costs` tool on this "cheapest_plan".

    - IF the total cost > {{budget}}, your output MUST be a JSON object with a 'critique' and the 'cheapest_plan' you created.
    - ELSE, your output MUST be a JSON object where the 'critique' is '{COMPLETION_PHRASE}' and you include the 'cheapest_plan'.

    Example Output if over budget:
    ```json
    {{
        "critique": "Even with the cheapest options, this plan is over budget. Find a cheaper venue.",
        "cheapest_plan": {{
            "venue": {{"name": "Affordable Hall", "estimated_cost": 3200}},
            "caterer": {{"name": "Good Eats Catering", "estimated_cost": 4000}},
            "entertainment": {{"name": "Local DJ", "estimated_cost": 1000}}
        }}
    }}
    ```
    """,
    output_key="evaluation"
)

# Cost Cutting Agent
cost_cutter_agent = Agent(
    name="cost_cutter_agent",
    model=googleGenAIModel,
    
    tools=[google_search_tool, exit_loop],
    instruction=f"""
    You are a cost-cutting expert. You have received an evaluation in the {{evaluation}} variable.

    Your task:
    1. Check the 'critique' field in the {{evaluation}}.
    2. IF the critique is '{COMPLETION_PHRASE}', you MUST call the `exit_loop` tool.
    3. ELSE, the plan is over budget. The plan to modify is in the 'cheapest_plan' field of {{evaluation}}.
    4. Read the 'critique' to identify which item to replace.
    5. Use your search tool to find a single, cheaper alternative for that one item.
    6. Output a new, complete JSON plan with this one change, keeping the other items the same.
    """,
    output_key="current_plan"
)

# Final Report
final_report = Agent(
    name="final_report",
    model=openAIModel,
    
    instruction="""
    You are an expert project assistant compiling a final event plan for a client.
    Your tone should be professional, clear, and confident.

    You have access to the following information:
    - `{{current_plan}}`: The final, budget-approved plan with one vendor for each category.
    - `{{venue_options}}`, `{{catering_options}}`, `{{entertainment_options}}`: The original lists of all vendors that were scouted.
    - `{{budget}}`: The client's initial budget.

    Your task is to generate a comprehensive markdown report that follows this exact structure:

    1.  **Executive Summary:** Start with a brief paragraph confirming the event details (e.g., event type, city) and state that a cost-effective plan has been found within the budget of ${{budget}}.
    2.  **Approved Plan & Cost:** Create a section that clearly lists the single, approved vendor for the Venue, Catering, and Entertainment from `{{current_plan}}`, along with their individual costs. Calculate and display the total final cost.
    3.  **Alternative Vendor Options:** Create a section that lists the *other* vendors that were considered from `{{venue_options}}`, `{{catering_options}}`, and `{{entertainment_options}}`. This gives the client extra options for their reference.
    4.  **Next Steps:** Conclude the report with a brief, professional statement about next steps (e.g., "The next steps would be to contact these vendors to finalize bookings.").

    Your entire output must be only the markdown report. Do not add any other conversational text.
    """,
)

# Guest List
guest_list = Agent(
    name="guest_list",
    model=openAIModel,
    
    instruction="You are a guest management assistant. Use the `add_guest` and `get_guest_list` tools.",
    tools=[add_guest, get_guest_list]
)

# Communications 
communications_agent = Agent(
    name="communications_agent",
    model=openAIModel,
    
    instruction="""
    You are a communications expert. Take the event plan from {{current_plan}}.

    Your task is to draft a professional announcement email and format it as a JSON object.
    The JSON object must have two keys: "subject" and "body".

    **CRITICAL: Your entire output must be ONLY the raw JSON object. It must start with `{` and end with `}`. Do not include ```json or any other text, introductions, or formatting.**

    Example of required output format:
    {
      "subject": "📢 Announcing Our Exclusive Tech Talk on AI!",
      "body": "Dear AI Enthusiast,\\n\\nGet ready to connect, learn, and innovate!..."
    }
    """,
    output_key="email_draft",
    output_schema=EmailDraft
)




###################
#     Loop Agent
###################

# Budget Refinement
budget_refinement = LoopAgent(
    name="budget_refinement",
    sub_agents=[accountant_agent, cost_cutter_agent],
    max_iterations=3
)




#############################
#####     Parallel Agent    
#############################

# Parallel Logistics Search
parallel_logistics_search = ParallelAgent(
    name="parallel_logistics_search",
    sub_agents=[venue_search_agent, catering_search_agent, entertainment_search_agent]
)




################################
#####     Sequential Agent    
################################

# Initial Planning
initial_planning = SequentialAgent(
    name="initial_planning",
    sub_agents=[parallel_logistics_search, initial_plan_synthesizer_agent]
)

# Budget Optimizer
budget_optimizer = SequentialAgent(
    name="budget_optimizer",
    sub_agents=[budget_refinement]
)

# Planning
planning_workflow = SequentialAgent(
    name="planning_workflow",
    sub_agents=[
        intake_agent,
        initial_planning,
        budget_optimizer,
        final_report
    ]
)

# Wrapper
planning_workflow_tool = AgentTool(agent=planning_workflow)
guest_list_tool = AgentTool(agent=guest_list)
communications_tool = AgentTool(agent=communications_agent)
linkedin_tool = AgentTool(agent=linkedin_agent)

# Base Agent
base_agent = Agent(
    model=openAIModel,
    name='base_agent',

    instruction="""
    You are the master event planning assistant. Delegate tasks to the correct tool.
    - For high-level planning requests (budgeting, finding vendors), use `planning_workflow_tool`.
    - For simple guest management (add, view), use `guest_list_tool`.
    - To draft an announcement email, linkedIn use `communications_tool`.
    - To send the final email use `send_email`.
    - To send linkedIn Post use `linkedin_tool`.

    - **IMPORTANT**: When the `communications_tool` is used, its output will be a JSON object with a 'subject' and a 'body'. You MUST format this into a clean, human-readable email draft for the user. Do not just show the raw JSON.
    """,
    tools=[
        planning_workflow_tool,
        guest_list_tool,
        communications_tool,
        send_email,
        linkedin_tool
    ]
)

# Process Request
async def process_request(agent: Agent, query: str, session: session, user_id: str):
    """Initializes a runner and executes a query for a given agent and session."""
    print(f"\n🚀 Running query for agent: '{agent.name}' in session: '{session.id}'...")
    runner = Runner(agent=base_agent, app_name=app_name, session_service=session_service)
    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user")
        ):
            if event.is_final_response():
                final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occurred: {e}"

    print("\n" + "#"*75 + "\n")
    print("✅ Response:")
    ## display(Markdown(final_response))
    print(" " + final_response + "\n")
    print("#"*75 + "\n")
    return final_response

# Enterprise CMA
async def enterprise_cma():
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id

    )

    print(f"\n🗣️ User: {REQUEST_MEETUP_QUERY}")
    await process_request(base_agent, REQUEST_MEETUP_QUERY, session, user_id)

    print(f"🗣️ User: {ADD_GUEST_QUERY}")
    await process_request(base_agent, ADD_GUEST_QUERY, session, user_id)

    print(f"🗣️ User: {Announcement_QUERY}")
    await process_request(base_agent, Announcement_QUERY, session, user_id)

    print(f"🗣️ User: {EMAIL_QUERY}")
    await process_request(base_agent, EMAIL_QUERY, session, user_id)

    print(f"🗣️ User: {LINKEDIN_QUERY}")
    await process_request(base_agent, LINKEDIN_QUERY, session, user_id)

if __name__ == "__main__":
    asyncio.run(enterprise_cma())
