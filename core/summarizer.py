from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Import centralized OpenRouter configuration and retry mechanism
from core.llm import get_llm, invoke_with_retry


def split_transcript(transcript: str) -> list[str]:
    """
    Splits the transcript into chunks for Map-Reduce processing.
    """
    if not transcript or not transcript.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    """
    Summarizes a meeting transcript using Map-Reduce:
    1. Splits transcript into chunks.
    2. Generates individual summaries for each chunk (Map step).
    3. Combines partial summaries into one final bulleted summary (Reduce step).
    """
    if not transcript or not transcript.strip():
        raise ValueError("Cannot summarize an empty transcript.")

    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize this portion of a meeting transcript concisely."),
            ("human", "{text}"),
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)
    if not chunks:
        raise ValueError("Transcript produced no chunks to summarize.")

    chunk_summaries = []
    for chunk in chunks:
        summary_piece = invoke_with_retry(map_chain, {"text": chunk})
        chunk_summaries.append(summary_piece)

    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert meeting summarizer. Combine these partial summaries "
                "into one final professional meeting summary in bullet points.",
            ),
            ("human", "{text}"),
        ]
    )

    combined_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | combined_prompt
        | llm
        | StrOutputParser()
    )

    final_summary = invoke_with_retry(combined_chain, combined)
    return final_summary


def generate_title(transcript: str = None, transcipt: str = None, **kwargs) -> str:
    """
    Generates a short professional meeting title (max 8 words) from the transcript.
    Supports both 'transcript' and legacy 'transcipt' argument names.
    Optimizes LLM context by reading up to the first 2,000 characters.
    """
    raw_text = transcript if transcript is not None else transcipt
    if raw_text is None:
        raw_text = kwargs.get("transcript") or kwargs.get("transcipt")

    if not raw_text or not str(raw_text).strip():
        raise ValueError("Cannot generate title from an empty transcript.")

    llm = get_llm()

    title_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Based on the meeting transcript, generate a short professional meeting title "
                    "(max 8 words). Only return the title, nothing else.",
                ),
                ("human", "{text}"),
            ]
        )
        | llm
        | StrOutputParser()
    )

    # Use first 2000 characters to avoid unnecessary duplicate tokens
    title = invoke_with_retry(title_chain, str(raw_text)[:2000])
    return title.strip().strip('"').strip("'")