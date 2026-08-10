"""
MiniBot — knows only about project management and making money.
Anything else is deferred to the owner to teach.
"""

import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MiniBot", description="Project management & money — nothing else.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Topic detection ──────────────────────────────────────────────────────────

PROJECT_MGMT_KEYWORDS = [
    "project", "task", "sprint", "backlog", "milestone", "timeline", "deadline",
    "roadmap", "kanban", "scrum", "agile", "planning", "team", "workflow",
    "priority", "blocker", "standup", "retro", "retrospective", "scope",
    "deliverable", "stakeholder", "resource", "gantt", "epic", "story",
    "estimate", "velocity", "capacity", "assign", "ticket", "issue", "board",
]

MONEY_KEYWORDS = [
    "money", "revenue", "income", "profit", "pricing", "invoice", "payment",
    "monetize", "monetization", "earn", "charge", "fee", "rate", "budget",
    "cost", "expense", "roi", "return", "investment", "cashflow", "cash flow",
    "salary", "quote", "contract", "upsell", "subscription", "mrr", "arr",
    "ltv", "cac", "margin", "gross", "net", "billing", "payout", "freelance",
    "client", "proposal", "retainer", "commission", "bonus", "raise",
]

SYSTEM_PROMPT = """You are MiniBot, a hyper-focused assistant.
You ONLY answer questions about:
1. Project management (planning, tasks, sprints, timelines, team workflows, agile, kanban, scrum, etc.)
2. Making money (revenue, pricing, invoicing, monetization strategies, budgeting, ROI, etc.)

If a question is outside these two topics, respond EXACTLY with:
"That's outside what I know right now — my owner will teach me that soon."

Be concise, practical, and direct. No fluff."""


def is_in_scope(text: str) -> bool:
    lower = text.lower()
    for kw in PROJECT_MGMT_KEYWORDS + MONEY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", lower):
            return True
    return False


OUT_OF_SCOPE_REPLY = (
    "That's outside what I know right now — my owner will teach me that soon."
)

# ── Hardcoded knowledge base (rule-based fallback) ───────────────────────────

KNOWLEDGE: dict[str, str] = {
    # Project Management
    "what is a sprint": "A sprint is a fixed time-box (usually 1–2 weeks) where a team commits to completing a set of tasks from the backlog.",
    "what is kanban": "Kanban is a visual workflow method where tasks move across columns (e.g., To Do → In Progress → Done) to track progress and limit work-in-progress.",
    "what is a backlog": "A backlog is a prioritized list of tasks, features, or bugs that need to be completed in a project.",
    "how do i prioritize tasks": "Use frameworks like MoSCoW (Must/Should/Could/Won't), Eisenhower Matrix (urgent vs important), or simply sort by business value vs effort.",
    "what is a standup": "A daily standup is a short team check-in (15 min max) where each person shares: what they did yesterday, what they're doing today, and any blockers.",
    "what is agile": "Agile is an iterative approach to project management that focuses on delivering value in small increments, adapting to change, and continuous improvement.",
    "what is a milestone": "A milestone is a key checkpoint or goal in a project timeline that marks significant progress or completion of a phase.",
    "how do i manage a remote team": "Use async communication tools (Slack, Notion), clear task assignments (Linear, Jira), regular syncs, and written documentation for everything.",
    # Making Money
    "how do i price my services": "Calculate your costs, research market rates, then add a margin. For freelancers: hourly rate = desired annual income ÷ 2000 billable hours.",
    "what is mrr": "MRR (Monthly Recurring Revenue) is the predictable revenue generated each month from subscriptions or retainers.",
    "how do i write an invoice": "Include: your name/business, client name, invoice number, date, itemized services, amounts, payment due date, and payment method.",
    "what is roi": "ROI (Return on Investment) = (Net Profit ÷ Cost of Investment) × 100. It measures the efficiency of an investment.",
    "how do i get clients": "Build a portfolio, leverage your network, ask for referrals, create content showing your expertise, and use LinkedIn or cold outreach.",
    "what is a retainer": "A retainer is a recurring fee a client pays to keep you available, often monthly, for ongoing work or consulting.",
    "how do i increase revenue": "Upsell existing clients, raise rates, add new service tiers, productize your service, or expand your client base.",
    "what is cashflow": "Cashflow is the movement of money in and out of your business. Positive cashflow means more money coming in than going out.",
    "what is ltv": "LTV (Lifetime Value) is the total revenue you expect from a customer over their entire relationship with your business.",
}


def rule_based_answer(text: str) -> str | None:
    lower = text.lower().strip().rstrip("?")
    for question, answer in KNOWLEDGE.items():
        if question in lower or lower in question:
            return answer
    return None


# ── LLM fallback (optional — set OPENAI_API_KEY env var) ────────────────────

def llm_answer(user_message: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=300,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


# ── API ───────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    in_scope: bool


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    msg = req.message.strip()
    if not msg:
        return ChatResponse(reply="Please send a message.", in_scope=True)

    if not is_in_scope(msg):
        return ChatResponse(reply=OUT_OF_SCOPE_REPLY, in_scope=False)

    # 1. Try rule-based answer
    answer = rule_based_answer(msg)
    if answer:
        return ChatResponse(reply=answer, in_scope=True)

    # 2. Try LLM if available
    answer = llm_answer(msg)
    if answer:
        return ChatResponse(reply=answer, in_scope=True)

    # 3. Honest fallback
    return ChatResponse(
        reply=(
            "I know this is about project management or money, but I don't have "
            "a specific answer yet. My owner will teach me more soon."
        ),
        in_scope=True,
    )


@app.get("/health")
def health():
    return {"status": "ok", "topics": ["project management", "making money"]}


@app.get("/")
def root():
    return {
        "name": "MiniBot",
        "version": "1.0.0",
        "knows_about": ["project management", "making money"],
        "usage": "POST /chat with JSON body: {\"message\": \"your question\"}",
    }
