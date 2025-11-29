📘 Project Overview — Conference Management Agent

The Conference Management Agent is an intelligent, goal-driven system designed to automate and streamline the entire lifecycle of conference and event planning. Organizing conferences typically requires coordinating venues, catering, entertainment, schedules, budgets, and communication across multiple tools and stakeholders. This creates friction, increases costs, and leaves room for human error.

This project solves that problem by introducing an autonomous agent that can reason, plan, and execute tasks end-to-end—dramatically reducing manual workload while improving accuracy and efficiency.

🎯 Problem

Event management is complex and fragmented. Planners often juggle:

Venue research and coordination

Catering and vendor management

Budget tracking and approvals

guest list updates

Email campaigns, announcements, and social posts

Scheduling and A/V arrangements

Doing all of this manually is slow, error-prone, and costly.

🤖 Why Agents?

Agents excel at dynamic, multi-step workflows. Using Google ADK principles, this agent is:

Adaptive — updates plans when budgets, schedules, or vendor availability changes

Goal-driven — focuses on outcomes (e.g., “organize a tech talk within budget”)

Integrated — connects across tools like email, calendars, vendor lists, and communication channels

Scalable — one agent can manage multiple events simultaneously

Agents automate the thinking, not just the doing—making them ideal for complex event coordination.

🏗️ Architecture at a Glance

The system is built around modular components:

Core Reasoning Engine
Breaks high-level goals into actionable steps, runs planning loops, and makes decisions autonomously.

Specialised Task Modules

Venue Coordination

Catering & Vendor Management

Budgeting & Cost Tracking

Entertainment & Scheduling

Communication (Email + LinkedIn)

Each module works together under a centralized agent that ensures the event is planned cohesively and efficiently.

🎬 Demo Summary

A real usage flow:

User defines an event (Tech Talk, 25 people, 50,000 INR budget).
→ Agent generates plan + vendor suggestions.

User adds a guest.
→ Agent updates the guest list.

User requests an announcement email.
→ Agent drafts it.

User wants a LinkedIn announcement.
→ Agent generates a polished social post.

🛠️ Technologies Used

Python 3.10+

Google ADK (Agent Development Kit)

Gemini + OpenAI Models

Custom tools for venue selection, budgeting, catering, and communication

🚀 Installation & Usage

Clone Repository
git clone https://github.com/rcseshwar/AI-Agents-Intensive.git

Install Dependencies
pip install -r requirements.txt

Set API Key
rename .env.example to .env
enter your API Key

Run Demo
python agent.py

