from urllib.parse import parse_qs, urlparse

import typer
from langchain.callbacks import get_openai_callback
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import NoTranscriptFound, YouTubeTranscriptApi

app = typer.Typer()


class InvalidURLException(Exception):
    pass


def get_videoid_from_url(url: str) -> str:
    """
    Gets video ID from give YouTube video URL

    :param url: YouTube video URL in 2 formats (standard and short)
    :return: id of YouTube video
    :raises InvalidURLException: If URL is not valid
    """
    url_data = urlparse(url)
    query = parse_qs(url_data.query)

    if ("v" in query) & ("youtube.com" in url_data.netloc):
        video_id = query["v"][0]
    elif "youtu.be" in url_data.netloc:
        path_lst = url.split("/")

        if path_lst:
            video_id = path_lst[-1]
        else:
            raise InvalidURLException("Invalid URL")
    else:
        raise InvalidURLException("Invalid URL")

    return video_id


def get_transcripts(url: str) -> str:
    video_id = get_videoid_from_url(url)

    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except NoTranscriptFound:
        transcript = transcript_list.find_generated_transcript(["en"])

    subtitles = transcript.fetch()

    subtitles = "\n".join(
        [sbt["text"] for sbt in subtitles if sbt["text"] != "[Music]"]
    )

    return subtitles


def generate_summary(subtitles: list) -> str:
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=4096, chunk_overlap=200
    )
    docs = text_splitter.create_documents([subtitles])

    chain = load_summarize_chain(llm, chain_type="map_reduce")
    result = chain(docs)
    return result["output_text"]


@app.command()
def main(url: str):
    subtitles = get_transcripts(url)

    with get_openai_callback() as cb:
        summary = generate_summary(subtitles)

    print()
    print("Summary:")
    print(summary)

    print()
    print("OpenAI Stats:")
    print(cb)
