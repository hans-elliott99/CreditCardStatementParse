import pandas as pd
from pathlib import Path

def concat_dfs(fp_list):
    if isinstance(fp_list, (str, Path)):
        fp_list = [fp_list]
    elif not isinstance(fp_list, list):
        raise TypeError(f"'fp_list' must be a list of file paths, not {type(fp_list)}.")
    out = pd.DataFrame()
    for fp in fp_list:
        out = pd.concat([out, pd.read_csv(fp, sep="|")], axis=0)
    return out


if __name__=="__main__":

    # cli args
    input_dir = "./parse/outputs/"
    output_path = "./analysis/data/spend_01-11_2023.txt"
    delim = "|"

    out = concat_dfs(list(Path(input_dir).glob("*.txt")))
    out = out.loc[~out.date.isna()]
    out.to_csv(output_path, sep=delim, index=False)
