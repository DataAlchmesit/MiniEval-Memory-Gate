import time, json, datetime
from supermemory import Supermemory
from minieval_pro import Evaluator
from minieval.database.db import init_db

import os
API_KEY = os.getenv("SUPERMEMORY_API_KEY", "AQ.YOUR_KEY_HERE")
client = Supermemory(api_key=API_KEY, base_url="http://localhost:6767")

init_db()
ev = Evaluator()
STORE_THRESHOLD = 0.5

def gate(source, fact):
    r = ev.score(question="Is this fact supported by what the user said?", context=source, answer=fact)
    faith = r.faithfulness.score
    label = r.faithfulness.label
    if label == "faithful" and faith >= STORE_THRESHOLD:
        return "STORE", faith, label
    elif label == "contradicts":
        return "REJECT", faith, label
    else:
        return "REVIEW", faith, label

def run(conversation, tag):
    print("CONVERSATION:", conversation)
    client.documents.add(content=conversation, container_tag=tag)
    print("Sent. Polling for extraction (up to 2 min)...")
    res = None
    for attempt in range(24):
        time.sleep(5)
        res = client.search.memories(q="Delhi Bangalore peanuts allergy moved lives", container_tag=tag)
        if len(res.results) > 0:
            print("  extracted after", (attempt+1)*5, "seconds")
            break
    if not res or len(res.results) == 0:
        print("No memories found after 2 min.")
        return
    print("\nMemories extracted:", len(res.results))
    counts = {"STORE":0, "REJECT":0, "REVIEW":0}
    log = []
    for item in res.results:
        fact = item.memory
        decision, faith, label = gate(conversation, fact)
        counts[decision] += 1
        print("\n  Fact:    ", fact)
        print("  Faith:   ", round(faith,2), "(" + label + ")")
        print("  Decision:", decision)
        log.append({"time": str(datetime.datetime.now()), "source": conversation, "fact": fact, "faith": round(faith,3), "label": label, "decision": decision})
    with open("gate_audit_log.json", "a") as f:
        for e in log:
            f.write(json.dumps(e) + "\n")
    print("\n--- SUMMARY ---")
    print("STORE:", counts["STORE"], "| REJECT:", counts["REJECT"], "| REVIEW:", counts["REVIEW"])

if __name__ == "__main__":
    run("I moved from Delhi to Bangalore last month. I am allergic to peanuts.", "user_run7")
