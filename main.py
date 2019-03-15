import argparse
import csv
import json

__author__ = "Noah Hummel"
parser = argparse.ArgumentParser(
    description="Convert xAPI-Probe xAPI statements to CSV"
)
parser.add_argument(
    "dump",
    type=str,
    help="JSON dump from the TLA facts store, one xAPI statement per line"
)

parser.add_argument(
    "out",
    type=str,
    help="Path of the CSV file which will be written by this script"
)

args = parser.parse_args()

with open(args.dump) as f:
    statements = [json.loads(line)["data"]["fact"]
                  for line in f.read().split("\n") if line]

answers = list(filter(
    lambda s: s["verb"]["id"] == "http://adlnet.gov/expapi/verbs/answered",
    statements
))

FIELD_NAMES = ["subject", "question_id", "dimension_id", "survey_id",
               "scale_start", "scale_end", "scale_step_size", "answer_value",
               "question_texts", "dimension_texts", "survey_texts"]

def to_csv_row(answer):
    subject = answer["actor"]["name"]
    question = answer["object"]
    dimension = answer["context"]["contextActivities"]["parent"][0]
    survey = answer["context"]["contextActivities"]["grouping"][0]

    question_texts = question["definition"]["name"]
    dimension_texts = dimension["definition"]["name"]
    survey_texts = survey["definition"]["name"]

    question_id = question["id"]
    dimension_id = dimension["id"]
    survey_id = survey["id"]

    score = answer["result"][0]["score"]
    scale_start = score["min"]
    scale_end = score["max"]
    scale_step_size = score["scaled"]
    answer_value = score["raw"]

    return {
        "subject": subject,
        "question_id":  question_id,
        "dimension_id": dimension_id,
        "survey_id": survey_id,
        "scale_start": scale_start,
        "scale_end": scale_end,
        "scale_step_size": scale_step_size,
        "answer_value": answer_value,
        "question_texts": question_texts,
        "dimension_texts": dimension_texts,
        "survey_texts": survey_texts
    }


with open(args.out, 'w+', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)

    writer.writeheader()
    for a in answers:
        writer.writerow(to_csv_row(a))
