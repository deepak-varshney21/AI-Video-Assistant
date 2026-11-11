import sys
import os

# Ensure the project root is in the python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from core.llm import get_llm, invoke_with_retry, OPENROUTER_BASE_URL, DEFAULT_OPENROUTER_MODEL
from core.summarizer import summarize, generate_title, split_transcript
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from langchain_openai import ChatOpenAI

def test_centralized_llm():
    print("--- Test 1: Centralized OpenRouter LLM Configuration ---")
    llm = get_llm()
    assert isinstance(llm, ChatOpenAI), f"Expected ChatOpenAI, got {type(llm)}"
    assert str(llm.openai_api_base).rstrip("/") == "https://openrouter.ai/api/v1", f"Base URL mismatch: {llm.openai_api_base}"
    print(f"  [OK] Centralized LLM instantiated: {llm.model_name}")
    print(f"  [OK] Base URL: {llm.openai_api_base}")
    print("Test 1 Passed: Centralized OpenRouter configuration verified.\n")

def test_no_mistral_in_code():
    print("--- Test 2: Verify No Mistral Imports in Codebase ---")
    import core.llm
    import core.summarizer
    import core.extractor
    import core.rag_engine

    for mod in [core.llm, core.summarizer, core.extractor, core.rag_engine]:
        source = open(mod.__file__, "r", encoding="utf-8").read()
        assert "ChatMistralAI" not in source, f"Found ChatMistralAI in {mod.__file__}"
        assert "langchain_mistralai" not in source, f"Found langchain_mistralai in {mod.__file__}"
        assert "MISTRAL_API_KEY" not in source, f"Found MISTRAL_API_KEY in {mod.__file__}"
    print("  [OK] Zero references to ChatMistralAI, langchain_mistralai, or MISTRAL_API_KEY found in core modules.")
    print("Test 2 Passed: Codebase is 100% clean of Mistral.\n")

def test_title_generation():
    print("--- Test 3: Title Generation via OpenRouter ---")
    sample_transcript = """
    Alice: Welcome everyone to our Q4 Engineering Sync. Today we discuss the OpenRouter migration.
    Bob: I completed migrating all LLM modules from Mistral to OpenRouter.
    Charlie: Testing shows excellent reliability with exponential backoff on HTTP 429.
    Alice: Fantastic, let's ship this to production today.
    """
    title = generate_title(sample_transcript)
    print(f"  Generated Title: {title}")
    assert isinstance(title, str), f"Title must be a string, got {type(title)}"
    assert len(title.strip()) > 0, "Title must not be empty"
    print("Test 3 Passed: Title generation verified.\n")

def test_action_item_extraction():
    print("--- Test 4: Action Items, Decisions & Questions via OpenRouter ---")
    sample_meeting = """
    Manager: Okay team, here are the next steps for our sprint.
    Dev1: I will deploy the OpenRouter integration to staging by Wednesday 5 PM.
    Dev2: I will write comprehensive unit tests for rate-limiting retry logic by Friday.
    Manager: We decided to standardize on the nvidia/nemotron-3-ultra-550b-a55b:free model for all tasks.
    Dev1: Should we also add streaming response support in the next phase?
    Manager: Let's discuss that in our next architecture review.
    """
    action_items = extract_action_items(sample_meeting)
    print(f"  Action Items Output:\n{action_items}\n")
    assert isinstance(action_items, str) and len(action_items.strip()) > 0

    decisions = extract_key_decisions(sample_meeting)
    print(f"  Key Decisions Output:\n{decisions}\n")
    assert isinstance(decisions, str) and len(decisions.strip()) > 0

    questions = extract_questions(sample_meeting)
    print(f"  Open Questions Output:\n{questions}\n")
    assert isinstance(questions, str) and len(questions.strip()) > 0

    print("Test 4 Passed: Extractor module verified with OpenRouter.\n")

def test_multi_chunk_summarization():
    print("--- Test 5: Multi-chunk Map-Reduce Summarization via OpenRouter ---")
    p1 = """
    Project Phoenix Status Report - Part 1:
    The team has successfully replaced the previous Mistral AI implementation with OpenRouter.
    The new architecture centralizes all LLM instantiations into core/llm.py.
    This eliminates code duplication and ensures consistent retry behavior across all modules.
    Whisper handles local English transcription while Sarvam AI is used for Hinglish audio.
    """ * 4

    p2 = """
    Project Phoenix Status Report - Part 2:
    Rate limit handling has been hardened. When OpenRouter returns HTTP 429, the system applies
    exponential backoff up to 5 retries and respects Retry-After headers when provided.
    All RAG Q&A retrieval runs through the centralized OpenRouter client as well.
    Vector storage continues to use ChromaDB and all-MiniLM-L6-v2 sentence embeddings.
    """ * 4

    full_transcript = p1 + "\n\n" + p2
    chunks = split_transcript(full_transcript)
    print(f"  Transcript length: {len(full_transcript)} characters, split into {len(chunks)} chunks.")
    assert len(chunks) > 1, "Must produce multiple chunks for Map-Reduce test."

    summary = summarize(full_transcript)
    print(f"  Final Map-Reduce Summary:\n{summary}\n")
    assert isinstance(summary, str) and len(summary.strip()) > 0
    print("Test 5 Passed: Multi-chunk Map-Reduce summarization verified.\n")

def test_rag_engine():
    print("--- Test 6: RAG Engine Q&A via OpenRouter ---")
    meeting_transcript = """
    Project Phoenix Meeting:
    The official deployment date for the AI Video Assistant is November 15, 2026.
    The primary contact for emergency escalations is Sarah Jenkins at ext 4092.
    """
    rag_chain = build_rag_chain(meeting_transcript)
    answer = ask_question(rag_chain, "What is the official deployment date for Project Phoenix?")
    print(f"  RAG Answer: {answer}")
    assert isinstance(answer, str) and "November 15" in answer
    print("Test 6 Passed: RAG Engine with OpenRouter verified.\n")

def test_error_handling():
    print("--- Test 7: Error Handling & Empty Inputs ---")
    try:
        generate_title("")
        assert False, "Empty transcript should raise ValueError"
    except ValueError as e:
        print(f"  [OK] generate_title empty check: {e}")

    try:
        summarize("   ")
        assert False, "Whitespace transcript should raise ValueError"
    except ValueError as e:
        print(f"  [OK] summarize empty check: {e}")

    assert extract_action_items("") == "No action items found."
    assert extract_key_decisions("") == "No key decisions found."
    assert extract_questions("") == "No open questions found."
    print("Test 7 Passed: Error handling and edge cases verified.\n")

if __name__ == "__main__":
    print("==================================================")
    print("STARTING COMPLETE OPENROUTER MIGRATION TEST SUITE")
    print("==================================================\n")
    test_centralized_llm()
    test_no_mistral_in_code()
    test_title_generation()
    test_action_item_extraction()
    test_multi_chunk_summarization()
    test_rag_engine()
    test_error_handling()
    print("==================================================")
    print("ALL 7 TEST SUITES PASSED SUCCESSFULLY!")
    print("==================================================")
