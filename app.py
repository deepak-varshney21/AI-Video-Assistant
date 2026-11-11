import os
import re
import tempfile
import time
import uuid
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the existing backend pipeline from main.py
from main import run_pipeline


# ==============================================================================
# 1. PAGE CONFIGURATION & STRICT LIGHT SAAS THEME CSS
# ==============================================================================
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bulletproof Light Theme CSS
LIGHT_THEME_CSS = """
<style>
/* -------------------------------------------------------------
   1. Typography & Global Layout
------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #1F2937 !important;
}

/* Overall Canvas Background */
.stApp {
    background-color: #F8F9FC !important;
    color: #1F2937 !important;
}

/* Header Cleanup */
header[data-testid="stHeader"] {
    background-color: #F8F9FC !important;
}

/* Force All Headings to Dark Navy/Black */
h1, h2, h3, h4, h5, h6 {
    color: #111827 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Standard Paragraph & Markdown Text */
p, span, label, div {
    color: #1F2937;
}

.stMarkdown, .stMarkdown p {
    color: #1F2937 !important;
}

/* -------------------------------------------------------------
   2. Sidebar Light Theme & Navigation
------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
}

[data-testid="stSidebar"] * {
    color: #1F2937 !important;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4 {
    color: #111827 !important;
}

/* Sidebar Radio Navigation */
[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    background-color: #F8F9FC !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    padding: 6px !important;
    gap: 4px !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    background-color: transparent !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background-color: #F1F5F9 !important;
}

[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
[data-testid="stSidebar"] div[data-testid="stRadio"] label span {
    color: #1F2937 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

/* Sidebar Secondary Buttons (History items) */
[data-testid="stSidebar"] div.stButton > button {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-align: left !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #F5F3FF !important;
    border-color: #7C3AED !important;
    color: #7C3AED !important;
}

[data-testid="stSidebar"] div.stButton > button p {
    color: inherit !important;
}

/* -------------------------------------------------------------
   3. SaaS Card Containers
------------------------------------------------------------- */
.app-header {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 14px !important;
    padding: 24px 30px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
}

.saas-card {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 14px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
}

.card-title {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #111827 !important;
    margin-bottom: 16px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

/* Hero Title Card */
.hero-title-card {
    background: #FAF5FF !important;
    border: 1px solid #E9D5FF !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
}

.hero-title-text {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #581C87 !important;
    margin: 0 !important;
    line-height: 1.3 !important;
}

/* Badge */
.app-badge {
    background-color: #F5F3FF !important;
    color: #7C3AED !important;
    border: 1px solid #DDD6FE !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* -------------------------------------------------------------
   4. Input Fields & Dropdowns (Strict Light Theme)
------------------------------------------------------------- */
/* Text Input & BaseWeb wrappers */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.15) !important;
}

/* Raw input and textarea tags */
input, textarea {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    -webkit-text-fill-color: #1F2937 !important;
    font-size: 14px !important;
}

input::placeholder, textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}

/* Streamlit widget labels */
div[data-testid="stWidgetLabel"] label,
div[data-testid="stWidgetLabel"] p {
    color: #111827 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    margin-bottom: 4px !important;
}

div[data-testid="stWidgetLabel"] small {
    color: #64748B !important;
}

/* Selectbox */
div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    color: #1F2937 !important;
}

div[data-baseweb="select"] span {
    color: #1F2937 !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
}

li[data-baseweb="menu-item"] {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
}

li[data-baseweb="menu-item"]:hover,
li[data-baseweb="menu-item"][aria-selected="true"] {
    background-color: #F5F3FF !important;
    color: #7C3AED !important;
}

/* File Uploader Container */
div[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 1px dashed #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #7C3AED !important;
    background-color: #FAF5FF !important;
}

div[data-testid="stFileUploader"] section {
    background-color: #FFFFFF !important;
}

div[data-testid="stFileUploader"] * {
    color: #1F2937 !important;
}

div[data-testid="stFileUploader"] small {
    color: #64748B !important;
}

div[data-testid="stFileUploader"] button {
    background-color: #F8F9FC !important;
    color: #1F2937 !important;
    border: 1px solid #E5E7EB !important;
}

/* -------------------------------------------------------------
   5. Buttons (Primary Purple & Secondary Outline)
------------------------------------------------------------- */
/* Primary Action Button (Generate Summary) */
div.stButton > button:first-child {
    background-color: #7C3AED !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 1px 2px rgba(124, 58, 237, 0.2) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:first-child:hover {
    background-color: #6D28D9 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button:first-child p,
div.stButton > button:first-child span {
    color: #FFFFFF !important;
}

/* Download Buttons */
div.stDownloadButton > button:first-child {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

div.stDownloadButton > button:first-child:hover {
    background-color: #F5F3FF !important;
    border-color: #7C3AED !important;
    color: #7C3AED !important;
}

div.stDownloadButton > button:first-child p,
div.stDownloadButton > button:first-child span {
    color: #1F2937 !important;
}

div.stDownloadButton > button:first-child:hover p,
div.stDownloadButton > button:first-child:hover span {
    color: #7C3AED !important;
}

/* -------------------------------------------------------------
   6. Streamlit Tabs
------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 6px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #64748B !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 8px 20px !important;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #111827 !important;
    background-color: #F8F9FC !important;
}

.stTabs [aria-selected="true"] {
    background-color: #F5F3FF !important;
    color: #7C3AED !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {
    color: #7C3AED !important;
}

/* -------------------------------------------------------------
   7. Metrics, Status Widget & Expander
------------------------------------------------------------- */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span {
    color: #64748B !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] div {
    color: #111827 !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

/* Status Widget */
div[data-testid="stStatusWidget"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

div[data-testid="stStatusWidget"] * {
    color: #1F2937 !important;
}

/* Checkboxes */
div[data-testid="stCheckbox"] label span {
    color: #1F2937 !important;
    font-size: 14px !important;
}

/* Scrollable Transcript Container */
.transcript-container {
    max-height: 420px !important;
    overflow-y: auto !important;
    background-color: #F8F9FC !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    padding: 18px !important;
    font-family: inherit !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
    color: #1F2937 !important;
    white-space: pre-wrap !important;
}
</style>
"""
st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)


# ==============================================================================
# 2. HELPER FUNCTIONS & CLIPBOARD COMPONENT
# ==============================================================================
def render_clipboard_button(text_to_copy: str, button_label: str = "Copy to Clipboard", button_id: str = "btn-copy"):
    """
    Renders a styled interactive copy button using browser clipboard API with feedback.
    """
    escaped_text = (
        text_to_copy.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("$", "\\$")
        .replace("\n", "\\n")
        .replace('"', '\\"')
    )

    html_code = f"""
    <div style="margin: 8px 0; font-family: 'Inter', -apple-system, sans-serif;">
        <button id="{button_id}" onclick="copyText_{button_id}()" style="
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            color: #1F2937;
            font-size: 13px;
            font-weight: 500;
            padding: 7px 14px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        ">
            📋 {button_label}
        </button>
        <span id="msg-{button_id}" style="
            display: none;
            color: #16A34A;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        ">✓ Copied!</span>
    </div>
    <script>
    function copyText_{button_id}() {{
        const text = "{escaped_text}";
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('{button_id}');
            const msg = document.getElementById('msg-{button_id}');
            msg.style.display = 'inline';
            setTimeout(() => {{
                msg.style.display = 'none';
            }}, 2000);
        }}).catch(err => {{
            console.error('Copy failed: ', err);
        }});
    }}
    </script>
    """
    components.html(html_code, height=45)


def is_valid_youtube_url(url: str) -> bool:
    """Validates standard, shorts, and embed YouTube video URLs."""
    if not url or not url.strip():
        return False
    youtube_pattern = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/)[a-zA-Z0-9_-]+.*$'
    )
    return bool(youtube_pattern.match(url.strip()))


def format_complete_analysis(result: dict, source_label: str) -> str:
    """Formats full analysis into a single clean text export."""
    title = result.get("title", "Untitled Analysis")
    summary = result.get("summary", "No summary available.")
    action_items = result.get("action_items", "None")
    key_decisions = result.get("key_decisions", "None")
    open_questions = result.get("open_questions", "None")
    transcript = result.get("transcript", "No transcript available.")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""================================================================================
AI VIDEO ASSISTANT - COMPLETE INTELLIGENCE REPORT
Generated on: {timestamp}
Source: {source_label}
================================================================================

TITLE:
{title}

--------------------------------------------------------------------------------
EXECUTIVE SUMMARY:
--------------------------------------------------------------------------------
{summary}

--------------------------------------------------------------------------------
ACTION ITEMS:
--------------------------------------------------------------------------------
{action_items}

--------------------------------------------------------------------------------
KEY DECISIONS:
--------------------------------------------------------------------------------
{key_decisions}

--------------------------------------------------------------------------------
OPEN QUESTIONS & FOLLOW-UPS:
--------------------------------------------------------------------------------
{open_questions}

--------------------------------------------------------------------------------
FULL TRANSCRIPT:
--------------------------------------------------------------------------------
{transcript}

================================================================================
Generated by AI Video Assistant | Powered by OpenRouter & Whisper
================================================================================
"""


# ==============================================================================
# 3. SESSION STATE INITIALIZATION
# ==============================================================================
if "history" not in st.session_state:
    st.session_state["history"] = []

if "current_result" not in st.session_state:
    st.session_state["current_result"] = None

if "current_source_label" not in st.session_state:
    st.session_state["current_source_label"] = ""

if "is_processing" not in st.session_state:
    st.session_state["is_processing"] = False


# ==============================================================================
# 4. SIDEBAR NAVIGATION & HISTORY
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
        <span style="font-size: 26px;">🎬</span>
        <div>
            <div style="font-size: 16px; font-weight: 700; color: #111827;">AI Video Assistant</div>
            <div style="font-size: 12px; color: #64748B;">SaaS Meeting Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 12px 0;'>", unsafe_allow_html=True)

    # Navigation
    nav_options = ["🏠 Dashboard", "➕ New Analysis", "📜 Processing History", "ℹ️ About"]
    selected_nav = st.radio("Navigation", nav_options, index=0, label_visibility="collapsed")

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 16px 0;'>", unsafe_allow_html=True)

    # Session Processing History
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>RECENT ANALYSES</div>", unsafe_allow_html=True)
    if st.session_state["history"]:
        for item in reversed(st.session_state["history"]):
            short_name = (item["title"][:26] + "...") if len(item["title"]) > 26 else item["title"]
            if st.button(f"📄 {short_name}", key=f"hist_{item['id']}", use_container_width=True):
                st.session_state["current_result"] = item["result"]
                st.session_state["current_source_label"] = item["title"]
                st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state["history"] = []
            st.rerun()
    else:
        st.markdown("<div style='font-size: 13px; color: #64748B; margin-bottom: 10px;'>No past analyses in this session yet.</div>", unsafe_allow_html=True)
        if st.button("💡 Load Demo Analysis", use_container_width=True):
            demo_result = {
                "title": "Q4 Engineering Sync: AI Video Assistant Launch",
                "summary": """**Executive Summary: Q4 Engineering Sync**

*   **Platform Launch Date:** Official deployment scheduled for **November 15, 2026**.
*   **Infrastructure Highlights:**
    *   Unified LLM routing through **OpenRouter** using Nemotron-3-Ultra.
    *   Hardened rate-limit handling with exponential backoff on HTTP 429 errors.
*   **Audio Pipeline:** Local Whisper inference for English, Sarvam AI for Hinglish translation.
*   **Next Steps:** Staging deployment on Wednesday; final security sign-off Friday.""",
                "transcript": """Alice: Welcome everyone to our Q4 Engineering Sync. Today we discuss the AI Video Assistant launch roadmap.
Bob: The engineering team has successfully migrated all LLM modules to OpenRouter, ensuring standardized retry handling and rate limiting resilience.
Charlie: Local Whisper transcription and Sarvam translation are fully tested on multiple video lengths.
Alice: Our official deployment date is set for November 15, 2026.
Bob: I will deploy the staging build by Wednesday 5 PM.
Dev2: I will finish unit tests for exponential backoff retries by Friday.
Alice: Great work everyone, meeting adjourned.""",
                "action_items": """1. **Deploy staging build**
   - **Owner:** Bob
   - **Deadline:** Wednesday 5 PM

2. **Complete exponential backoff unit tests**
   - **Owner:** Dev2
   - **Deadline:** Friday

3. **Finalize production documentation**
   - **Owner:** Alice
   - **Deadline:** Next Monday""",
                "key_decisions": """1. Deploy the AI Video Assistant to production on November 15, 2026.
2. Standardize all AI summarization and extraction on OpenRouter Nemotron-3-Ultra model.
3. Use ChromaDB with local sentence embeddings for contextual RAG search.""",
                "open_questions": """1. Should streaming response support be integrated into the Phase 2 RAG chat?
2. Are additional multilingual audio models required for regional dialects?""",
                "rag_chain": None,
            }
            st.session_state["current_result"] = demo_result
            st.session_state["current_source_label"] = "Demo: Q4 Engineering Sync"
            st.session_state["history"].append({
                "id": "demo001",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "title": demo_result["title"],
                "result": demo_result,
            })
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 16px 0;'>", unsafe_allow_html=True)

    # Architecture Overview
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>SYSTEM ARCHITECTURE</div>", unsafe_allow_html=True)
    current_model = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
    has_api_key = bool(os.getenv("OPENROUTER_API_KEY"))

    st.markdown(f"""
    <div style="font-size: 12px; color: #475569; line-height: 1.7;">
        <div>• <b>Model:</b> <code style="color: #7C3AED; background: #F5F3FF; padding: 2px 5px; border-radius: 4px;">{current_model.split('/')[-1]}</code></div>
        <div>• <b>Provider:</b> OpenRouter API</div>
        <div>• <b>Transcription:</b> Local Whisper / Sarvam</div>
        <div>• <b>Vector Store:</b> ChromaDB</div>
        <div style="margin-top: 6px;">• <b>API Status:</b> {'<span style="color:#16A34A;font-weight:700;">● Connected</span>' if has_api_key else '<span style="color:#DC2626;font-weight:700;">● Missing Key</span>'}</div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. HEADER COMPONENT
# ==============================================================================
st.markdown("""
<div class="app-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 style="font-size: 26px; font-weight: 700; color: #111827; margin: 0; display: flex; align-items: center; gap: 10px;">
                <span>🎬</span> AI Video Assistant
            </h1>
            <p style="font-size: 14px; color: #64748B; margin-top: 4px; margin-bottom: 0;">Turn videos into knowledge.</p>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span class="app-badge">✨ OpenRouter Powered</span>
            <span class="app-badge" style="background:#F1F5F9 !important; color:#475569 !important; border-color:#CBD5E1 !important;">Map-Reduce LCEL</span>
        </div>
    </div>
    <div style="font-size: 13px; color: #475569; margin-top: 10px; max-width: 780px; line-height: 1.5;">
        Extract executive summaries, verbatim transcripts, actionable task checklists,
        and key decisions from YouTube videos or local media files.
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 6. ROUTING VIEW LOGIC
# ==============================================================================
if "New Analysis" in selected_nav:
    st.session_state["current_result"] = None
    st.session_state["current_source_label"] = ""

if "About" in selected_nav:
    st.markdown("""
    <div class="saas-card">
        <h3 style="color:#111827; margin-top:0;">About AI Video Assistant</h3>
        <p style="color:#374151; line-height: 1.6;">
            AI Video Assistant is an enterprise-ready video and meeting intelligence platform built
            with Streamlit, LangChain, and OpenRouter.
        </p>
        <h4 style="color:#111827; margin-top:16px;">Core Architecture:</h4>
        <ul style="color:#374151; line-height: 1.7;">
            <li><b>Ingestion:</b> Audio extraction via yt-dlp and 16kHz WAV normalization via FFmpeg/Pydub.</li>
            <li><b>Transcription:</b> Speech recognition using OpenAI Whisper (English) and Sarvam AI (Hinglish/multilingual).</li>
            <li><b>Summarization:</b> Map-Reduce architecture using RecursiveCharacterTextSplitter and OpenRouter LLMs.</li>
            <li><b>Extraction:</b> Structured parsing of action items (with owner and deadlines), decisions, and open questions.</li>
            <li><b>Reliability:</b> Centralized exponential backoff retries respecting HTTP 429 Retry-After headers.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ==============================================================================
# 7. INPUT CARD (YOUTUBE URL OR LOCAL FILE UPLOAD)
# ==============================================================================
st.markdown('<div class="saas-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title"><span>📥</span> Video Ingestion & Settings</div>', unsafe_allow_html=True)

input_tab1, input_tab2 = st.tabs(["🔗 YouTube URL", "📁 Local File Upload"])

youtube_url = ""
uploaded_file = None

def clear_url_callback():
    st.session_state["yt_input"] = ""

with input_tab1:
    col_yt1, col_yt2 = st.columns([5, 1])
    with col_yt1:
        youtube_url = st.text_input(
            "Enter YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            key="yt_input",
            help="Supports standard YouTube videos, shorts, and embed URLs",
            label_visibility="collapsed",
        )
    with col_yt2:
        st.button("Clear", on_click=clear_url_callback, use_container_width=True)

with input_tab2:
    uploaded_file = st.file_uploader(
        "Upload audio or video file",
        type=["mp4", "mp3", "wav", "m4a", "webm", "mov"],
        help="Supported formats: MP4, MP3, WAV, M4A, WEBM, MOV (Max recommended: 200MB)",
        label_visibility="collapsed",
    )
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.markdown(f"<div style='font-size: 13px; color: #475569; margin-top: 6px;'>Attached: <b>{uploaded_file.name}</b> ({file_size_mb:.1f} MB)</div>", unsafe_allow_html=True)

# Settings Row
col_opt1, col_opt2 = st.columns([2, 3])

with col_opt1:
    target_language = st.selectbox(
        "Target Language",
        options=["English", "Hindi", "Hinglish"],
        index=0,
        help="Select the target language for speech processing",
    )

with col_opt2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Generate Summary", use_container_width=True, disabled=st.session_state["is_processing"])

st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 8. PIPELINE EXECUTION & PROCESSING INTERFACE
# ==============================================================================
if generate_btn:
    # 1. Validation
    source_to_process = None
    source_display_name = ""
    is_temp_file = False

    if youtube_url.strip():
        if not is_valid_youtube_url(youtube_url):
            st.error("⚠️ Invalid YouTube URL. Please enter a valid URL (e.g., https://www.youtube.com/watch?v=... or https://youtu.be/...)")
            st.stop()
        source_to_process = youtube_url.strip()
        source_display_name = youtube_url.strip()

    elif uploaded_file is not None:
        source_display_name = uploaded_file.name
        file_ext = os.path.splitext(uploaded_file.name)[-1].lower() or ".wav"
        
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, dir=temp_dir)
        temp_file.write(uploaded_file.read())
        temp_file.flush()
        temp_file.close()
        source_to_process = temp_file.name
        is_temp_file = True

    else:
        st.warning("⚠️ Please provide a YouTube URL or upload a local media file to begin.")
        st.stop()

    if not os.getenv("OPENROUTER_API_KEY"):
        st.error("❌ OPENROUTER_API_KEY is not configured in your .env file. Please check your environment variables.")
        if is_temp_file and source_to_process and os.path.exists(source_to_process):
            os.remove(source_to_process)
        st.stop()

    # 2. Execution with Processing Interface
    st.session_state["is_processing"] = True
    
    stages_order = [
        "Downloading / Loading Audio",
        "Audio Processing",
        "Transcribing Audio",
        "Generating Summary",
        "Generating Title",
        "Extracting Action Items",
        "Completed"
    ]
    
    status_container = st.status("🎬 Processing pipeline initiated...", expanded=True)
    
    def ui_status_callback(stage_name: str):
        with status_container:
            st.write(f"⏳ **Stage:** {stage_name}...")

    try:
        ui_status_callback(stages_order[0])
        start_time = time.time()

        # Execute existing backend pipeline
        pipeline_result = run_pipeline(
            source=source_to_process,
            language=target_language.lower(),
            status_callback=ui_status_callback,
        )

        elapsed = time.time() - start_time
        status_container.update(
            label=f"✅ Pipeline Completed Successfully in {elapsed:.1f}s!",
            state="complete",
            expanded=False,
        )

        st.session_state["current_result"] = pipeline_result
        st.session_state["current_source_label"] = source_display_name

        # Append to session history
        history_entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": pipeline_result.get("title") or source_display_name,
            "result": pipeline_result,
        }
        st.session_state["history"].append(history_entry)

    except PermissionError as e:
        status_container.update(label="Authentication Error", state="error", expanded=True)
        st.error(f"🔐 Authentication Error: {e}")
    except RuntimeError as e:
        status_container.update(label="Execution Error", state="error", expanded=True)
        st.error(f"⚠️ Processing Error: {e}")
    except Exception as e:
        status_container.update(label="Unexpected Error", state="error", expanded=True)
        st.error(f"❌ An unexpected error occurred: {e}")
    finally:
        st.session_state["is_processing"] = False
        if is_temp_file and source_to_process and os.path.exists(source_to_process):
            try:
                os.remove(source_to_process)
            except Exception:
                pass


# ==============================================================================
# 9. RESULTS DASHBOARD (4 TABS)
# ==============================================================================
if st.session_state["current_result"]:
    result = st.session_state["current_result"]
    source_label = st.session_state["current_source_label"]

    title = result.get("title", "Generated Meeting Summary")
    summary = result.get("summary", "No summary available.")
    transcript = result.get("transcript", "No transcript available.")
    action_items = result.get("action_items", "No action items found.")
    key_decisions = result.get("key_decisions", "No key decisions found.")
    open_questions = result.get("open_questions", "No open questions found.")

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 24px 0;'>", unsafe_allow_html=True)

    # High-level Metrics Header
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Source", "YouTube" if "http" in source_label else "Uploaded File")
    with col_m2:
        word_count = len(transcript.split()) if transcript else 0
        st.metric("Transcript Words", f"{word_count:,}")
    with col_m3:
        est_read_min = max(1, word_count // 200)
        st.metric("Est. Read Time", f"~{est_read_min} min")
    with col_m4:
        st.metric("Language", target_language if 'target_language' in locals() else "English")

    # Tabs
    tab_summary, tab_transcript, tab_actions, tab_title = st.tabs([
        "📋 Summary",
        "📝 Transcript",
        "✅ Action Items",
        "📌 Title",
    ])

    # --------------------------------------------------------------------------
    # TAB 1: SUMMARY
    # --------------------------------------------------------------------------
    with tab_summary:
        st.markdown(f"""
        <div class="hero-title-card">
            <div style="font-size: 12px; font-weight: 700; color: #7C3AED; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                Executive Title
            </div>
            <h2 class="hero-title-text">{title}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span>📋</span> AI Meeting Summary (Map-Reduce)</div>', unsafe_allow_html=True)
        st.markdown(summary)
        st.markdown('</div>', unsafe_allow_html=True)

        col_sum_act1, col_sum_act2, col_sum_act3 = st.columns([1.5, 1.5, 3])
        with col_sum_act1:
            render_clipboard_button(summary, "Copy Summary", "btn_copy_sum")
        with col_sum_act2:
            st.download_button(
                label="⬇️ Download Summary (.txt)",
                data=summary,
                file_name=f"summary_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col_sum_act3:
            complete_text = format_complete_analysis(result, source_label)
            st.download_button(
                label="📦 Download Complete Analysis (.txt)",
                data=complete_text,
                file_name=f"complete_analysis_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # --------------------------------------------------------------------------
    # TAB 2: TRANSCRIPT
    # --------------------------------------------------------------------------
    with tab_transcript:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        col_tr_head1, col_tr_head2 = st.columns([3, 1])
        with col_tr_head1:
            st.markdown('<div class="card-title"><span>📝</span> Complete Speech-to-Text Transcript</div>', unsafe_allow_html=True)
        with col_tr_head2:
            expand_transcript = st.checkbox("Expand full view", value=False)

        if expand_transcript:
            st.markdown(f"""
            <div style="background-color: #F8F9FC; border: 1px solid #E5E7EB; border-radius: 8px; padding: 18px; font-size: 14px; line-height: 1.65; color: #1F2937; white-space: pre-wrap;">
{transcript}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="transcript-container">{transcript}</div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        col_tr_act1, col_tr_act2, _ = st.columns([1.5, 1.5, 3])
        with col_tr_act1:
            render_clipboard_button(transcript, "Copy Transcript", "btn_copy_tr")
        with col_tr_act2:
            st.download_button(
                label="⬇️ Download Transcript (.txt)",
                data=transcript,
                file_name=f"transcript_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # --------------------------------------------------------------------------
    # TAB 3: ACTION ITEMS & INSIGHTS
    # --------------------------------------------------------------------------
    with tab_actions:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span>✅</span> Extracted Action Items & Deliverables</div>', unsafe_allow_html=True)
        st.markdown(action_items)
        st.markdown('</div>', unsafe_allow_html=True)

        col_act_sub1, col_act_sub2 = st.columns(2)
        with col_act_sub1:
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span>🔑</span> Key Decisions Agreed</div>', unsafe_allow_html=True)
            st.markdown(key_decisions)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_act_sub2:
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span>❓</span> Unresolved Questions & Follow-ups</div>', unsafe_allow_html=True)
            st.markdown(open_questions)
            st.markdown('</div>', unsafe_allow_html=True)

        col_ac_act1, col_ac_act2, _ = st.columns([1.5, 1.5, 3])
        with col_ac_act1:
            render_clipboard_button(action_items, "Copy Action Items", "btn_copy_act")
        with col_ac_act2:
            st.download_button(
                label="⬇️ Download Action Items (.txt)",
                data=action_items,
                file_name=f"action_items_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # --------------------------------------------------------------------------
    # TAB 4: TITLE
    # --------------------------------------------------------------------------
    with tab_title:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span>📌</span> AI-Generated Professional Title</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hero-title-card" style="margin-top: 10px;">
            <div style="font-size: 13px; color: #7C3AED; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                Concise meeting heading (max 8 words):
            </div>
            <div style="font-size: 26px; font-weight: 700; color: #581C87;">
                "{title}"
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_title_act1, _ = st.columns([2, 4])
        with col_title_act1:
            render_clipboard_button(title, "Copy Title", "btn_copy_title")
        st.markdown('</div>', unsafe_allow_html=True)
