# TrendAnalisys API

TrendAnalisys API is a powerful backend service designed to fuel a sophisticated content and affiliate marketing research tool, likely for a platform called Noodl. It provides a multi-phased analysis engine that takes a simple topic and generates comprehensive insights, from trend analysis and blog ideas to keyword research and affiliate marketing opportunities.

The system is built with a Python/Flask backend that performs all the heavy lifting, a Supabase database for persistent storage with Row Level Security (RLS), and is designed to be consumed by a Noodl frontend application.

## Features

-   **Phase 1: Enhanced Trend Research:** Analyzes a given topic for current trends, content gaps, and market insights using Google Trends and LLM-powered analysis.
-   **Phase 2: Blog Idea Generation:** Takes the results from the trend analysis and generates a wealth of blog post ideas, complete with outlines, strategic insights, and content calendars.
-   **Phase 3: Keyword Research Integration:** Allows users to import keyword data from popular SEO tools (Ahrefs, SEMrush, Moz, etc.) to enrich and optimize the generated blog ideas.
-   **Affiliate Marketing Analysis:** Researches and analyzes affiliate program opportunities related to the topic, providing profitability scores and strategic recommendations.
-   **Efficient Database-First Architecture:** Implements a smart storage system for affiliate programs, searching the existing database before making new API calls to reduce redundancy and improve performance.
-   **Multi-LLM Support:** Integrates with a variety of Large Language Models, including OpenAI, Anthropic, DeepSeek, and Gemini.
-   **Secure & Scalable:** Uses Supabase with Row-Level Security (RLS) to ensure that users can only access their own data.

## Architecture

The system is composed of three main parts:

1.  **Python/Flask Backend (This Repository):** A robust API server that exposes endpoints for all analysis phases. It handles the complex logic, interacts with external APIs (LLMs, Google Trends), and manages data storage.
2.  **Supabase Database:** A PostgreSQL database with the Supabase platform providing a simple API, authentication, and Row-Level Security. It acts as the central data store for all analysis results.
3.  **Noodl Frontend:** A low-code/no-code application that provides the user interface. It authenticates users, makes requests to the Python backend, and uses custom JavaScript to display the data fetched from Supabase.

## Getting Started

Follow these instructions to get the backend server up and running on your local machine.

### Prerequisites

-   Python 3.8+
-   `pip` and `venv`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLTK data:**
    Some features require data from the NLTK library. Run the following commands to download them:
    ```bash
    python -c "import nltk; nltk.download('punkt')"
    python -c "import nltk; nltk.download('stopwords')"
    ```

## Configuration

The application uses a `.env` file to manage environment variables.

1.  **Create a `.env` file** in the root of the project. You can copy the example file:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** with your credentials. The following variables are required:

    ```dotenv
    # Supabase Credentials
    SUPABASE_URL="https://your-project-ref.supabase.co"
    SUPABASE_KEY="your-supabase-anon-key"

    # LLM API Keys (at least one is required)
    OPENAI_API_KEY="sk-..."
    ANTHROPIC_API_KEY="..."
    DEEPSEEK_API_KEY="..."
    GEMINI_API_KEY="..."

    # Optional API Keys
    LINKUP_API_KEY="..."
    GOOGLE_TRENDS_API_KEY="..."
    ```

## Usage

### Running the Server

You can run the server in development mode using Flask's built-in server:

```bash
flask run --host=0.0.0.0 --port=8001
```

For production, it is recommended to use a WSGI server like Gunicorn:

```bash
gunicorn --bind 0.0.0.0:8001 main:app
```

### Example API Request

Here is an example of how to call the main trend research endpoint using `curl`. Remember to replace `"your-uuid"` and `"your-key"` with a valid user ID and API key.

```bash
curl -X POST http://localhost:8001/api/v2/enhanced-trend-research \
-H "Content-Type: application/json" \
-d '{
    "topic": "AI in marketing",
    "user_id": "your-uuid-from-noodl-auth",
    "llm_config": {
        "provider": "openai",
        "api_key": "your-key"
    },
    "focus_area": "SaaS companies",
    "target_audience": "Marketing professionals"
}'
```

## API Endpoints

The API is structured into several phases. Here are some of the key endpoints:

-   `POST /api/v2/enhanced-trend-research`: Kicks off the Phase 1 trend analysis.
-   `POST /api/v2/generate-blog-ideas/<analysis_id>`: Starts Phase 2 blog idea generation from a completed trend analysis.
-   `POST /api/v2/keyword-research/upload`: Allows uploading a CSV of keyword data for Phase 3.
-   `POST /api/v2/keyword-research/enhance-blog-ideas`: Enriches blog ideas with the uploaded keyword data.
-   `POST /api/v2/affiliate-research`: Performs affiliate program research for a given topic.
-   `GET /api/v2/health`: A health check endpoint for the server.

## Testing

This project is set up to use `pytest`. To run the tests, execute the following command in the root directory:

```bash
pytest
```
