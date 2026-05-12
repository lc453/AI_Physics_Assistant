import os
from koboldapi import KoboldAPICore, ChunkingProcessor
import requests
import json
from sympy_calculator import safe_calculator
from arxiv_search import search_query
from arxiv_search import extract_paper
import datetime

#BASE_URL = "http://localhost:5001"
BASE_URL = "http://192.168.68.154:5001"
# get the model from the url
response = requests.get(f"{BASE_URL}/v1/models")
modelname = response.json()["data"][0]["id"]

SYSTEM_PROMPT = """

You can:
1: Answer questions directly
2: Use a calculator when needed
3: Perform an arXiv search

Each response should contain exactly one reasoning step, and use no more than one tool.
Any reasoning should be done before the tool use, such as
<Reasoning>
ACTION: <tool>
INPUT: <params>
For the tool API to work, the last line of the response MUST be the input parameters, otherwise an error will occur.
To ensure relevant results, always default to looking up relevant materials before answering for advanced topics.

For each of the below tools, respond EXACTLY in the given format:
# calculator
ACTION: calculator
INPUT: <sympy expression>
# arXiv search
ACTION: arXiv
INPUT: <arXiv search terms>

Otherwise, respond:
FINAL ANSWER: <your answer>
"""

# Main loop for the agent
def run_agent(user_input: str):
    messages = [
        {"role": "system", "content": f"Request Time: {datetime.datetime.now()}"},
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "The surface area of an infinitely short cylinder is given by twice the area of the circle of the given radius.\n\n ACTION: calculator\nINPUT: 2*pi*3.5^2"},
        {"role": "assistant", "content": "Let's search for papers related to 2D materials and quantum computing.\n\n ACTION: arXiv\nINPUT: qubit 2D materials OR quantum computing graphene"},
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
        #print(response)
        reply = response.json().get("choices", [{}])[0].get("message",{}).get("content", "No response")
        print("Agent:", reply)

        # Decision Point
        if 'ACTION:' in reply:
            # calculator tool
            if "calculator" in reply:
                expr = reply.split("INPUT:")[-1].strip()
                #print(expr)
                result = safe_calculator("evaluate", expr)

                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "system", "content": f"OBSERVATION: {result}"})
            if ("arXiv" or "arxiv") in reply:
                query = reply.split("INPUT:")[-1].strip()
                # Removing special symbols that might interfere with the arXiv search
                query = query.translate(str.maketrans('','','\"\'()[]\{\}'))
                #print(query)
                max_results = 5
                results = search_query(query)
                if len(results)==0:
                    messages.append({"role": "assistant", "content": reply})
                    messages.append({"role": "system", "content": f"SEARCH RESULTS: none. Refine search parameters."})
                else:
                    for result in results[:max_results]:
                        papermessages = [
                            {"role": "system", "content": extract_paper(result["link"])},
                            {"role": "system", "content": f"In three sentences, summarize the information from the above passage that pertains to the request: {user_input}.\nDo not use markdown."}
                        ]
                        paperpayload = {
                            "model": modelname,
                            "messages": papermessages,
                            "max_tokens": 128,
                            "temperature": 0.8
                        }
                        paperresponse = requests.post(f"{BASE_URL}/v1/chat/completions", json=paperpayload)
                        summary = paperresponse.json().get("choices", [{}])[0].get("message",{}).get("content", "No summary")
                        result["summary"] = summary
                    messages.append({"role": "assistant", "content": reply})
                    messages.append({"role": "system", "content": f"SEARCH RESULTS: {results[:max_results]}"})
                
        else:
            messages.append({"role": "assistant", "content": reply})
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

    