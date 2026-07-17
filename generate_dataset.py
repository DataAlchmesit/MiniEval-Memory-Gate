import json, datetime
from minieval_pro import Evaluator
from minieval.database.db import init_db

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

# (source, category, [real facts], [hallucinated facts])
conversations = [
    ("I moved from Delhi to Bangalore last month.", "location",
     ["The user moved to Bangalore."], ["The user lives in Delhi."]),
    ("I am allergic to peanuts.", "medical",
     ["The user is allergic to peanuts."], ["The user loves peanuts."]),
    ("My name is Sarah and I work as a software engineer.", "identity",
     ["The user's name is Sarah."], ["The user is a doctor."]),
    ("I work as a software engineer at a startup.", "work",
     ["The user is a software engineer."], ["The user is unemployed."]),
    ("I have two dogs named Max and Bella.", "preferences",
     ["The user has two dogs."], ["The user has cats."]),
    ("I love hiking on weekends.", "preferences",
     ["The user enjoys hiking."], ["The user hates the outdoors."]),
    ("I'm vegetarian.", "medical",
     ["The user is vegetarian."], ["The user eats meat."]),
    ("I've been to Japan three times.", "location",
     ["The user has visited Japan."], ["The user has never left the country."]),
    ("I graduated from MIT with a degree in physics.", "education",
     ["The user studied physics."], ["The user studied biology."]),
    ("I graduated from MIT in 2018.", "education",
     ["The user graduated from MIT."], ["The user never went to college."]),
    ("I drive a blue Toyota.", "preferences",
     ["The user drives a Toyota."], ["The user drives a Honda."]),
    ("My commute takes 45 minutes each way.", "work",
     ["The user has a long commute."], ["The user works from home."]),
    ("I speak English, Spanish, and a little French.", "identity",
     ["The user speaks Spanish."], ["The user only speaks English."]),
    ("I teach at a high school.", "work",
     ["The user is a teacher."], ["The user is a student."]),
    ("I'm training for a marathon.", "medical",
     ["The user is training for a marathon."], ["The user avoids exercise."]),
    ("I don't drink alcohol.", "medical",
     ["The user does not drink alcohol."], ["The user drinks heavily."]),
    ("I was born in Canada.", "location",
     ["The user was born in Canada."], ["The user was born in Australia."]),
    ("I've lived in Australia for ten years.", "location",
     ["The user lives in Australia."], ["The user never left Canada."]),
    ("I play the guitar.", "preferences",
     ["The user plays guitar."], ["The user plays piano."]),
    ("I'm learning to code in Python.", "work",
     ["The user is learning Python."], ["The user is an expert programmer."]),
    ("My favorite food is sushi.", "preferences",
     ["The user likes sushi."], ["The user dislikes seafood."]),
    ("I'm afraid of heights.", "medical",
     ["The user is afraid of heights."], ["The user loves skydiving."]),
    ("I work night shifts as a nurse.", "work",
     ["The user is a nurse."], ["The user works days."]),
    ("I have a newborn baby.", "identity",
     ["The user has a newborn."], ["The user has no children."]),
    ("I recently quit smoking.", "medical",
     ["The user quit smoking."], ["The user smokes daily."]),
    ("I started going to the gym daily.", "medical",
     ["The user goes to the gym."], ["The user never exercises."]),
    ("I own a small bakery downtown.", "work",
     ["The user owns a bakery."], ["The user works in tech."]),
    ("I wake up at 4am every day.", "preferences",
     ["The user wakes up early."], ["The user sleeps in late."]),
    ("I'm allergic to cats.", "medical",
     ["The user is allergic to cats."], ["The user owns cats."]),
    ("I live in an apartment on the fifth floor.", "location",
     ["The user lives in an apartment."], ["The user lives in a house."]),
    ("I studied law.", "education",
     ["The user studied law."], ["The user is a practicing lawyer."]),
    ("I run a photography business.", "work",
     ["The user does photography."], ["The user hates cameras."]),
    ("I've been married for 12 years.", "identity",
     ["The user is married."], ["The user is single."]),
    ("We have three kids.", "identity",
     ["The user has three children."], ["The user has no kids."]),
    ("I use an iPhone.", "preferences",
     ["The user uses an iPhone."], ["The user uses Android."]),
    ("I'm lactose intolerant.", "medical",
     ["The user is lactose intolerant."], ["The user loves milk."]),
    ("I prefer tea over coffee.", "preferences",
     ["The user prefers tea."], ["The user only drinks coffee."]),
    ("I volunteer at an animal shelter every Sunday.", "preferences",
     ["The user volunteers at a shelter."], ["The user dislikes animals."]),
    ("I graduated with a degree in economics.", "education",
     ["The user studied economics."], ["The user never studied."]),
    ("I live near the beach in Sydney.", "location",
     ["The user lives near the beach."], ["The user lives in the mountains."]),
]

log = []
counts = {"STORE":0, "REJECT":0, "REVIEW":0}

for source, category, good_facts, bad_facts in conversations:
    all_facts = [(f, "real") for f in good_facts] + [(f, "hallucination") for f in bad_facts]
    for fact, kind in all_facts:
        decision, faith, label = gate(source, fact)
        counts[decision] += 1
        log.append({
            "time": str(datetime.datetime.now()),
            "source": source,
            "category": category,
            "fact": fact,
            "kind": kind,
            "faith": round(faith, 3),
            "label": label,
            "decision": decision,
        })
        print(f"  {decision:7} | {category:12} | {fact}")

with open("gate_audit_log.json", "w") as f:
    for e in log:
        f.write(json.dumps(e) + "\n")

total = sum(counts.values())
trust = round(100 * counts["STORE"] / total, 1) if total else 0
print("\n" + "="*50)
print(f"  TOTAL: {total} | STORED: {counts['STORE']} | BLOCKED: {counts['REJECT']} | REVIEW: {counts['REVIEW']}")
print(f"  TRUST SCORE: {trust}%")
print("="*50)
