import re
from collections import namedtuple
from typing import List

import typer
import yt_dlp
from langchain import LLMChain, PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rich.console import Console
from rich.panel import Panel
from typer.rich_utils import (
    ALIGN_ERRORS_PANEL,
    ERRORS_PANEL_TITLE,
    STYLE_ERRORS_PANEL_BORDER,
)
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

# Define named tuple
SectionSummary = namedtuple("SectionSummary", ["timestamp_seconds", "text"])

VideoInfo = namedtuple("VideoInfo", ["id", "title"])

app = typer.Typer()

SECTION_TITLES_PROMPT = """Your mission is to summarize a video using its title and english subtitles.
The format of the subtitles will be `[timestamp in seconds]: [subtitle]`.
For each sentence in the summary, you should provide a timestamp to the original video section that this sentence is based on.
For example, a summary of a video section that starts at second 31 will be: `[31]: summary`.

The title of the video is: {video_title}
The subtitles are given between the triple backticks:
```
{text}
```

Your summary:
"""
SECTION_TITLES_PROMPT_TEMPLATE = PromptTemplate(
    template=SECTION_TITLES_PROMPT, input_variables=["text", "video_title"]
)

SUMMARY_PROMPT = """Your mission is to write a conscise summary of a video using its title and chapter summaries.
The format of the chapter summaries will be `[chapter timestamp in seconds]: chapter summary`.
For example, a summary of a chapter that starts at second 31 will be: `[31]: summary`.

The title of the video is: {video_title}
The chapter summaries are given between the triple backticks:
```
{text}
```

Your concise video summary:"""
SUMMARY_PROMPT_TEMPLATE = PromptTemplate(
    template=SUMMARY_PROMPT, input_variables=["text", "video_title"]
)


class InvalidURLException(Exception):
    pass


def extract_video_information(url: str) -> VideoInfo:
    ydl_opts = {"quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get("title")
        id = info_dict.get("id")
        return VideoInfo(id=id, title=title)


def get_transcripts(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled as e:
        raise Exception("Transcripts are disabled for this video") from e

    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except NoTranscriptFound:
        transcript = transcript_list.find_generated_transcript(["en"])

    subtitles = transcript.fetch()

    subtitles = "\n".join(
        [
            f"{sbt['start']}: {sbt['text']}"
            for sbt in subtitles
            if sbt["text"] != "[Music]"
        ]
    )

    return subtitles


def generate_section_summaries(video_title: str, subtitles: str) -> str:
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=1024, chunk_overlap=100
    )
    docs = text_splitter.create_documents([subtitles])

    prompt = SECTION_TITLES_PROMPT_TEMPLATE.partial(video_title=video_title)
    map_chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    reduce_chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    combine_document_chain = StuffDocumentsChain(
        llm_chain=reduce_chain,
        document_variable_name="text",
        verbose=False,
    )
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        combine_document_chain=combine_document_chain,
        document_variable_name="text",
        verbose=False,
    )
    result = map_reduce_chain(docs)
    return result["output_text"]


def generate_summary(video_title: str, section_titles: str) -> str:
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    document = Document(page_content=section_titles)
    prompt = SUMMARY_PROMPT_TEMPLATE.partial(video_title=video_title)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    result = chain([document])
    return result["text"]


def parse_section_summaries_text(text: str) -> List[SectionSummary]:
    # Split text into lines
    lines = text.split("\n")

    parsed_lines = []

    # Parse each line
    for line in lines:
        match = re.match(r"\s*\[(\d+(?:\.\d+)?)\]:\s+(.*)", line)
        if match:
            timestamp_seconds, text = match.groups()
            parsed_line = SectionSummary(
                timestamp_seconds=int(float(timestamp_seconds)), text=text
            )
            parsed_lines.append(parsed_line)

    return parsed_lines


def pretty_timestamp(timestamp_seconds: int) -> str:
    hours, remainder = divmod(timestamp_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"


def get_pretty_section_summary_text(url: str, section_summaries: str) -> str:
    parsed_section_summaries = parse_section_summaries_text(section_summaries)
    pretty_summaries = []
    for section_summary in parsed_section_summaries:
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
    console = Console(highlight=False)
    err_console = Console(stderr=True)

    try:
        video_information = extract_video_information(url)

        subtitles = get_transcripts(video_information.id)

        with get_openai_callback() as cb:
            section_summaries = generate_section_summaries(
                video_information.title, subtitles
            )
            summary = generate_summary(video_information.title, section_summaries)

        console.print()
        console.print(f"[bold]Video Title:[/bold] {video_information.title}")

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
