# Web Scraper for Vectorization

This project is a powerful and versatile web scraper designed to crawl websites, extract clean text content, and prepare it for AI applications like Retrieval-Augmented Generation (RAG). It comes with two user-friendly interfaces: a web-based UI built with Streamlit and a professional Command-Line Interface (CLI) built with Typer.



## Key Features

- **Dual Interfaces**: Run the scraper through an interactive **Web UI** or a powerful **CLI**.
- **Concurrent Scraping**: Uses **multithreading** to fetch multiple pages simultaneously for high performance.
- **Respectful Crawling**: Automatically reads and respects `robots.txt` rules and applies rate limiting to avoid overwhelming servers.
- **AI-Ready Data**: Optionally generates **sentence embeddings** (vectors) for each text chunk using `sentence-transformers`, making the output ready for vector databases.
- **Structured Output**: Saves cleaned text content in a structured `JSON` format and provides a detailed `TXT` navigation log.
- **Customizable**: Control crawl depth, number of threads, request delays, and user-agent strings.

---
## Project Structure

```
.
├── output/                  # Default directory for output files
├── app.py                   # The Streamlit Web UI
├── cli.py                   # The Typer CLI tool
├── scraper.py               # Core WebScraper class and logic
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

---
## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a new virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

Create a file named `requirements.txt` with the following content:

```text
# requirements.txt
requests
beautifulsoup4
streamlit
typer
rich
sentence-transformers
torch
```

Now, install all the required libraries at once:

```bash
pip install -r requirements.txt
```

---
## How to Use

You can run the scraper using either the Web UI or the CLI.

### 🖥️ Option 1: Using the Web UI (Streamlit)

The web interface is the easiest way to use the scraper. It provides a form to enter all the necessary parameters.

**To start the app, run:**
```bash
streamlit run app.py
```
Your browser will automatically open a new tab with the user interface. Fill in the fields and click "Start Scraping".

### ⌨️ Option 2: Using the CLI Tool (Typer)

The CLI is perfect for scripting, automation, or for users who prefer the command line.

**Get Help:**
```bash
python cli.py --help
```

**Basic Usage:**
*Scrapes the first two levels of the Python docs and saves results to the `output/` directory.*
```bash
python cli.py [https://docs.python.org/3/](https://docs.python.org/3/) --depth 2
```

**Advanced Usage:**
*Scrapes up to depth 3 with 10 threads, saves to a custom directory, and enables vectorization.*
```bash
python cli.py [https://docs.python.org/3/](https://docs.python.org/3/) --depth 3 --threads 10 --output-dir ./py_docs --vectorize
```

---
## Output Files

The scraper generates two primary files in the specified output directory (`output/` by default):

1.  **`scraped_data.json`**: Contains the structured text data. Each page includes its URL, navigation path, and a list of text "chunks". If vectorization is enabled, each chunk will also include its embedding vector.
2.  **`scraped_log.txt`**: A detailed log showing the navigation path for every link visited and its status (e.g., `scraped`, `denied by robots.txt`, `failed`).