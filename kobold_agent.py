import os
from koboldapi import KoboldAPICore, ChunkingProcessor
import requests
from tools import safe_calculator
import json

BASE_URL = "http://localhost:5001"
# get the model from the url
response = requests.get(f"{BASE_URL}/v1/models")
modelname = response.json()["data"][0]["id"]

SYSTEM_PROMPT = """
You are a physics research assistant.

You can:
1: Answer questions directly
2: Use a calculator when needed

When using a tool, respond EXACTLY in this format:

ACTION: <tool name>
INPUT: <expression>

Otherwise, respond:
FINAL ANSWER: <your answer>
available tools: 'calculator'
"""

# Main loop for the agent
def run_agent(user_input: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    for _ in range(5): # limit to 5 iterations to prevent infinite loops
        # Create payload to send to the API
        payload = {
            "model": modelname,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.8
        }

        response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload)
        print(response)
        reply = response.json().get("choices", [{}])[0].get("message",{}).get("content", "No response")
        print("Agent:", reply)

        # Decision Point
        if 'ACTION:' in reply:
            # calculator tool
            if "calculator" in reply:
                expr = reply.split("INPUT:")[-1].strip()
                print(expr)
                result = safe_calculator("evaluate", expr)

                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"OBSERVATION: {result}"})
        else:
            # Check the working directory for history jsonl file, then save history for debugging purposes
            filename = "HISTORY"
            if os.path.exists(f"{filename}.jsonl"):
                index = 1
                while os.path.exists(f"{filename}{index}.jsonl"):
                    index += 1
                with open(f"{filename}{index}.jsonl", 'w', encoding='utf-8') as outfile:
                    for message in messages:
                        json.dump(message, outfile)
                        outfile.write('\n')
            else:
                with open(f"{filename}.jsonl", 'w', encoding='utf-8') as outfile:
                    for message in messages:
                        json.dump(message, outfile)
                        outfile.write('\n')
            return reply
        
    # Check the working directory for history jsonl file, then save history for debugging purposes
    filename = "HISTORY"
    if os.path.exists(f"{filename}.jsonl"):
        index = 1
        while os.path.exists(f"{filename}{index}.jsonl"):
            index += 1
        with open(f"{filename}{index}.jsonl", 'w', encoding='utf-8') as outfile:
            for message in messages:
                json.dump(message, outfile)
                outfile.write('\n')
    else:
        with open(f"{filename}.jsonl", 'w', encoding='utf-8') as outfile:
            for message in messages:
                json.dump(message, outfile)
                outfile.write('\n')

    