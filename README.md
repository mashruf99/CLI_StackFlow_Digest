# CLI StackFlow Digest

> Search Stack Overflow questions and answers directly from your terminal — with readability analysis and QR codes. No browser needed.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-F48024?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-F48024?style=flat-square)]()
[![Level](https://img.shields.io/badge/Level-Beginner-ffcc00?style=flat-square)]()
[![Stack Overflow](https://img.shields.io/badge/Powered%20by-Stack%20Overflow-F48024?style=flat-square&logo=stackoverflow&logoColor=white)](https://stackoverflow.com)

---

## Project Overview

**CLI StackFlow Digest** is a Python-based command-line tool that searches Stack Overflow for any topic you provide and displays the most relevant questions and top-voted answers directly in the terminal. It also generates a readability score for the top answer and a QR code to the thread.

This is a **Level 1 Beginner Project** — ideal for learning how to work with REST APIs, parse JSON responses, and build interactive CLI tools in Python.

---

## Product Requirements (PRD)

### Problem Statement
When developers need a quick answer, they open a browser, search Stack Overflow, and get distracted by ads and tabs. There is no simple tool to search and read Stack Overflow answers from the terminal.

### Target Users
- Python beginners building their first real-world project
- Developers who prefer a terminal-centric workflow
- Anyone who frequently looks up answers on Stack Overflow

### Goals
- [x] Search Stack Overflow questions from the terminal
- [x] Browse paginated results and pick the most relevant question
- [x] Read top-voted answers with accepted status and author info
- [x] Understand answer complexity with a readability score
- [x] Generate a QR code to open the full thread on any device
- [x] Manage API key configuration securely using `.env`

### Non-Goals (Outside of Scope)
- No GUI or web interface (v1)
- No support for sites other than Stack Overflow (v1)
- No answer posting or voting
- No user login or OAuth flow

---

## Features

| Feature | Description | Library |
|---------|-------------|---------|
| **SO Search** | Searches Stack Overflow and returns top 8 relevant questions sorted by relevance and votes | `requests` |
| **Answer Display** | Fetches top 3 answers for selected question with vote count, accepted status, and 400-char preview | `stackexchange api` |
| **Table Formatting** | Displays question details and readability metrics in a clean `fancy_grid` table | `tabulate` |
| **QR Code** | Generates and saves a PNG QR code from the thread URL | `qrcode[pil]` |
| **Readability Score** | Runs Flesch score, grade level, and difficulty rating on the top answer | `textstat` |
| **Pagination** | Press `[n]` for next page, `[s]` for a new search without restarting | built-in |
| **Env Management** | Stores Stack Exchange API key in `.env` file; falls back to 300 req/day without a key | `python-dotenv` |

---

## Project Structure

```
CLI_StackFlow_Digest/
│
├── news_digest.py        # Main application file
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (git-ignored)
├── .env.example          # Example env file (committed)
├── .gitignore            # Files to ignore in git
└── README.md             # This file
```

---

## Tech Stack

```
Python 3.8+
├── requests          → Stack Exchange API calls
├── tabulate          → Terminal table formatting
├── qrcode[pil]       → QR code generation
├── textstat          → Readability analysis
└── python-dotenv     → .env file loading
```

---

## Installation

### Prerequisites
- Python 3.8 or above
- pip (Python package manager)
- Git
- Stack Exchange API key (free — see step 4)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/mashruf99/CLI_StackFlow_Digest.git
cd CLI_StackFlow_Digest
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Get a Free API Key

1. Go to [stackapps.com/apps/oauth/register](https://stackapps.com/apps/oauth/register)
2. Log in with your Stack Overflow account
3. Fill in the form:
   - **Application Name:** CLI StackFlow Digest
   - **OAuth Domain:** stackexchange.com
   - **Application Website:** https://stackexchange.com
4. Click **Register Your Application**
5. Copy the `Key` value from the next page

> Without a key the tool still works, but is limited to 300 requests/day. With a key it is 10,000/day.

### Step 5 — Create .env File

```bash
cp .env.example .env
```

Open `.env` and fill in your key:

```env
APP_NAME=CLI StackFlow Digest
VERSION=1.0.0
STACKOVERFLOW_KEY=your_key_here
```

### Step 6 — Run!

```bash
python news_digest.py
```

---

## Usage

```
$ python news_digest.py

========================================================
  CLI StackFlow Digest v1.0
========================================================

  Search Stack Overflow: caching

  Searching Stack Overflow for: "caching"...

  Results (page 1):

  [1] What is the difference between cache and buffer?
       Answered  |  Votes: 892  |  Answers: 12

  [2] How does HTTP caching work in browsers?
       Answered  |  Votes: 445  |  Answers: 8

  [3] Python dict caching vs functools.lru_cache
       Answered  |  Votes: 231  |  Answers: 5

  [n] Next page
  [s] New search
  [0] Quit

  Pick a number: 2

  ────────────────────────────────────────────────────────
  QUESTION DETAILS
  ────────────────────────────────────────────────────────
  ╒══════════╤══════════════════════════════════════════════╕
  │ Title    │ How does HTTP caching work in browsers?      │
  │ Votes    │ 445                                          │
  │ Answers  │ 8                                            │
  │ Answered │ Yes                                          │
  │ Views    │ 128,400                                      │
  │ Tags     │ http, caching, browser, web                  │
  ╘══════════╧══════════════════════════════════════════════╛

  TOP ANSWERS

  Answer #1 [Accepted]  |  Votes: 389  |  By: Jon Skeet
  ──────────────────────────────────────────────────────
  HTTP caching works by storing copies of responses...

  ────────────────────────────────────────────────────────
  READABILITY (Top Answer)
  ────────────────────────────────────────────────────────
  ╒══════════════════╤══════════╕
  │ Flesch Score     │ 61.2     │
  │ Grade Level      │ 10.4     │
  │ Word Count       │ 134      │
  │ Sentences        │ 7        │
  │ Difficulty       │ Medium   │
  ╘══════════════════╧══════════╛

  QR CODE
  Saved : How_does_HTTP_caching_qr.png
  URL   : https://stackoverflow.com/q/44541892

========================================================
  Done.
========================================================
```

---

## requirements.txt

```txt
python-dotenv
requests
qrcode[pil]
tabulate
textstat
```

---

## .env.example

```env
APP_NAME=CLI StackFlow Digest
VERSION=1.0.0
STACKOVERFLOW_KEY=your_key_here
```

---

## Troubleshooting

| Error | Reason | Solution |
|-------|--------|----------|
| `ModuleNotFoundError` | Package not installed | Run `pip install -r requirements.txt` |
| `PIL not found` | Pillow missing | Run `pip install pillow` |
| `ConnectionError` | No internet | Check your internet connection |
| `Timeout` | Request took too long | Try again; may be a temporary API issue |
| `API Error 502` | Key is invalid or missing | Check `STACKOVERFLOW_KEY` in your `.env` |
| No results found | Query too vague or specific | Try different keywords |

---

## Roadmap

### v1.0 (Current)
- [x] Stack Overflow question search
- [x] Top 3 answers with vote count and accepted status
- [x] Paginated results with new search option
- [x] Readability score for top answer
- [x] QR code generation

### v1.1 (Planned)
- [ ] Filter results by tag (e.g. `--tag python`)
- [ ] Save answer to `.txt` file
- [ ] Search history stored locally

### v2.0 (Future)
- [ ] Support other Stack Exchange sites (Server Fault, Super User)
- [ ] CLI flags support (`--tag`, `--no-qr`, `--page`)
- [ ] Colorized terminal output with `rich` library

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Mashruf Islam**
- GitHub: [@mashruf99](https://github.com/mashruf99)

---

> *"The best tool is the one you actually use."*