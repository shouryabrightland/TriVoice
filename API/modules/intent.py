import re
from typing import Literal

Intent = Literal[
    "EXIT",
    "COMMAND_MODE",
    "PASSIVE",
    "STORY",
    "QUERY",
    "UNKNOWN"
]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_intent(raw_text: str) -> Intent:
    text = normalize(raw_text)
    words = text.split()

    if not words:
        return "UNKNOWN"

    # -------------------------------------------------
    # 1. EXIT intent (HIGHEST PRIORITY)
    # -------------------------------------------------
    exit_tokens = {
        "bye", "goodbye", "exit", "quit", "leave"
    }

    exit_phrases = {
        "go away",
        "shut up",
        "fuck off"
    }

    if any(word in exit_tokens for word in words):
        return "EXIT"

    if any(phrase == text for phrase in exit_phrases):
        return "EXIT"

    # -------------------------------------------------
    # 2. COMMAND MODE (Try / Tri / Tie Command)
    # -------------------------------------------------
    primary = {"try", "tri", "tie", "tray", "dry"}
    secondary = {"command", "commands", "commend", "comand"}

    found_primary = any(word in primary for word in words)
    found_secondary = any(word in secondary for word in words)

    if found_primary and found_secondary:
        return "COMMAND_MODE"

    # -------------------------------------------------
    # 3. PASSIVE / CONTINUE
    # -------------------------------------------------
    passive_tokens = {
        "hmm", "hm", "ok", "okay", "yes",
        "yeah", "alright", "sure"
    }

    if len(words) <= 2 and all(word in passive_tokens for word in words):
        return "PASSIVE"

    # -------------------------------------------------
    # 4. QUERY (questions)
    # -------------------------------------------------
    question_starters = {
        "why", "how", "what", "when", "where", "who"
    }

    if "?" in raw_text:
        return "QUERY"

    if words[0] in question_starters:
        return "QUERY"

    # -------------------------------------------------
    # 5. STORY / STATEMENT
    # -------------------------------------------------
    if len(words) >= 6:
        return "STORY"

    # -------------------------------------------------
    # 6. FALLBACK
    # -------------------------------------------------
    return "UNKNOWN"
