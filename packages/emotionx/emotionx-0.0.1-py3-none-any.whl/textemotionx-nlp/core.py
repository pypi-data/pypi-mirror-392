def analyze_emotion(text: str) -> str:
    text = text.lower()

    emotions = {
        "happy": ["happy", "glad", "joy", "awesome", "great"],
        "sad": ["sad", "down", "unhappy", "depressed"],
        "angry": ["angry", "mad", "furious", "annoyed"],
        "fear": ["scared", "afraid", "fear", "terrified"],
    }

    for emotion, keywords in emotions.items():
        for kw in keywords:
            if kw in text:
                return emotion

    return "neutral"
