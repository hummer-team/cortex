# Cortex 🧠 - Your Personal AI-Powered Second Brain

**Cortex is not just another note-taking app or a knowledge base. It's your personal cognitive assistant, designed to combat context fragmentation and enhance your deep thinking process in the age of LLMs.**

In a world where our digital interactions are scattered across countless platforms—ChatGPT, Gemini, IDEs, browsers—Cortex acts as your unified, private, and intelligent memory layer. It remembers what you've learned, discussed, and decided, empowering you to have smarter conversations with any AI, anytime.

[!License: Apache License 2.0](http://www.apache.org/licenses/)
[!Python Version](https://www.python.org/downloads/)
[!Status](In gestation，In development 😄)

---

## The Core Problem Cortex Solves

We all pay a heavy **"Context Tax"** every day. We manually recall, copy, and paste background information to have a meaningful conversation with LLMs. Our valuable insights are fragmented across different chat histories and applications. Cortex is designed to solve this by:

1.  **Eliminating Context Tax**: Automatically providing deep, relevant context for your AI conversations, freeing you from manual context management.
2.  **Unifying Fragmented Memory**: Integrating your interactions from various LLMs and local development environments into a single, searchable memory.
3.  **Ensuring Privacy & Sovereignty**: Operating with a **local-first** architecture. All your data is stored and processed on your own device, giving you 100% control and privacy.

## How It Works: From "AI Tool" to "Cognitive Partner"

Cortex works as an **intelligent context assistant**, not a fully automated agent. You are always in control.

1.  **🧠 Ingest & Learn**: Manually import your chat histories (from ChatGPT, Gemini, etc.) or let Cortex's background agents (future feature) passively observe your work in your IDE and browser. Cortex cleans, chunks, and converts this information into semantic "memory fragments" stored locally.

2.  **🔍 Query & Recall**: Before starting a new conversation with an LLM, you ask Cortex a simple question or provide a topic in its "Memory Console". For example: *"our final design for the workflow engine's routing logic"*.

3.  **✨ Synthesize & Prepare**: Cortex's retrieval engine searches your local memory for the most relevant fragments. It then uses a local, lightweight LLM to synthesize these scattered pieces of information into a coherent, condensed **"Memory Packet"**.

4.  **🚀 Empower & Converse**: Cortex presents you with this high-quality "Memory Packet" and a "Copy to Clipboard" button. You then paste this context into your LLM of choice and ask your new question. The LLM, now armed with a perfect memory of your past work, provides a vastly more insightful and accurate response.

## Key Features (MVP)

*   **Local-First Architecture**: All data, indexes, and models run on your local machine. Nothing is sent to the cloud without your explicit action.
*   **Manual Memory Ingestion**: Simple drag-and-drop interface to import your exported LLM chat histories (JSON, Markdown).
*   **Semantic Memory Query**: Use natural language to search your entire memory base.
*   **AI-Powered Context Synthesis**: Leverages local LLMs to distill retrieved memories into a clean, high-quality context summary.
*   **One-Click Context Export**: Easily copy the generated "Memory Packet" for use in any LLM platform.

## Technology Stack

Cortex is built on a modern, robust, and privacy-focused technology stack:

| Component | Technology | Reason |
| :--- | :--- | :--- |
| **Core Application** | **Electron** (TypeScript) | Cross-platform desktop application framework. |
| **Backend Engine** | **Python** with **FastAPI** | High-performance, modern web framework for the local API. |
| **Vector Database** | **ChromaDB** | Embeddable, developer-friendly, and open-source vector store. |
| **Embedding Model** | **Sentence Transformers** | Runs locally, open-source, excellent performance. |
| **Synthesis LLM** | **Ollama** (with Llama 3/Mistral) | Runs large language models locally for ultimate privacy and zero cost. |
| **UI Framework** | **React / Vue** | Modern, component-based UI development. |

## Getting Started (Development)

1.  **Prerequisites**:
    *   Python 3.12.5+
    *   Node.js 18+
    *   Ollama installed and running.

    