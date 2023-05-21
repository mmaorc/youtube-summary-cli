# YouTube Transcript Summarizer

This project extracts and summarizes transcripts from YouTube videos using OpenAI GPT-3.5-turbo language model. I made it since I couldn't find any simple CLI app for this.

## Installation

Before using the project, make sure to install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Prior to running the script, ensure that the `OPENAI_API_KEY` environment variable is set up correctly.

To summarize the transcript of a YouTube video, run the `app.py` script with the video URL as an argument:

```bash
python app.py "https://www.youtube.com/watch?v=your_video_id"
```

Replace `your_video_id` with the actual video ID.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.