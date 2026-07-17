import json
from minieval_pro import Evaluator
from minieval.database.db import init_db

init_db()
ev = Evaluator()

def faithfulness(source, fact):
    r = ev.score(question="Is this fact supported by what the user said?", context=source, answer=fact)
    return round(r.faithfulness.score, 2), r.faithfulness.label

def adjudicate(old_source, old_fact, new_source, new_fact):
    old_score, old_label = faithfulness(old_source, old_fact)
    new_score, new_label = faithfulness(new_source, new_fact)
    if new_label == "faithful" and new_score >= 0.5:
        verdict, reason = "ACCEPT", "New memory is faithful to its source — legitimate update."
    elif new_label == "contradicts":
        verdict, reason = "BLOCK", "New memory is a hallucination — protecting the true memory."
    else:
        verdict, reason = "REVIEW", "New memory is uncertain — not confident enough to overwrite."
    return {
        "old_fact": old_fact, "old_score": old_score,
        "new_fact": new_fact, "new_score": new_score,
        "new_label": new_label, "verdict": verdict, "reason": reason,
    }

cases = [
    adjudicate("I live in Bangalore.", "The user lives in Bangalore.",
               "I moved to Chennai last week.", "The user lives in Chennai."),
    adjudicate("I am allergic to peanuts.", "The user is allergic to peanuts.",
               "I had a great salad for lunch.", "The user loves eating peanuts."),
    adjudicate("I work as a nurse.", "The user is a nurse.",
               "I just finished medical school and now practice as a doctor.", "The user is a doctor."),
    adjudicate("I am vegetarian.", "The user is vegetarian.",
               "I enjoyed a nice pasta dish today.", "The user eats meat."),
]

with open("adjudication_log.json", "w") as f:
    json.dump(cases, f, indent=2)

for c in cases:
    print(f"{c['verdict']:7} | old: {c['old_fact']} ({c['old_score']}) | new: {c['new_fact']} ({c['new_score']})")
print("\nSaved to adjudication_log.json")
