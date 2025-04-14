import os
import json
from jsonlines import jsonlines


def annotate_data():

    # Get index from user
    index = input("Enter the index of the dataset to annotate (1-9) (or 'test' for testing data): ")

    input_file = f"annotate_data/out_{index}.jsonl"
    output_file = f"annotate_data_out/out_{index}_explained.jsonl"

    os.makedirs('annotate_data_out', exist_ok=True)

    # Read current to get progress
    out_data = []
    if os.path.exists(output_file):
        with jsonlines.open(output_file, "r") as outfile:
            for d in outfile:
                out_data.append(d)

    max_lines = 60
    current_line = len(out_data)

    in_data = []
    with jsonlines.open(input_file, "r") as infile:
        for d in infile:
            in_data.append(d)

    # Open the output file for writing
    with jsonlines.open(output_file, "w") as outfile:
        # Write the existing data to the output file -- if user interrupted before first write
        outfile.write_all(out_data)

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

            # Wait for user input
            selected_spans = []
            while True:
                try:
                    selected_span = input("Enter selected span: ")
                    selected_spans.append(selected_span)
                    outfile.write_all(out_data)
                except EOFError:
                    print(" [EOF received, ending input]")
                    break

            # Print the selected spans
            print('Selected spans:')
            print("\n\t".join(selected_spans))
            d["selected_spans"] = selected_spans

            # Add the modified JSON object to the output list
            out_data.append(d)
            print("\n---\n")



print("INSTRUCTIONS for LLM")
print(
    """
    You will be presented with a query and passage, please 
    extract passage spans which are most relevant to the query.

    Span must be comprehensive: removing the span from the text should make it irrelevant 
    to the query.
    Span must be plausible: human reading only this span should be convinced that text is relevant.   
    Let's read both passage and query, and then carefully consider
    relevance of each passage part to the query. 

    You may select multiple spans if needed, but ensure that the selected sections do not overlap. 
    Try not to select entire sentences, but only fine-grained spans.
    Do not correct or modify the text!
    Include all grammatical and syntactic errors from the original text, 
    do not remove senseless spaces or punctuation.

    Return only json_object with key 'spans' and list of selected spans 
    (text, start, end) as value. 
    \n
    Query: {query}
    Passage: {passage}
    """
)


print("INSTRUCTIONS for person")
print(
    """
    same as above, but:
    
    imagine that you google for the query and get the passage as a result
    
    What parts of the passage would you love to be highlighted (to get response/most relevant part faster)?
    
    
    =========== END OF INSTRUCTIONS ===========\n\n\n
    """
)


annotate_data()