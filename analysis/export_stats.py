import pandas as pd

# aggregate transactions and output stats
# todo: send to google sheets? dashboard? boring?

def agg_stats(data, group_cols, prefix=""):
    s = data.groupby(group_cols).agg({
        "amount" : ["sum", "mean", "std"],
        "label" : "count"
    })
    s = s.reset_index()
    cols = []
    for col in s.columns:
        if col[0] in group_cols and col[1] == "":
            cols.append(col[0])
        else:
            cols.append(
                prefix + " ".join(col).strip().replace(" ", "_")
            )
    s.columns = cols
    return s



if __name__=="__main__":
    fp = "analysis/data/labeled_spend_01-08_2023_w_emb.txt"
    d = pd.read_csv(fp, sep="|")
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d.date.dt.month
    d["year"] = d.date.dt.year

    stats_yr = agg_stats(d, ["label", "year"], prefix="year_")
    stats_yr.to_clipboard(excel=True, index=False)
    
    stats_mnth = agg_stats(d, "month").sort_values(by="month")
    stats_mnth.to_clipboard(excel=True, index=False)

    stats_mnth_lab = agg_stats(d, ["label", "month"])
    stats_mnth_lab.to_clipboard(excel=True, index=False)
