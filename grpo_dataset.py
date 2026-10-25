import pandas as pd
from datasets import Dataset
from data_generation import *
from dataset_generation import DATASET_2, DATASET_3, DATASET_4

OUTPUTS = 33
RULES = open("eclipse_battle_rules_simplified.txt", "r").read()

INSTRUCTION = "Your goal is to predict outcomes of battles in the boardgame Eclipse.\n"\
    + RULES\
    + "Reply in exactly this format: <think>short reasoning</think><answer>probability between 0 and 1</answer>"

def to_rows(path, n=None, seed=0):
    df = pd.read_csv(path, header=None)
    if n:
        df = df.sample(min(n, len(df)), random_state=seed)
    X = df.iloc[:, 1:-OUTPUTS].values   # skip signature, skip 33 outputs
    y = df.iloc[:, -OUTPUTS].values     # attacker win chance
    return [
        {
            "prompt": [
                {"role": "system", "content": INSTRUCTION},
                {"role": "user", "content": vectorToBattle([int(v) for v in x]).toString()},
            ],
            "truth": float(t),
        }
        for x, t in zip(X, y)
    ]

if __name__ == "__main__":
    train = to_rows(DATASET_2, 3000) + to_rows(DATASET_3, 3000)
    test = to_rows(DATASET_4, 1000)
    Dataset.from_list(train).shuffle(seed=0).save_to_disk("datasets/grpo_train")
    Dataset.from_list(test).save_to_disk("datasets/grpo_test")
    print(len(train), len(test))
    print(train[0]["prompt"][1]["content"], "->", train[0]["truth"])