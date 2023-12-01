import pandas as pd

# append new data to the hand labeled dataset

fullpath = "./analysis/data/spend_01-11_2023.txt"
labeledpath = "./analysis/data/hand_labeled_spend.txt"

full = pd.read_csv(fullpath, sep="|")
full["date"] = pd.to_datetime(full.date)

labeled = pd.read_csv(labeledpath, sep="|")
labeled["date"] = pd.to_datetime(labeled.date)
maxdate = labeled.date.max()

new = pd.concat([
    labeled,
    full.loc[full.date > maxdate]
], axis=0).reset_index(drop=True)


labeled.to_csv(labeledpath.replace(".txt", "_backup.txt"), sep="|", index=False)
new.to_csv(labeledpath, sep="|", index=False)

