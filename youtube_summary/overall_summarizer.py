from typing import List
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document

from youtube_summary.section_summarizer import SectionSummary


class OverallSummarizer:
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

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    def summarize(
        self, video_title: str, section_summaries: List[SectionSummary]
    ) -> str:
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        serialized_section_summaries = "\n".join([s.text for s in section_summaries])
        document = Document(page_content=serialized_section_summaries)
        prompt = OverallSummarizer.SUMMARY_PROMPT_TEMPLATE.partial(
            video_title=video_title
        )
        chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
        result = chain([document])
        return result["text"]
