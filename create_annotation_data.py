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

    # Process common part and random part separately, so that common comes first
    common_jsons = [build_json(dp) for dp in common_part]
    random_jsons = [build_json(dp) for dp in random_part]
    all_jsons = common_jsons + random_jsons

    # Write all JSON objects to 'out.jsonl'
    with jsonlines.open(f'annotate_data/out_{annotator_id}.jsonl', mode='w') as writer:
        writer.write_all(all_jsons)

    print(f"Output written to out.jsonl with {len(all_jsons)} items.")



# code to get 35 samples dataset from bclavie/msmarco-2m-triplets
# print_30_random()

# Paths
queries_path = "colbert_data/evaluation/queries.dev.small.tsv"
collection_path = "colbert_data/training/collection.tsv"
qrels_path = 'colbert_data/evaluation/qrels.dev.small.tsv'

# Load collections
collection = load_collection(collection_path)
queries = load_queries(queries_path)
all_datapoints = flatten_qrels(load_qrels(qrels_path))


nr_annotators = 10
for i in range(nr_annotators):
    get_data_to_annotate(i)



