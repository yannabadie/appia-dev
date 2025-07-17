import json
import os

import numpy as np
from textblob import TextBlob


class JarvisAI:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE")
        self.gcp_sa_json = json.loads(os.getenv("GCP_SA_JSON", "{}"))
        self.llms = ["gpt-3.5-turbo", "claude-v1", "palm-2"]
        self.memory = {}

    def sentiment_analysis(self, text):
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def quantum_inspired_decision(self, options, sentiment):
        probs = np.abs(np.random.normal(size=len(options))) ** 2
        probs /= probs.sum()
        if sentiment > 0.5:
            probs = np.flip(probs)
        return np.random.choice(options, p=probs)

    def route_llm(self, query):
        sentiment = self.sentiment_analysis(query)
        selected_llm = self.quantum_inspired_decision(self.llms, sentiment)
        response = f"Routing to {selected_llm} with sentiment {sentiment:.2f}"
        self.memory[query] = response
        return response

    def self_improve(self):
        if len(self.memory) > 10:
            avg_sentiment = np.mean([self.sentiment_analysis(q) for q in self.memory])
            if avg_sentiment < 0:
                self.llms.append("new-optimistic-llm")
        return len(self.memory)


if __name__ == "__main__":
    ai = JarvisAI()
    queries = ["Hello, how are you?", "This is frustrating!", "Exciting news!"]
    for q in queries:
        print(ai.route_llm(q))
    print(f"Memory size after improvement: {ai.self_improve()}")
