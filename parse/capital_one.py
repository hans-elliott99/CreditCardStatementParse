#!/usr/bin/env python
# capital_one.py
# Parse monthly CapitalOne account statement PDF into text delimited dataset
#
# Hans Elliott

import tabula
import pandas as pd
from src.helpers import validate_java
import re
import calendar
from pathlib import Path
from datetime import datetime
import argparse

MONTHS = {mnth.lower(): idx for idx, mnth
          in enumerate(calendar.month_abbr) if mnth}

YEAR = datetime.now().year

def init_data():
    return {
        "date" : [],
        "descr" : [],
        "amount" : []
    }

def format_date(date_str, year=None):
    m, d = date_str.lower().strip().split(" ")
    m = MONTHS[m.strip()]
    if int(m) < 10:
        m = "0" + str(m)
    if int(d) < 10:
        d = "0" + str(d)
    if year is None:
        year = YEAR 

    return f"{year}-{m}-{d}"

def format_num(num_str):
    return float(re.sub("[^\d\.]", "", num_str))


def scrape_page(page, data):
    in_table = False
    for i, row in page.iterrows():
        # print(i)
        row = ' '.join([str(e) for e in list(row)])
        row_lwr = row.lower().strip()
        if "trans date" in row_lwr:
            # print("in")
            in_table = True
            continue
        elif in_table and ("additional information" in row_lwr
                           or "transaction" in row_lwr
                           or "capital one" in row_lwr
                           or "total fees" in row_lwr
                           or "interest charge" in row_lwr):
            # print("out")
            in_table = False
            continue
        if in_table:
            row_split = row.split(" ")
            # get date
            try:
                data["date"].append(format_date(' '.join(row_split[0:2]),
                                                year=None))
            except Exception as e:
                print(f"Warning - failed to parse date.\n{e}")
                data["date"].append("")
            # get payment descr
            try:
                data["descr"].append(' '.join(row_split[4:-1]))
            except Exception as e:
                print(f"Warning - failed to parse description.\n{e}")
                data["descr"].append("")
            # get payment amount
            try:
                data["amount"].append(format_num(row_split[-1]))
            except Exception as e:
                print(f"Warning - failed to parse transaction amount.\n{e}")
                data["amount"].append("")
    return data

parser = argparse.ArgumentParser(
    prog="capital_one.py",
    description="Convert your CapitalOne statement PDF into a delimited text file.",
    epilog=""
)
parser.add_argument("pdf_filename")
parser.add_argument("-o", "--output",
                    default=None,
                    help="The path to save the script output to. Default is to save it to the working directory with the same name as the input."
                    )
parser.add_argument("-p", "--pages",
                    default="all",
                    metavar="1,2,N",
                    help="The page(s) of the PDF to parse. Defaults to 'all'. If multiple pages, separate with a comma. Specifying pages can help speed up the data extraction process."
                    )
parser.add_argument("-a", "--area",
                    metavar="T,L,B,R",
                    default="0,0,2480,3508",
                    help="Portion of the page to analyze(top,left,bottom,right). Defaults to (0,0,2480,3508), which tends to work. See https://tabula-py.readthedocs.io/en/latest/tabula.html#tabula.io.read_pdf"
                    )
parser.add_argument("-d", "--delim",
                    default="|",
                    help="The delimiter to use for the outputted delimited text file. Defaults to the pipe `|`.")
parser.add_argument("-q", "--quiet",
                    action="store_true",
                    help="If this flag is used the script is executed without printing info.")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.quiet:
        def print(*args, **kwargs):
            pass

    validate_java(verbose=True)
    # process args
    args.pdf_filename = Path(args.pdf_filename)
    assert args.pdf_filename.exists()

    if args.output is None:
        file = ''.join(str(args.pdf_filename.name).split(".")[:-1])
        args.output = f"./{file}.txt"

    args.area = [int(a) for a in args.area.split(",")]
    assert len(args.area) == 4
    if args.pages != "all":
        args.pages = [int(p) for p in args.pages.split(",")]
        assert len(args.pages) > 0

    # Process pdf
    print(f"Extracting text from {args.pdf_filename}")
    print(f" - pages: {args.pages}")
    print(f" - extraction area: {args.area}")
    pdf = tabula.read_pdf(args.pdf_filename,
                          area=args.area,
                          pages=args.pages)

    print(f"Extracting data from text")
    dat = init_data()
    for pg in pdf:
        dat = scrape_page(pg, dat)
 
    # convert to dataframe and address corner cases in date
    dat = pd.DataFrame(dat)
    # if it's january, we may have transactions from december of last year
    dat["date"] = pd.to_datetime(dat.date)
    dat["month"] = dat.date.dt.month
    if dat.month.mode().item() == 1:
        dat.loc[dat.month == 12, "date"] = dat.loc[dat.month == 12,
                                                   ].date.astype(str).str.replace(str(YEAR), str(YEAR-1))

    # save
    print(f"Saving to {args.output}")
    pd.DataFrame(dat).to_csv(
        args.output,
        sep=args.delim,
        index=False
    )
