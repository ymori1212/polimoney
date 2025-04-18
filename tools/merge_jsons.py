import os
import glob
import json
import pandas as pd


def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
        print(data)

    df = pd.DataFrame.from_dict(data["items"])
    return df



def main():
    target_dir = "output_json"
    file_paths = glob.glob(os.path.join(target_dir, "*.json"))

    df = pd.concat([load_json(f) for f in file_paths])
    df.to_csv("merged_files/all.csv", index=False)
    with open("merged_files/all.json", "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
