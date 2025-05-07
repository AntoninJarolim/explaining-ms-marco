import json
import random
import time
from pathlib import Path

def run_annotation_session(dataset_dir="data/accuracy_dataset/to_annotate"):
    # Prompt for annotator ID
    while True:
        try:
            annotator_id = int(input("Enter your annotator ID (1–5): "))
            if annotator_id in {1, 2, 3, 4, 5}:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a number between 1 and 5.")

    dataset_path = Path(dataset_dir) / f"{annotator_id}_annotator.jsonl"
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    random.seed(42)
    random.shuffle(data)

    # Add a dummy example to the beginning
    training_example = {
        "q_id": "train_0",
        "psg_id": "train_0",
        "query": "je venca gey",
        "extraction": "venca je giga teplej",
        "source": "dummy"
    }
    data.insert(0, training_example)

    print("""
You will read a query and a text.
Your task is to decide whether the text is relevant to the query.
""")
    print("READY?")
    while input().strip().lower() != "yep":
        print("Just type 'yep' when you're ready.")

    annotations = []
    start_time = time.time()

    for i, example in enumerate(data):
        if i == 0:
            print("\n--- TRAINING EXAMPLE ---")

        print(f"\n--- {i}/30 ---" if i > 0 else "\n--- Training ---")
        print("Query:\n", example["query"])
        print("Extraction:\n", example["extraction"])
        print("\nYou should hit 'y' or 'n' now.")

        while True:
            decision = input().strip().lower()
            if decision in {"y", "n"}:
                break

        elapsed = time.time() - start_time
        start_time = time.time()

        if i > 0:
            annotations.append({
                "q_id": example["q_id"],
                "psg_id": example["psg_id"],
                "query": example["query"],
                "extraction": example["extraction"],
                "decision": decision,
                "time_sec": round(elapsed, 2)
            })

        if i == 8:
            print("doufám, že to není nejnudnější věc co dnes děláš!")
            input("(hit anything to continue)")
        elif i == 16:
            print("hej, dej si pauzičku a pak lock in!")
            input("(hit anything to continue)")
        elif i == 25:
            print("díky za to, fakt, dlužím ti sušenku.")
            input("(hit anything to continue)")

    print("\nTHANKS A LOT ❤️")

    # Optionally return the annotations for saving later
    return annotations, annotator_id


if __name__ == "__main__":
    # Run the annotation session
    annotations, annotator_id = run_annotation_session()

    # Save the annotations to a file
    out_dir = "data/accuracy_dataset/annotated"
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    dataset_path = Path(out_dir) / f"{annotator_id}_annotator.jsonl"
    with open(dataset_path, "a", encoding="utf-8") as f:
        for annotation in annotations:
            f.write(json.dumps(annotation) + "\n")
