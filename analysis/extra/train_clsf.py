from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def str2float_list(str_list):
    return [float(e) for e in str_list.strip("[]").split(",")]


if __name__=="__main__":
    data_fp = "analysis/data/labeled_spend_01-08_2023_w_emb.txt"
    emb_col = "descr_emb"
    lab_col = "label"
    delim = "|"
    out_dir = "analysis/data"

    # output path
    base = Path(data_fp).name.split(".")[0]
    out = Path(out_dir) / f"{base}_classd.csv"

    # load data and prep embeddings
    dat = pd.read_csv(data_fp, sep=delim, dtype=str)
    dat[emb_col] = dat[emb_col].apply(str2float_list)

    # label-index map
    ltoi = {l: i for i, l in enumerate(dat[lab_col].unique())}
    itol = {i: l for l, i in ltoi.items()}

    # extract inputs and labels
    X = np.array(dat[emb_col].to_list())
    y = np.array(dat[lab_col].map(ltoi).to_list())

    # pca
    scaler = StandardScaler()
    Xscaled = scaler.fit_transform(X)
    Xpc = PCA(n_components=2).fit_transform(Xscaled)
    plt.plot(Xpc)

    # train classifier
    X_train, y_train = X[:100], y[:100]
    X_test, y_test = X[100:,], y[100:]
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print(classification_report(y_test, preds))




