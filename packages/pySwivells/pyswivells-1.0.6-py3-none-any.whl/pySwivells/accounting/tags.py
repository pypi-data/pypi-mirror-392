import pandas as pd
import numpy as np
import pickle


def read_tags(tag_file: str):
    tags = pd.read_csv(tag_file)
    tags = tags.replace({np.nan: None})
    TAGS = {}
    for _, row in tags.iterrows():
        order = row["Nom de la commande"]
        if row.get("Balises de commande"):
            if TAGS.get(order):
                TAGS[order].append(row["Balises de commande"])
            else:
                TAGS[order] = [row["Balises de commande"]]
        elif row.get("Balise de commande"):
            if TAGS.get(order):
                TAGS[order].append(row["Balise de commande"])
            else:
                TAGS[order] = [row["Balise de commande"]]

    with open("tags.pkl", "wb") as f:
        pickle.dump(TAGS, f)
