# Actionable items, decisions, and questions extractor

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Centralized OpenRouter LLM configuration and retry handler
from core.llm import get_llm, invoke_with_retry


def build_chain(system_prompt: str, temperature: float = 0.2):
    """
    Constructs an LCEL extraction chain using the centralized OpenRouter LLM.
    """
    llm = get_llm(temperature=temperature)
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{text}"),
            ]
        )
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    """
    Extracts actionable items, assignees, and deadlines from the transcript.
    """
    if not transcript or not transcript.strip():
        return "No action items found."

    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )

    return invoke_with_retry(chain, transcript)


def extract_key_decisions(transcript: str) -> str:
    """
    Extracts key decisions agreed upon during the meeting.
    """
    if not transcript or not transcript.strip():
        return "No key decisions found."

    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    return invoke_with_retry(chain, transcript)


def extract_questions(transcript: str) -> str:
    """
    Extracts unresolved questions or topics requiring follow-up.
    """
    if not transcript or not transcript.strip():
        return "No open questions found."

    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    return invoke_with_retry(chain, transcript)