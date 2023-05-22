# YouTube Transcript Summarizer

This project extracts and summarizes transcripts from YouTube videos using OpenAI GPT-3.5-turbo language model. I made it since I couldn't find any simple CLI app for this.

## Installation

### Install from PyPi
You can install the application using `pip` or `pipx`:
```bash
pip install --user youtube-summary
```
or
```bash
pipx install youtube-summary
```

### Compile from source

You can compile directly from source:
```bash
git clone https://github.com/mmaorc/youtube-summary-cli
cd youtube-summary-cli
python setup.py install --user
```


### Development
For development purposes, clone the repository, navigate to the project directory, and install in a virtual environment:

```bash
git clone https://github.com/mmaorc/youtube-summary-cli
cd youtube-summary-cli
python -m venv .env
source .env/bin/activate  # On Windows use `.env\Scripts\activate`
pip install --editable .
```


## Usage

Prior to running the script, ensure that the `OPENAI_API_KEY` environment variable is set up correctly.

To summarize the transcript of a YouTube video, run the `app.py` script with the video URL as an argument:

```bash
youtube-summary "https://www.youtube.com/watch?v=your_video_id"
```

Replace `your_video_id` with the actual video ID.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.