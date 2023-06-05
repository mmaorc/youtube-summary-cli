# YouTube Summary CLI

A simple CLI tool that summarizes YouTube videos. This tool is designed to help users quickly understand the main points of a video without having to watch the entire content. It uses AI to generate a concise summary of the video's transcript.

![Screenshot](./docs/screenshot.png)

The timestamps are also clickable, try them 🙂

## Usage

### Installation

You can install the application using `pip` or `pipx`:
```bash
pip install --user youtube-summary
pipx install youtube-summary
```

You can also compile directly from source:
```bash
git clone https://github.com/mmaorc/youtube-summary-cli
cd youtube-summary-cli
python setup.py install --user
```

### Run

Prior to running the script, ensure that the `OPENAI_API_KEY` environment variable is set up correctly.

To summarize the transcript of a YouTube video, run the app with the video URL as an argument:

```bash
youtube-summary "https://www.youtube.com/watch?v=your_video_id"
```

Replace `your_video_id` with the actual video ID.

Note that generating a summary might take a couple of minutes, depending on the video's transcript length.


## Development
For development purposes, clone the repository, navigate to the project directory, and install in a virtual environment:

```bash
git clone https://github.com/mmaorc/youtube-summary-cli
cd youtube-summary-cli
python -m venv .env
source .env/bin/activate  # On Windows use `.env\Scripts\activate`
pip install --editable .
```

Ensure that the `OPENAI_API_KEY` environment variable is set up correctly.

Now you can run it:
```bash
python -m youtube_summary "https://www.youtube.com/watch?v=your_video_id"
```

Replace `your_video_id` with the actual video ID.


## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.


## Contact Me

You can find me on [Twitter](https://bit.ly/43ow5WT).