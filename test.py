test_cases = [

    # 2
    {
        "agent": "Do you want a short explanation or a detailed one?",
        "user": "short"
    },

    # 5
    {
        "agent": "Do you want to stop here?",
        "user": "no"
    },

    # 7
    {
        "agent": "That’s how rainbows form.",
        "user": "cool"
    },

    # 8
    {
        "agent": "I can explain it more simply.",
        "user": "explain"
    },

    # 10
    {
        "agent": "That’s the basic idea.",
        "user": "huh"
    },

    # 11
    {
        "agent": "Do you want another example?",
        "user": "maybe"
    },

    # 12
    {
        "agent": "Tell me if you want to stop.",
        "user": "bye"
    },

    # 14
    {
        "agent": "That’s all for now.",
        "user": "alright bye"
    },

    # 15
    {
        "agent": "Should I explain the math behind it?",
        "user": "no explain physics"
    },

    # 17
    {
        "agent": "Want a real-life example?",
        "user": "yes please"
    },

    # 20
    {
        "agent": "I can continue explaining.",
        "user": "hmm idk"
    },

    # 21
    {
        "agent": "Tell me what you prefer.",
        "user": "exit, now!"
    },
]

from API.modules.intent import detect_intents
from API.modules.expectation import detect_expectation

def intent_middleware(
    raw_text: str,
    intent: str,
    confidence: float,
    expectation: str = "NONE"
):
    """
    Final gate between user input and agent.
    This does NOT execute actions.
    It only reshapes or blocks input.
    """

    # Default response
    result = {
        "action": "PASS",
        "final_text": raw_text,
        "intent": intent,
        "confidence": confidence
    }

    # -------------------------
    # EXIT (strong only)
    # -------------------------
    if intent == "exit" and confidence >= 0.85:
        result["action"] = "EXIT"
        result["final_text"] = None
        return result

    # -------------------------
    # COMMAND MODE
    # -------------------------
    if intent == "command" and confidence >= 0.85:
        result["action"] = "COMMAND"
        result["final_text"] = raw_text
        return result

    # -------------------------
    # YES / NO EXPECTATION
    # -------------------------
    if expectation == "YES_NO":
        if intent == "passive" and confidence >= 0.7:
            result["final_text"] = "YES. " + raw_text
            return result

        if intent == "negative" and confidence >= 0.7:
            result["final_text"] = "NO. " + raw_text
            return result

    # -------------------------
    # CONFIRM EXIT (soft)
    # -------------------------
    if intent == "exit" and confidence >= 0.6:
            print("confirm first...")
            result["action"] = "INTENT"
            result["final_text"] = "YES. " + raw_text
            return result
    
    if expectation == "CONFIRM_EXIT":
        if intent == "exit" and confidence >= 0.6:
            result["final_text"] = "YES. " + raw_text
            return result

    # -------------------------
    # EMPTY / USELESS INPUT
    # -------------------------
    # if intent == "passive" and confidence < 0.5:
    #     result["action"] = "IGNORE"
    #     result["final_text"] = None
    #     return result

    # -------------------------
    # DEFAULT → PASS THROUGH
    # -------------------------
    return result








for i in test_cases:
    print(i)
    exp = detect_expectation(i["agent"])
    intent = detect_intents(i["user"],exp)
    #print(intent,exp)
    print(intent_middleware(i["user"],intent[1],intent[2],exp))
    print()  














'''
{'agent': 'Do you want to stop here?', 'user': 'no'} ({}, None, 0.0)
{'agent': 'Light bends differently in air.', 'user': 'okay continue'} ({}, None, 0.0)
{'agent': 'That’s how rainbows form.', 'user': 'cool'} ({}, None, 0.0)
{'agent': 'I can explain it more simply.', 'user': 'explain'} ({}, None, 0.0)
{'agent': 'Do you want another example?', 'user': 'maybe'} ({}, None, 0.0)
{'agent': 'Tell me if you want to stop.', 'user': 'bye'} ({}, None, 0.0)
'''