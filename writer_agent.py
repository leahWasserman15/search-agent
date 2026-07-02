from pydantic import BaseModel, Field
from agents import Agent
from dotenv import load_dotenv
import os

load_dotenv(override=True)
MODEL_NAME = "gpt-5.4"
task = (
    "Help a company with a warehouse at 440 9th Ave, New York, NY anticipate weather, events, "
    "and other disruptions over the next week that may impact inbound and outbound shipping operations."
)

INSTRUCTIONS  = f"""
You are a senior logistics analyst tasked with writing a cohesive report for this research query:
"{task}"

The company operates a warehouse at 440 9th Ave in Manhattan (Hell's Kitchen / West Midtown),
near the Lincoln Tunnel, West Side Highway, and Penn Station corridor. You will be provided
with the original query and summarized web research. Using that research, generate a concise
report that helps the company anticipate disruptions to inbound and outbound shipping.

Organize findings by category (e.g. weather, transit disruptions, labor strikes, protests,
road/bridge closures, port or airport issues, and major public events). For each item identified,
include its expected timing, severity, and specific implications for truck access, loading docks,
and delivery routes serving 440 9th Ave (e.g. delivery delays, route closures, curb restrictions,
capacity constraints). Only include items with a real, specific impact — omit categories with
nothing relevant found.

Conclude with a short section highlighting the highest-priority risks the warehouse should
plan around this week, with practical recommendations for dispatch and scheduling.

Return structured output with:
- short_summary: a 2-3 sentence executive summary of the key findings
- markdown_report: the full report in markdown, ONE PAGE MAX (roughly 400-600 words) —
  prioritize the highest-impact items and use tight bullet points rather than long prose
- follow_up_questions: suggested topics to research further if gaps remain in the research
"""

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


writer_agent = Agent(name="Writer Agent", instructions=INSTRUCTIONS, model=MODEL_NAME, output_type=ReportData)
