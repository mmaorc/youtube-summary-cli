from dataclasses import dataclass
import yt_dlp


@dataclass(frozen=True)
class VideoInfo:
    id: str
    title: str
    url: str
    duration: int
    channel: str
    channel_url: str


def extract_video_information(url: str) -> VideoInfo:
    ydl_opts = {"quiet": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return VideoInfo(
            id=info_dict.get("id"),
            title=info_dict.get("title"),
            url=info_dict.get("webpage_url"),
            duration=info_dict.get("duration"),
            channel=info_dict.get("channel"),
            channel_url=info_dict.get("channel_url"),
        )
