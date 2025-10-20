import os
import random
from collections import defaultdict

from datasets import load_dataset, Dataset
import json

from jsonlines import jsonlines
from tqdm import tqdm

def print_30_random():
    # Load the dataset
    dataset = load_dataset("bclavie/msmarco-2m-triplets")["train"]

    # Slice the first 10,000 rows
    subset = dataset.select(range(10_000))

    # Randomly select 1000 rows
    select_n = 1000
    random.seed(42)  # For reproducibility 29 samples
    random.seed(56415)  # For reproducibility 6 additional samples
    sample_indices = random.sample(range(len(subset)), select_n)
    sampled_data = subset.select(sample_indices)

    # To view the sampled data
    nr_to_save = 6
    for i in range(select_n):
        if sampled_data[i]["positive"].isascii():
            print(json.dumps(sampled_data[i], ensure_ascii=False))
            # print(sampled_data[i]["positive"])

            nr_to_save -= 1
            if nr_to_save == 0:
                break


def load_queries(queries_path):
    queries = {}
    with open(queries_path, "r") as q_file:
        for line in tqdm(q_file, desc="Loading queries", unit="lines", total=808731):
            q_id, q = line.strip().split("\t")
            queries[int(q_id)] = q
    return queries


def load_collection(collection_path):
    collection = defaultdict(str)
    with open(collection_path, "r") as coll_file:
        for line in tqdm(coll_file, desc="Loading collection", unit="lines", total=8841823):
            p_id, d = line.strip().split("\t")
            collection[int(p_id)] = d
    return collection


def load_qrels(qrels_path):
    qrels = defaultdict(list)
    with open(qrels_path, "r") as qrels_file:
        for line in tqdm(qrels_file, desc="Loading qrels", unit="lines", total=8841823):
            q_id, _, p_id, _ = line.strip().split("\t")
            qrels[int(q_id)].append(int(p_id))
    return qrels


def flatten_qrels(qrels):
    """
    Flatten the qrels dictionary into a list of (qid, psgid) tuples.
    """
    datapoints = []
    for qid, psg_ids in qrels.items():
        for psgid in psg_ids:
            datapoints.append((qid, psgid))
    return datapoints


def write_pairs_to_annotate(id_to_write, annotator_id):
    # Build JSON objects for each datapoint
    def build_json(dp):
        qid, psgid = dp
        data = {
            "qid": qid,
            "psgid": psgid,
            "query": queries.get(qid, ""),
            "passage": collection.get(psgid, "")
        }
        return data

    all_jsons = [build_json(dp) for dp in id_to_write]

    base_dir = 'annotate_data'
    os.makedirs(base_dir, exist_ok=True)

    # Write all JSON objects to 'out.jsonl'
    full_path = os.path.join(base_dir, f'out_{annotator_id}.jsonl')
    with jsonlines.open(full_path, mode='w') as writer:
        writer.write_all(all_jsons)
    print(f"Output written to out.jsonl with {len(all_jsons)} items.")


def get_data_to_annotate(annotator_id):
    if len(all_datapoints) < 40:
        raise ValueError("Not enough datapoints in qrels to sample 40 items.")

    random.seed()  # get random seed from system time

    # Sample 40 random datapoints (without replacement)
    random_40 = random.sample(all_datapoints, 100)

    # Deterministically sample 20 as common part
    random.seed(42369565)  # Fixed seed for the common part to be the same
    common_part = random.sample(all_datapoints, 20)

    # Remove common part from random_40 to avoid duplicates and get first 40
    common_set = set(common_part)
    random_part = [dp for dp in random_40 if dp not in common_set][:40]

    all_ids = list(common_set) + list(random_part)

    write_pairs_to_annotate(all_ids, annotator_id)


def read_annotated(input_directory):
    """
    Reads what whas cerated by fce build_json()
    and creates list of qid psg id that are annotated once
    removes those that are annotated multiple times
    :return:
    """
    multi_annotations = set()
    exclude_ids = set()
    for file in os.listdir(input_directory):
        if not file.endswith(".jsonl"):
            continue

        full_path = os.path.join(input_directory, file)
        with jsonlines.open(full_path, mode='r') as reader:
            for obj in reader:
                pair = (obj['qid'], obj['psgid'])

                if pair in exclude_ids:
                    multi_annotations.add(pair)

                exclude_ids.add(pair)

    unique_annotations = exclude_ids - multi_annotations
    return unique_annotations, exclude_ids

# code to get 35 samples dataset from bclavie/msmarco-2m-triplets
# print_30_random()



# Paths
queries_path = "colbert_data/evaluation/queries.dev.small.tsv"
collection_path = "colbert_data/training/collection_fixed.tsv"
qrels_path = 'colbert_data/evaluation/qrels.dev.small.tsv'

# Load collections
collection = load_collection(collection_path)
queries = load_queries(queries_path)
all_datapoints = flatten_qrels(load_qrels(qrels_path))

# Exclude already annotated ids
old_annotated_path = 'annotate_data_out_old/'
annotated_once, exclude_ids = read_annotated(old_annotated_path)

# Create data for second annotation round
write_pairs_to_annotate(annotated_once, 'second_round')

all_datapoints = [dp for dp in all_datapoints if dp not in exclude_ids]
random.seed()

# Shuffle the remaining datapoints
random.shuffle(all_datapoints)


nr_annotators = 3
total_per_annotator = 120
for i in range(nr_annotators):
    # This was the way to generate shared for all annotators and random part for each annotator
    # get_data_to_annotate(i)

    # Now we instead assign total_per_annotator random samples to each annotator
    # and make sure that 50% are overlapping between each pair of annotators
    # also for the last annotator, we match the first annotator first half

    # E.g.
    # Annotator 0: 0-119
    # Annotator 1: 60-179
    # Annotator 2: 120-179 & 0-59

    start_index = (i * (total_per_annotator // 2)) % len(all_datapoints)
    if i == nr_annotators - 1:
        # last annotator
        end_index = start_index + total_per_annotator // 2
        shared_with_first = all_datapoints[0:(total_per_annotator // 2)]
        ids_to_write = shared_with_first + all_datapoints[start_index:end_index]
    else:
        end_index = start_index + total_per_annotator
        ids_to_write = all_datapoints[start_index:end_index]

    write_pairs_to_annotate(ids_to_write, i)
    print(f"Annotator {i} assigned samples from index"
          f" {start_index} to {end_index} (total {len(ids_to_write)})")

print("Done")



