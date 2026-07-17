from minieval_pro import Evaluator
from minieval.database.db import init_db

init_db()
ev = Evaluator()

def faithfulness(source, fact):
    r = ev.score(question="Is this fact supported by what the user said?", context=source, answer=fact)
    return r.faithfulness.score, r.faithfulness.label

def adjudicate(old_source, old_fact, new_source, new_fact):
    """
    When a new memory would overwrite an old one, decide by faithfulness.
    Returns which memory to keep.
    """
    old_score, old_label = faithfulness(old_source, old_fact)
    new_score, new_label = faithfulness(new_source, new_fact)

    print(f"\n{'='*60}")
    print(f"  CONFLICT — new memory wants to overwrite old memory")
    print(f"{'='*60}")
    print(f"  OLD: '{old_fact}'")
    print(f"       source: '{old_source}'")
    print(f"       faithfulness: {old_score:.2f} ({old_label})")
    print(f"  NEW: '{new_fact}'")
    print(f"       source: '{new_source}'")
    print(f"       faithfulness: {new_score:.2f} ({new_label})")

    if new_label == "faithful" and new_score >= 0.5:
        print(f"\n  DECISION: Accept overwrite. New memory is faithful to its source — legitimate update.")
        return "new"
    elif new_label == "contradicts":
        print(f"\n  DECISION: BLOCK overwrite. New memory is a hallucination.")
        print(f"  >> Supermemory alone would have overwritten a TRUE memory with a FALSE one.")
        return "old"
    else:
        print(f"\n  DECISION: FLAG for review. New memory is uncertain — not confident enough to overwrite.")
        return "review"

if __name__ == "__main__":
    # Case 1: legitimate update — user genuinely moved (new is faithful)
    print("\n### CASE 1: Legitimate update (user actually moved) ###")
    adjudicate(
        old_source="I live in Bangalore.",
        old_fact="The user lives in Bangalore.",
        new_source="I moved to Chennai last week.",
        new_fact="The user lives in Chennai.",
    )

    # Case 2: DANGEROUS — new memory is a hallucination trying to overwrite truth
    print("\n\n### CASE 2: Hallucinated overwrite (MiniEval protects the truth) ###")
    adjudicate(
        old_source="I am allergic to peanuts.",
        old_fact="The user is allergic to peanuts.",
        new_source="I had a great salad for lunch.",
        new_fact="The user loves eating peanuts.",
    )
