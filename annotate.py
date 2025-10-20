import os
import json
from jsonlines import jsonlines


def annotate_data():

    # Get index from user
    index = input("Enter the index of the dataset to annotate (0-2) (or 'second_round'): ")

    input_file = f"annotate_data/out_{index}.jsonl"
    output_file = f"annotate_data_out/out_{index}_explained.jsonl"

    os.makedirs('annotate_data_out', exist_ok=True)

    # Read current to get progress
    out_data = []
    if os.path.exists(output_file):
        with jsonlines.open(output_file, "r") as outfile:
            for d in outfile:
                out_data.append(d)

    current_line = len(out_data)

    in_data = []
    with jsonlines.open(input_file, "r") as infile:
        for d in infile:
            in_data.append(d)

    max_lines = len(in_data)



    for i, d in enumerate(in_data):

        # Skip already annotated lines
        if i < current_line:
            continue
        print()
        print()
        print(f"Progress: {i + 1} of {max_lines}")

        # Print the query and positive fields
        print(f"Query: {d['query']}")
        print(f"Text : {d['passage']}")

        print()

        # Wait for user input
        selected_spans = []
        while True:
            try:
                selected_span = input("Enter selected span: ")
                selected_spans.append(selected_span)

            except EOFError:
                print("[EOF received, ending input]")
                break

        # Print the selected spans
        print('Selected spans:')
        print("\n\t".join(selected_spans))
        d["selected_spans"] = selected_spans

        # Add the modified JSON object to the output list
        out_data.append(d)

        # Open the output file for writing
        with jsonlines.open(output_file, "w") as outfile:
            outfile.write_all(out_data)
        print("\n---\n")



print(
    """
    =========== START OF INSTRUCTIONS ===========

    You will be presented with a query and a passage. 
    Please extract the passage spans that are most relevant to the query.

    For illustration, imagine that you search for the query on Google
    and the passage is one of the results. 
    Which parts of the passage would you like to see highlighted (to get response/most relevant part faster)?
    
    A span must be comprehensive: removing the span from the text should make the text irrelevant to the query.
    A span must be plausible: a human reading only selected span should be convinced that the text is relevant.
    
    Let’s read both the passage and the query, and then carefully consider 
    the relevance of each part of the passage to the query.
    
    You may select multiple spans if needed, but ensure that the selected sections do not overlap. Try not to select entire sentences; prefer fine-grained spans.
    
    Usage:
    Select span using cursor, 
    [Ctrl + C] to copy selected span
    [Ctrl + V] to paste selected span
    [Enter] to submit pasted span and proceed to selection of another
    [Ctrl + D] to submit example and proceed to another example
    [Ctrl + C] to abort the program (restart app to discard progress on current example)
    
    =========== END OF INSTRUCTIONS ===========
    """
)


annotate_data()