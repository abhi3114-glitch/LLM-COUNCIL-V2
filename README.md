# LLM Council

**Where AI Models Debate, Critique, and Synthesize the Truth.**

![LLM Council Banner](header.jpg)

LLM Council is a next-generation AI reasoning platform that convenes a council of diverse Large Language Models (LLMs) to deliberate on your query. By leveraging the collective intelligence of models like **Llama 3.3**, **Gemini 2.0**, and **Mixtral**, it provides responses that are more accurate, balanced, and insightful than any single model could achieve alone.

---

## Key Improvements Over the Original

This project significantly expands upon the original concept (e.g., karpathy/llm-council) by transforming a basic script into a full-fledged, production-grade application.

| Feature | Original Concept | This Version |
| :--- | :--- | :--- |
| **Interface** | CLI / Basic Script | **Premium React Web App** with glassmorphism and animations |
| **Interaction** | Single-turn | **Multi-turn Chat** (Continue Chat) with context retention |
| **Reasoning** | Simple Ranking | **Debate Mode**: Models explicitly critique each other before ranking |
| **Control** | Hardcoded Models | **Dynamic Model Selection** via UI configuration |
| **Persistence** | None | **Conversation History** saved locally |
| **Visuals** | Text Output | **Visual Stages**: Carousel, Ranking Table, and Hero Card |
| **Cost** | High (Paid APIs) | **Free / Low-Cost** (Optimized for Gemini 2.0 Flash & Groq) |

---

## Key Features

### The 3-Stage Council Process
1.  **Stage 1: Individual Opinions**
    *   Multiple top-tier LLMs (Council Members) independently answer your question.
    *   Visualized as a sleek carousel of model cards.

2.  **Stage 2: Peer Review & Ranking**
    *   Models read each other's answers (anonymously) and rank them based on accuracy, depth, and helpfulness.
    *   **Debate Mode**: Toggle this to force models to *critique* each other's logic and expose fallacies before ranking.
    *   Displayed as a competitive leaderboard.

3.  **Stage 3: The Chairman's Verdict**
    *   A highly capable "Chairman" model (e.g., Llama 3.3 70B) synthesizes the best insights from all responses and rankings into one final, authoritative answer.
    *   Presented in a premium "Hero Card".

### Premium UI/UX
*   **"Big Tech" Aesthetic**: Clean, modern interface inspired by Google's Material Design 3.
*   **Dark Mode**: Fully supported, persistent dark theme for late-night research.
*   **Glassmorphism & Animations**: Smooth transitions, fade-ins, and shimmer effects for a delightful experience.
*   **Interactive**: Suggestion chips, hover effects, and a responsive sidebar.

### Powerful Configuration
*   **Model Selection**: Choose exactly which models sit on your council.
*   **Conversation History**: Save, manage, and delete past debates.
*   **Streaming**: Real-time feedback as models think and debate.
*   **Free Tier Optimization**: Built to run entirely on free or ultra-low-cost API tiers using **Gemini 2.0 Flash** and **Llama 3.3** (via Groq), making advanced AI reasoning accessible to everyone.

---

## Getting Started

### Prerequisites
*   **Python 3.8+**
*   **Node.js 16+**
*   API Keys for **OpenRouter**, **Google Gemini**, and **Groq**.

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/abhi3114-glitch/llm-council.git
    cd llm-council
    ```

2.  **Backend Setup**
    ```bash
    # Create virtual environment
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```env
    OPENROUTER_API_KEY=your_key_here
    GOOGLE_API_KEY=your_key_here
    GROQ_API_KEY=your_key_here
    ```

### Running the App

1.  **Start Backend**
    ```bash
    # From root directory
    uv run python -m backend.main
    ```

2.  **Start Frontend**
    ```bash
    # From frontend directory
    npm run dev
    ```

3.  Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Tech Stack

*   **Frontend**: React, Vite, CSS Modules (Custom Design System)
*   **Backend**: FastAPI, Python, Uvicorn
*   **AI Integration**: Google Generative AI SDK, Groq SDK, OpenRouter API
*   **State Management**: React Hooks & Context

---

## Credits

**Made with love by Abhi**

*   **GitHub**: [abhi3114-glitch](https://github.com/abhi3114-glitch)
*   **LinkedIn**: [Abhishek Pratap Singh Chauhan](https://www.linkedin.com/in/abhishek-pratap-singh-chauhan-5431a828a)

---

*LLM Council © 2025. All Rights Reserved.*
