import os
import argparse
import pandas as pd


def run(ROOT):
    tab = pd.read_csv("mutant_side.tab", sep="\t")

    for i, row in tab.iterrows():
        vid_fn = f"{ROOT}/{row.Stage}/{row.Genotype}/{row.Video}.mp4"
        json_fn = f"{ROOT}/{row.Stage}/{row.Genotype}/{row.Video}.json"

        dictionary = {}
        dictionary["mutant_side"] = row.Mutant_Side

        if not os.path.exists(json_fn):
            if not os.path.exists(vid_fn):
                print(f"WARNING: video file '{vid_fn}' for json does not exist")
            with open(json_fn, "w") as outfile:
                json.dump(dictionary, outfile)
            print(f"Writing {json_fn}")

        else:
            if not os.path.exists(vid_fn):
                print(f"WARNING: video file '{vid_fn}' for json does not exist")
            print(f"{json_fn} okay")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frog-Analysis cluster analysis run")

    parser.add_argument(
        "root",
        help="Movie root folder",
        type=str,
        required=True,
    )

    args = parser.parse_args()

    assert os.path.exists(args.root), "Movie root dir does not exist"
    run(args.root)
