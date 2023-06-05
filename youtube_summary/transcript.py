from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)


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
