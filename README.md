# 🎬 AI Video Assistant
> **Turn videos into knowledge.**

An enterprise-ready AI meeting and video intelligence platform that automatically ingests audio/video from YouTube or local files, transcribes speech with Whisper or Sarvam AI, performs multi-chunk **Map-Reduce summarization**, extracts structured action items, decisions, and questions via **OpenRouter**, and enables semantic Q&A with **ChromaDB RAG**.

---

## 🌟 Key Features

* **Dual Ingestion Engine**:
  * **YouTube URLs**: Directly downloads and extracts high-quality audio using `yt-dlp`.
  * **Local File Upload**: Drag-and-drop support for `MP4`, `MP3`, `WAV`, `M4A`, `WEBM`, and `MOV`.
* **Audio Normalization & Chunking**:
  * Automatically converts input media to single-channel 16kHz WAV format with `FFmpeg` and `Pydub`.
  * Slices long audio recordings into manageable 10-minute chunks for robust transcription.
* **Hybrid Speech-to-Text (STT)**:
  * **English**: High-accuracy local inference via OpenAI Whisper.
  * **Hinglish / Multilingual**: Cloud transcription and translation powered by Sarvam AI (`saaras:v2.5`).
* **Map-Reduce Summarization Architecture**:
  * Chunks long transcripts with `RecursiveCharacterTextSplitter` (3,000 characters, 200 overlap).
  * Executes individual chunk-level Map summaries in parallel.
  * Synthesizes partial summaries into a final, executive bulleted report in the Reduce phase.
* **Centralized OpenRouter LLM Routing**:
  * Fully unified model management under `core/llm.py`.
  * Standardized on `nvidia/nemotron-3-ultra-550b-a55b:free` (or any custom model via `.env`).
* **Resilient Rate-Limit & Error Handling**:
  * Automatic exponential backoff retry mechanism specifically tuned for HTTP 429 rate limits.
  * Honors HTTP `Retry-After` headers from OpenRouter.
  * Immediate, actionable error handling for authentication (401), credit/quota exhaustion (402), and model availability (404).
* **Structured Insights Extraction**:
  * Extracts actionable tasks formatted with task descriptions, responsible owners, and deadlines.
  * Identifies agreed-upon key decisions and unresolved questions needing follow-up.
* **Contextual RAG Q&A (Phase 2)**:
  * Persistent vector storage with ChromaDB and `all-MiniLM-L6-v2` sentence transformers.
  * Context-grounded Q&A retrieving top-4 semantic matches (`k=4`).
* **Modern Minimal Light SaaS Dashboard**:
  * Built with Streamlit enforcing a crisp, high-contrast light theme (`#F8F9FC` background, `#FFFFFF` cards, `#7C3AED` purple accents).
  * 4 interactive result tabs: **Summary**, **Transcript**, **Action Items**, and **Title**.
  * Interactive copy-to-clipboard buttons and one-click `.txt` downloads.
  * Session-based processing history.

---

## 🏗️ System Architecture

```
                      +-----------------------------------+
                      |   YouTube URL / Local Audio/Video |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------------------------+
                      | Ingestion & Preprocessing (utils) |
                      |  - yt-dlp: Audio download         |
                      |  - FFmpeg / Pydub: WAV conversion |
                      |  - Pydub: 10-min chunk slicing    |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------------------------+
                      | Speech-to-Text Engine (transcriber)
                      |  - English: Local Whisper model   |
                      |  - Hinglish: Sarvam AI STT API    |
                      +-----------------+-----------------+
                                        |
                                   [Transcript]
                                        |
       +--------------------+-----------+-----------+--------------------+
       |                    |                       |                    |
       v                    v                       v                    v
+--------------+   +-------------------+   +--------------------+  +------------+
| Title Gen    |   | Map-Reduce Summary|   | Metadata Extractor |  | VectorStore|
| (summarizer) |   | (summarizer)      |   | (extractor)        |  | (ChromaDB) |
+------+-------+   +--------+----------+   +---------+----------+  +-----+------+
       |                    |                        |                   |
       |                    |                        |                   v
       |                    |                        |             +------------+
       |                    |                        |             | RAG Engine |
       |                    |                        |             | (rag_engine|
       |                    |                        |             +-----+------+
       |                    |                        |                   |
       +--------------------+-----------+------------+-------------------+
                                        |
                                        v
                       +----------------------------------+
                       | Centralized LLM Engine (core.llm)|
                       |  - Provider: OpenRouter API      |
                       |  - Model: Nemotron 3 Ultra 550B  |
                       |  - Exponential Backoff (HTTP 429)|
                       |  - Retry-After Header Compliance |
                       +-----------------+----------------+
                                         |
                       +-----------------+----------------+
                       |                                  |
                       v                                  v
         +----------------------------+     +----------------------------+
         | Streamlit Web App (app.py) |     |  Interactive CLI (main.py) |
         +----------------------------+     +----------------------------+
```

---

## 📂 Project Structure

```
AI video assitant/
│
├── .streamlit/
│   └── config.toml          # Enforces strict light SaaS theme and server settings
│
├── core/
│   ├── llm.py               # Centralized OpenRouter client & exponential backoff retry handler
│   ├── summarizer.py        # Map-Reduce transcript summarizer & title generator
│   ├── extractor.py         # Action items, key decisions, and questions extractor
│   ├── rag_engine.py        # LCEL retrieval-augmented generation pipeline
│   ├── transcriber.py       # Whisper and Sarvam AI speech-to-text integration
│   └── vector_store.py      # ChromaDB vector store and HuggingFace embeddings
│
├── utils/
│   └── audio_processor.py   # yt-dlp downloader, FFmpeg conversion, and audio chunking
│
├── .env                     # Local environment secrets (never commit)
├── .env.example             # Configuration template for required API keys
├── app.py                   # Modern Streamlit SaaS Web Dashboard
├── main.py                  # Full end-to-end pipeline & interactive CLI entry point
├── pyproject.toml           # Project metadata and dependencies (managed via uv)
├── requirements.txt         # Standard pip-compatible requirements file
├── test_openrouter.py       # 7-stage automated migration and integration test suite
└── uv.lock                  # Exact dependency lockfile
```

---

## 🛠️ Prerequisites

1. **Python**: Version `3.12` or higher.
2. **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended for fast dependency resolution) or standard `pip`.
3. **FFmpeg**: Required on your system for audio/video processing:
   * **Windows**: `choco install ffmpeg` or `winget install Gyan.FFmpeg`
   * **macOS**: `brew install ffmpeg`
   * **Ubuntu/Debian**: `sudo apt update && sudo apt install -y ffmpeg`

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "AI video assitant"
```

### 2. Set Up Virtual Environment & Dependencies

Using **`uv`** (Recommended):
```powershell
# Create virtual environment and synchronize dependencies
uv sync
```

Alternatively, using standard **`pip`**:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the template to `.env`:
```powershell
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# OpenRouter API (Centralized LLM for Summarization, Titles, Extractions & RAG)
OPENROUTER_API_KEY="sk-or-v1-your-openrouter-api-key"
OPENROUTER_MODEL="nvidia/nemotron-3-ultra-550b-a55b:free"

# Audio Transcription & Translation (Whisper / Sarvam)
SARVAM_API_KEY="your_sarvam_api_key"
SARVAM_STT_MODEL="saaras:v2.5"

# Embeddings & HuggingFace (Optional)
HF_TOKEN="your_huggingface_token"
```

> **Note**: An OpenRouter API key can be obtained for free at [openrouter.ai](https://openrouter.ai/). The default model `nvidia/nemotron-3-ultra-550b-a55b:free` is completely free to use.

---

## 🚀 Running the Application

### Option A: Modern Streamlit Web Dashboard

Launch the browser interface:
```powershell
uv run streamlit run app.py
```
Or directly via virtual environment:
```powershell
.venv\Scripts\streamlit.exe run app.py
```

Open your browser at `http://localhost:8501`.

#### Features in the Web UI:
* **Interactive Ingestion**: Paste a YouTube URL or drag-and-drop local audio/video files.
* **Target Language**: Select between **English**, **Hindi**, and **Hinglish**.
* **Progress Tracking**: Real-time status indicators covering all 7 pipeline stages.
* **Results Dashboard**:
  * **📋 Summary Tab**: Executive title, formatted bullet-point summary, copy & download buttons.
  * **📝 Transcript Tab**: Full speech-to-text text container with expand/collapse view.
  * **✅ Action Items Tab**: Action items with assignees & deadlines, key decisions, and open questions.
  * **📌 Title Tab**: Prominent title hero card with one-click copy.
  * **📦 Export All**: Download complete intelligence report as `.txt`.
* **Sidebar History**: Instant access to previous analyses in the current session.

---

### Option B: Interactive Command-Line Interface (CLI)

Run the end-to-end pipeline in your terminal:
```powershell
uv run python main.py
```
Or:
```powershell
.venv\Scripts\python.exe main.py
```

1. Enter a YouTube URL or local file path when prompted.
2. Select target language (`english` or `hinglish`).
3. View the generated Title, Summary, Action Items, Key Decisions, and Open Questions directly in stdout.
4. Chat interactively with the meeting transcript via Phase 2 RAG search. Type `exit` to quit.

---

## 🧪 Automated Testing

A comprehensive 7-stage test suite is included in [test_openrouter.py](file:///c:/Users/ACER/Documents/Projects/AI%20video%20assitant/test_openrouter.py) to verify model connectivity, pipeline components, and error handling:

```powershell
uv run python test_openrouter.py
```

### Verified Test Cases:
| Test Suite | Component Tested | Verification Description |
| :--- | :--- | :--- |
| **Test 1** | `core/llm.py` | Validates `ChatOpenAI` OpenRouter base URL and model configuration. |
| **Test 2** | Codebase Integrity | Ensures zero deprecated Mistral imports remain in any core module. |
| **Test 3** | `generate_title()` | Verifies short professional meeting title generation (<8 words). |
| **Test 4** | `core/extractor.py` | Validates action items (task/owner/deadline), decisions, and open questions. |
| **Test 5** | `summarize()` | Tests multi-chunk Map-Reduce execution on long transcripts (>3000 chars). |
| **Test 6** | `core/rag_engine.py` | Verifies ChromaDB vector store indexing and semantic Q&A retrieval. |
| **Test 7** | Error Handling | Confirms graceful handling of empty inputs and rate limit retry backoff. |

---

## 🛡️ Error Handling & Rate Limiting

The centralized LLM client in `core/llm.py` enforces production-grade resilience:
* **HTTP 429 Rate Limits**: Automatically retries using exponential backoff (`delay = 2.0 * (2 ** attempt)`), honoring `Retry-After` headers if returned by OpenRouter (up to 5 attempts).
* **HTTP 401 Authentication**: Halts immediately with a clear `PermissionError` prompting the user to check `OPENROUTER_API_KEY`.
* **HTTP 402 Credits**: Immediately raises a descriptive `RuntimeError` regarding quota limits.
* **HTTP 404 Model Not Found**: Identifies invalid or decommissioned model names.
* **HTTP 5xx Server Errors**: Retries transient provider downtime up to 5 times.
* **Zero Silent Fallbacks**: Never returns fake or hallucinated summaries when an API error occurs.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
