import os
import re
import html
import requests
import qrcode
import textstat
from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()
APP_NAME = os.getenv("APP_NAME", "CLI StackFlow Digest")
VERSION  = os.getenv("VERSION", "1.0.0")
SO_KEY   = os.getenv("STACKOVERFLOW_KEY", "")

BASE_URL = "https://api.stackexchange.com/2.3"
HEADERS  = {"User-Agent": "CLIStackFlowDigest/1.0"}

CODE_WIDTH = 72


# ─────────────────────────────────────────
def print_banner():
    print("\n" + "=" * 56)
    print(f"  {APP_NAME} v{VERSION}")
    print("=" * 56 + "\n")


# ─────────────────────────────────────────
def parse_answer_body(raw_html):
    """
    Parse the HTML body into segments.
    Returns list of dicts: {"type": "text"|"code", "content": str}
    """
    segments = []

    parts = re.split(r"(<pre>.*?</pre>)", raw_html, flags=re.DOTALL)

    for part in parts:
        if part.startswith("<pre>"):
            code = re.sub(r"<pre>\s*<code[^>]*>", "", part, flags=re.DOTALL)
            code = re.sub(r"</code>\s*</pre>", "", code, flags=re.DOTALL)
            code = html.unescape(code).strip()
            if code:
                segments.append({"type": "code", "content": code})
        else:
            part = re.sub(r"<code>(.*?)</code>", r"`\1`", part, flags=re.DOTALL)
            part = re.sub(r"<li[^>]*>", "\n  • ", part)
            part = re.sub(r"<br\s*/?>", "\n", part, flags=re.IGNORECASE)
            part = re.sub(r"<p[^>]*>", "\n", part)
            part = re.sub(r"</p>", "", part)
            part = re.sub(r"<[^>]+>", "", part)
            part = html.unescape(part)
            part = re.sub(r"\n{3,}", "\n\n", part).strip()
            if part:
                segments.append({"type": "text", "content": part})

    return segments


def print_code_block(code):
    """Show the code block beautifully in a box."""
    lines = code.split("\n")
    border = "  +" + "-" * CODE_WIDTH + "+"
    print(border)
    for line in lines:
        while len(line) > CODE_WIDTH - 2:
            print(f"  | {line[:CODE_WIDTH - 2]} |")
            line = "  " + line[CODE_WIDTH - 2:]
        print(f"  | {line:<{CODE_WIDTH - 2}} |")
    print(border)


def print_answer_body(segments, max_text_chars=500):
    """Print the parsed segments — text normally, in a code box."""
    text_printed = 0

    for seg in segments:
        if seg["type"] == "text":
            content = seg["content"]
            remaining = max_text_chars - text_printed
            if remaining <= 0:
                break
            if len(content) > remaining:
                content = content[:remaining].rstrip() + "..."
            for line in content.split("\n"):
                print(f"  {line}")
            text_printed += len(seg["content"])
            print()

        elif seg["type"] == "code":
            print()
            print_code_block(seg["content"])
            print()


# ─────────────────────────────────────────
def clean_html(text):
    """Use this if you need plain text (title, table)."""
    text = re.sub(r"<code>(.*?)</code>", r"`\1`", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─────────────────────────────────────────
def search_questions(query, page=1):
    params = {
        "order":    "desc",
        "sort":     "relevance",
        "q":        query,
        "site":     "stackoverflow",
        "pagesize": 8,
        "page":     page,
        "filter":   "!nNPvSNdWme",
    }
    if SO_KEY:
        params["key"] = SO_KEY

    try:
        resp = requests.get(f"{BASE_URL}/search/advanced",
                            params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if "error_id" in data:
            print(f"\n  API Error {data['error_id']}: {data.get('error_message', '')}")
            return None

        return data.get("items", [])

    except requests.exceptions.ConnectionError:
        print("\n  Connection failed. Please check your internet.")
        return None
    except requests.exceptions.Timeout:
        print("\n  Request timed out. Try again.")
        return None
    except Exception as e:
        print(f"\n  Unexpected error: {e}")
        return None


# ─────────────────────────────────────────
def fetch_answers(question_id):
    params = {
        "order":    "desc",
        "sort":     "votes",
        "site":     "stackoverflow",
        "pagesize": 3,
        "filter":   "!nNPvSNdWme",
    }
    if SO_KEY:
        params["key"] = SO_KEY

    try:
        resp = requests.get(f"{BASE_URL}/questions/{question_id}/answers",
                            params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception:
        return []


# ─────────────────────────────────────────
def pick_question(query):
    page = 1
    while True:
        print(f'\n  Searching Stack Overflow for: "{query}"...\n')
        questions = search_questions(query, page=page)

        if questions is None:
            return None

        if not questions:
            print("  No results found. Please try a different query.")
            new_q = input("\n  Enter new search query (or press Enter to quit): ").strip()
            if not new_q:
                return None
            query = new_q
            page  = 1
            continue

        print(f"  Results (page {page}):\n")
        for i, q in enumerate(questions, 1):
            answered = "Answered" if q.get("is_answered") else "Unanswered"
            votes    = q.get("score", 0)
            answers  = q.get("answer_count", 0)
            title    = clean_html(q.get("title", ""))
            print(f"  [{i}] {title}")
            print(f"       {answered}  |  Votes: {votes}  |  Answers: {answers}\n")

        print("  [n] Next page")
        print("  [s] New search")
        print("  [0] Quit")

        choice = input("\n  Pick a number: ").strip().lower()

        if choice == "0":
            return None
        elif choice == "n":
            page += 1
        elif choice == "s":
            new_q = input("  Enter new search query: ").strip()
            if new_q:
                query = new_q
                page  = 1
        elif choice.isdigit() and 1 <= int(choice) <= len(questions):
            return questions[int(choice) - 1]
        else:
            print(f"  Please enter a number between 1 and {len(questions)}, or n/s/0.")


# ─────────────────────────────────────────
def readability_score(text):
    flesch = textstat.flesch_reading_ease(text)
    grade  = textstat.flesch_kincaid_grade(text)
    words  = textstat.lexicon_count(text)
    sents  = textstat.sentence_count(text)

    if flesch >= 70:   level = "Easy"
    elif flesch >= 50: level = "Medium"
    else:              level = "Hard"

    return {
        "Flesch Score": f"{flesch:.1f}",
        "Grade Level":  f"{grade:.1f}",
        "Word Count":   words,
        "Sentences":    sents,
        "Difficulty":   level,
    }


# ─────────────────────────────────────────
def display_table(data, headers=("Metric", "Value")):
    rows = [[k, v] for k, v in data.items()]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))


def display_question_table(q):
    tags     = ", ".join(q.get("tags", [])[:5])
    answered = "Yes" if q.get("is_answered") else "No"
    data = {
        "Title":    clean_html(q.get("title", "")),
        "Votes":    q.get("score", 0),
        "Answers":  q.get("answer_count", 0),
        "Answered": answered,
        "Views":    q.get("view_count", 0),
        "Tags":     tags,
        "Asked by": q.get("owner", {}).get("display_name", "Unknown"),
    }
    rows = [[k, v] for k, v in data.items()]
    print(tabulate(rows, headers=["Field", "Details"],
                   tablefmt="fancy_grid", maxcolwidths=[12, 58]))


# ─────────────────────────────────────────
def generate_qr(url, title):
    safe_name = re.sub(r"[^\w\s-]", "", title)[:50].strip().replace(" ", "_")
    filename  = f"{safe_name}_qr.png"
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename


# ─────────────────────────────────────────
def main():
    print_banner()

    if not SO_KEY:
        print("  Warning: STACKOVERFLOW_KEY not set in .env")
        print("  Running without key (300 requests/day limit)\n")

    query = input("  Search Stack Overflow: ").strip()
    if not query:
        print("  No query entered. Exiting.")
        return

    # ── 1. Pick a question ──
    question = pick_question(query)
    if not question:
        print("\n  Exiting.")
        return

    q_id  = question["question_id"]
    q_url = question.get("link", f"https://stackoverflow.com/q/{q_id}")

    # ── 2. Question details ──
    print("\n" + "─" * 56)
    print("  QUESTION DETAILS")
    print("─" * 56)
    display_question_table(question)

    # ── 3. Top answers ──
    print("\n" + "─" * 56)
    print("  TOP ANSWERS")
    print("─" * 56)
    answers = fetch_answers(q_id)

    if not answers:
        print("  No answers found for this question.")
    else:
        for i, ans in enumerate(answers, 1):
            raw_body = ans.get("body", "")
            votes    = ans.get("score", 0)
            owner    = ans.get("owner", {}).get("display_name", "Unknown")
            accepted = " [Accepted]" if ans.get("is_accepted") else ""

            print(f"\n  Answer #{i}{accepted}  |  Votes: {votes}  |  By: {owner}")
            print("  " + "─" * 52)

            segments = parse_answer_body(raw_body)
            print_answer_body(segments, max_text_chars=500)

    # ── 4. Readability of top answer ──
    if answers:
        top_plain = clean_html(answers[0].get("body", ""))
        if len(top_plain.split()) > 20:
            print("─" * 56)
            print("  READABILITY (Top Answer)")
            print("─" * 56)
            display_table(readability_score(top_plain))

    # ── 5. QR Code ──
    print("\n" + "─" * 56)
    print("  QR CODE")
    print("─" * 56)
    title   = clean_html(question.get("title", "question"))
    qr_file = generate_qr(q_url, title)
    print(f"  Saved : {qr_file}")
    print(f"  URL   : {q_url}")

    print("\n" + "=" * 56)
    print("  Done.")
    print("=" * 56 + "\n")


if __name__ == "__main__":
    main()