import numpy as np
import pandas as pd
from pathlib import Path
import pickle

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def calc_tokens(text, token_rate=0.0001):
    tok = len(''.join(text)) / 4
    print(f"Embedding roughly {tok} tokens at rate of ${token_rate} per token...")
    print(f" ~ ${tok * token_rate}")

def str2float_list(str_list):
    return [float(e) for e in str_list.strip("[]").split(",")]

def load_class_embeddings(filepaths, agg_mthd="mean"):
    """If multiple filepaths, label embeddings from the different files
    are combined using `agg_mthd`.
    """
    if not isinstance(filepaths, list):
        filepaths = [filepaths]
    if agg_mthd == "mean":
        div = len(filepaths)
    elif agg_mthd == "sum":
        div = 1
    else:
        raise ValueError("agg_mthd: Argument must be 'sum' or 'mean'")
    lab_embs = None
    for fp in filepaths:
        with open(fp, "rb") as f:
            x = pickle.load(f)
            if lab_embs is None:
                lab_embs = {k : np.array(v) / div for k, v in x.items()}
            else:
                for k in lab_embs.keys():
                    lab_embs[k] += np.array(x[k]) / div
    return lab_embs


def cos_sim_match(txt_emb, lab_embs):
    """Compare a text embedding with all label embeddings, and classify the
    text based on the highest cosine similarity.

    txt_emb - a single list containing the embedding for some text
    lab_embs - a dict of {class-name: embeddings}
    """
    labels = list(lab_embs.keys())
    sims = np.zeros(shape=(len(labels)))
    for i, lab in enumerate(labels):
        sims[i] = cosine_similarity(txt_emb, lab_embs[lab] )
    highest = np.argmax(sims)
    return labels[highest], sims[highest]


if __name__ == "__main__":

    # cli args
    data_fp = "analysis/data/aug_2023_w_emb.csv"
    emb_col = "descr_emb"
    delim = "|"
    labs_fp = ["analysis/data/labels_nl_descr_simple_2023-08-27.pkl",
               "analysis/data/labels_kw_list_2023-08-27.pkl",
               "analysis/data/labs_only_2023-08-27.pkl"]
    out_dir = "analysis/data"

    # output path
    base = Path(data_fp).name.split(".")[0]
    out = Path(out_dir) / f"{base}_classd.csv"

    # load data and prep embeddings
    dat = pd.read_csv(data_fp, sep=delim)
    dat[emb_col] = dat[emb_col].apply(str2float_list)

    # load class embeddings
    lab_embs = load_class_embeddings(labs_fp, agg_mthd="sum")

    # MATCH TEXT EMBEDDINGS TO LABEL WITH HIGHEST COSINE SIM
    print("matching data embeddings with class embeddings...")
    dat["label"], dat["cos_sim"] = zip(
        *dat[emb_col].apply(lambda x: cos_sim_match(txt_emb=x, lab_embs=lab_embs))
    )

    # save
    dat.drop(labels=emb_col, axis=1, inplace=True)
    dat.to_csv(
        out, sep=delim, index=False
    )
    print(f"Saved {out}")