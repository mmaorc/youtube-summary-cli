from typing import List
import typer
from langchain.callbacks import get_openai_callback
from rich.console import Console
from rich.panel import Panel
from typer.rich_utils import (
    ALIGN_ERRORS_PANEL,
    ERRORS_PANEL_TITLE,
    STYLE_ERRORS_PANEL_BORDER,
)
from youtube_summary.overall_summarizer import OverallSummarizer
from youtube_summary.section_summarizer import SectionSummarizer, SectionSummary
from youtube_summary.transcript import get_transcripts

from youtube_summary.video_infromation import extract_video_information

app = typer.Typer()


def pretty_timestamp(timestamp_seconds: int) -> str:
    hours, remainder = divmod(timestamp_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"


def get_pretty_section_summary_text(
    url: str, section_summaries: List[SectionSummary]
) -> str:
    pretty_summaries = []
    for section_summary in section_summaries:
        timestamp_seconds = section_summary.timestamp_seconds
        link = f"{url}&t={timestamp_seconds}"
        timestamp_pretty = pretty_timestamp(timestamp_seconds)
        summary = f"[link={link}]{timestamp_pretty}[/link]: {section_summary.text}"
        pretty_summaries.append(summary)
    return "\n".join(pretty_summaries)


def pretty_print_exception_message(console: Console, e: Exception) -> None:
    console.print(
        Panel(
            f"An error occurred: {e}",
            border_style=STYLE_ERRORS_PANEL_BORDER,
            title=ERRORS_PANEL_TITLE,
            title_align=ALIGN_ERRORS_PANEL,
            highlight=False,
        )
    )


@app.command()
def main(url: str, debug_mode: bool = False):
    """
    A simple CLI tool that summarizes YouTube videos.

    If you encounter a bug, please open an issue at: https://github.com/mmaorc/youtube-summary-cli.

    If you have any questions, you can find me on Twitter: https://bit.ly/43ow5WT.
    """
    console = Console(highlight=False)
    err_console = Console(stderr=True)

    try:
        section_summarizer = SectionSummarizer()
        overall_summarizer = OverallSummarizer()

        video_information = extract_video_information(url)

        subtitles = get_transcripts(video_information.id)

        with get_openai_callback() as cb:
            section_summaries = section_summarizer.summarize(
                video_information.title, subtitles
            )
            summary = overall_summarizer.summarize(
                video_information.title, section_summaries
            )

        console.print()
        console.print(
            f"[bold]Title:[/bold] [link={video_information.url}]"
            f"{video_information.title}[/link]"
        )
        video_duration = pretty_timestamp(video_information.duration)
        console.print(f"[bold]Duration:[/bold] {video_duration}")
        console.print(
            f"[bold]Channel:[/bold] [link={video_information.channel_url}]"
            f"{video_information.channel}[/link]"
        )

        console.print()
        console.print("[bold]Summary:[/bold]")
        console.print(summary)

        console.print()
        console.print("[bold]Chapter Summaries:[/bold]")
        console.print(get_pretty_section_summary_text(url, section_summaries))

        console.print()
        console.print("[bold]OpenAI Stats:[/bold]")
        console.print(cb)
    except Exception as e:
        if debug_mode:
            raise e
        pretty_print_exception_message(err_console, e)
        raise typer.Exit(1)
