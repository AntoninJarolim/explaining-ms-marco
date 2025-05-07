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
        "q_text": "je venca gey",
        "extraction": "venca je giga teplej",
        "source": "dummy"
    }
    data.insert(0, training_example)

    print(
    """
    You will read a query and a text.
    Your task is to decide whether the text contains the information asked in the query.
    Note, that 'empty text' is not relevant to the query.
    """
    )
    print("READY?")
    print("Just type 'yep' when you're ready.")
    while input().strip().lower() != "yep":
        print("Just type 'yep' when you're ready.")

    annotations = []

    for i, example in enumerate(data):
        if i == 0:
            print("\n--- TRAINING EXAMPLE ---")

        print(f"\n--- {i}/30 ---" if i > 0 else "\n--- Training ---")
        print("Query:\n", example["q_text"])
        print("Text:\n", example["extraction"])
        print("\nYou should hit 'y' or 'n' now.")

        start_time = time.time()
        while True:
            decision = input().strip().lower()
            if decision in {"y", "n"}:
                break
        elapsed = time.time() - start_time

        if decision == "n" and i == 0:
            print("zjevne si nepochopil task, prosim kontaktuj me.")
            exit(1)

        if i > 0:
            annotations.append({
                "q_id": example["q_id"],
                "psg_id": example["psg_id"],
                "q_text": example["q_text"],
                "extraction": example["extraction"],
                "decision": decision,
                "time_sec": round(elapsed, 2)
            })

        if i == 8:
            print("\n\n\n")
            print("BREAK TIME")
            print("doufám, že to není nejnudnější věc cos dnes dělal!")
            print("Just type 'je' when you're ready.")
            while input().strip().lower() != "je":
                print("Just type 'je' when you're ready.")

        elif i == 16:
            print("\n\n\n")
            print("hej, heey heyyyy, yooooo, dej si pauzičku a pak lock in! thx")
            print("Just type 'locked in baby' when you're ready.")
            while input().strip().lower() != "locked in baby":
                print("Just type 'locked in baby' when you're ready.")

        elif i == 25:
            print("\n\n\n")
            print("BREAK TIME")
            print("díky za to, fakt, dlužím ti sušenku.")
            print("Just type 'fest' when you're ready.")
            while input().strip().lower() != "fest":
                print("Just type 'fest' when you're ready.")

        # Save the annotations to a file
        out_dir = "annotated"
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        dataset_path = Path(out_dir) / f"{annotator_id}_annotator.jsonl"
        with open(dataset_path, "w", encoding="utf-8") as f:
            for annotation in annotations:
                f.write(json.dumps(annotation) + "\n")

        print("\n\n\n")
    print("\nTHAT'S IT, THANX A LOT ❤️")

    # Optionally return the annotations for saving later
    return annotations, annotator_id


if __name__ == "__main__":
    run_annotation_session()
