from dataclasses import dataclass
import re
from typing import List
from langchain import LLMChain, PromptTemplate
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class SectionSummary:
    timestamp_seconds: int
    text: str


class SectionSummarizer:
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

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n"], chunk_size=1024, chunk_overlap=100
        )

    def summarize(self, video_title: str, subtitles: str) -> List[SectionSummary]:
        docs = self.text_splitter.create_documents([subtitles])

        prompt = SectionSummarizer.SECTION_TITLES_PROMPT_TEMPLATE.partial(
            video_title=video_title
        )
        map_chain = LLMChain(llm=self.llm, prompt=prompt, verbose=False)
        reduce_chain = LLMChain(llm=self.llm, prompt=prompt, verbose=False)
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

        llm_result = map_reduce_chain(docs)

        llm_output = llm_result["output_text"]

        return self._parse_section_summaries_text(llm_output)

    @staticmethod
    def _parse_section_summaries_text(text: str) -> List[SectionSummary]:
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
