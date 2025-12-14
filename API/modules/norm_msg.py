def normalize_user_input(text: str):
    text = text.strip()
    lower = text.lower()

    # 3. Passive signals (keep talking)
    passive_words = {
        "hmm", "hm", "okay", "ok", "oh", "yes", "yeah"
    }
    if lower in passive_words:
        return text + ". Please continue explaining."

    # 4. Very short factual answers (place, name, number)
    words = text.split()
    if len(words) <= 2 and "?" not in text:
        # treat as contextual info, not a stop
        return text + ". Continue."

    # 5. Normal input
    return text
