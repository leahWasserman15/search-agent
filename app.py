from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
import asyncio
import nest_asyncio

nest_asyncio.apply()

query= (
    "Help a company with a warehouse at 440 9th Ave, New York, NY anticipate weather, events, "
    "and other disruptions over the next week that may impact inbound and outbound shipping operations."
)
class ResearchManager:

    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            yield f"Starting research. Trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            search_plan = await self.plan_searches(query)
            yield f"Searches planned, starting {len(search_plan.searches)} searches..."
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            self._last_report = await self.write_report(query, search_results)
            yield self._last_report.markdown_report

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        result = await Runner.run(planner_agent, f"Query: {query}")
        return result.final_output

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        tasks = [self.search(item) for item in search_plan.searches]
        return await asyncio.gather(*tasks)

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input_message = f"Search term: {item.query}\nReason for searching: {item.reason}"
        result = await Runner.run(search_agent, input_message)
        return result.final_output

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        input_message = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, input_message)
        return result.final_output

async def run(query: str):
    async for status_update in ResearchManager().run(query):
        yield status_update

import gradio as gr
import tempfile
import html
from pathlib import Path
from datetime import datetime
from styles import CSS, HEADER_HTML


def save_report_to_file(report: ReportData) -> str:
    file_path = Path(tempfile.gettempdir()) / f"logistics_report_{datetime.now():%Y%m%d_%H%M%S}.md"
    content = (
        f"# Logistics Disruption Report\n\n"
        f"## Executive Summary\n\n{report.short_summary}\n\n---\n\n{report.markdown_report}"
    )
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def format_progress(logs: list[str]) -> str:
    if not logs:
        return '<div class="dr-log"><span class="dr-log-muted">Ready to run.</span></div>'
    lines = "".join(
        f'<div class="dr-log-line">{html.escape(line)}</div>' for line in logs
    )
    return f'<div class="dr-log">{lines}</div>'


async def run_logi_agent():
    logs = []

    def log(msg: str) -> str:
        logs.append(msg)
        return format_progress(logs)

    hidden_download = gr.update(value=None, visible=False)
    disabled_btn = gr.update(interactive=False)
    enabled_btn = gr.update(interactive=True)

    yield log("Starting research..."), "", hidden_download, disabled_btn

    try:
        manager = ResearchManager()

        async for update in manager.run(query):
            if getattr(manager, "_last_report", None) and update is manager._last_report.markdown_report:
                continue
            yield log(update), "", hidden_download, disabled_btn

        report = manager._last_report
        report_md = f"**Executive Summary:** {report.short_summary}\n\n---\n\n{report.markdown_report}"
        file_path = save_report_to_file(report)

        yield (
            log("Report complete!"),
            report_md,
            gr.update(value=file_path, visible=True),
            enabled_btn,
        )
    except Exception as e:
        yield (
            log(f"Error: {e}"),
            "",
            hidden_download,
            enabled_btn,
        )


with gr.Blocks(title="Research Agent Hub", css=CSS) as demo:
    gr.HTML(HEADER_HTML)
    with gr.Row(elem_classes=["dr-action-row"]):
        run_btn = gr.Button("Run Logistics Agent", variant="primary", elem_id="dr-run")
        download_btn = gr.DownloadButton("Download Report", visible=False, elem_id="dr-download")
    gr.HTML('<div class="dr-progress-label">Progress</div>')
    status_output = gr.HTML(
        value=format_progress([]),
        elem_id="dr-progress",
        show_label=False,
    )
    report_output = gr.Markdown(label="Report", elem_id="dr-report", show_label=False)

    run_btn.click(
        fn=run_logi_agent,
        outputs=[status_output, report_output, download_btn, run_btn],
        show_progress="hidden",
    )

demo.queue().launch(inbrowser=True)