import pandas as pd
import math
import numpy as np
import pickle
import os

from pySwivells import iomix
from pySwivells.accounting.tva import TVA_RATES


def nullify(row):
    for col in [
        "Ventes brutes",
        "Réductions",
        "Retours",
        "Ventes nettes",
        "Frais d’expédition",
        "Taxes",
        "Ventes totales",
    ]:
        row[col] = 0


RULES = [
    {
        "tag": "lesbienfaiteurs",
        "comment": "Vente les bien faiteurs",
        "action": nullify,
    },
    {"tag": "Etsy", "comment": "Commande Etsy", "action": lambda r: r},
]


def __load_tags():
    if not os.path.exists("tags.pkl"):
        iomix.warning("Aucun fichier de balises trouvé.")
        rep = iomix.yes_or_no("Voulez-vous continuer sans balises ?")
        if rep is False:
            iomix.log("Opération terminée par l'utilisateur.")
            iomix.log(
                "Veuillez d'abord exécuter 'pyswivells compta tags <FICHIER.csv>'"
            )
            exit(1)
        else:
            return {}

    with open("tags.pkl", "rb") as f:
        return pickle.load(f)


def __apply_rules(df):
    tag_map = __load_tags()
    modified_rows = []
    for _, row in df.iterrows():
        order = row["Nom de la commande"]
        tags = tag_map.get(order)
        row["Comment"] = ""
        if tags:
            for rule in RULES:
                if rule["tag"] in tags:
                    row["Comment"] += rule["comment"] + "; "
                    rule["action"](row)
        modified_rows.append(row)

    df = pd.DataFrame(modified_rows)
    return df


def __calculate_tva(df) -> float:
    df["TVA"] = df["Pays d’expédition"].map(TVA_RATES)
    df["Taxes calculées"] = round(
        round(df["Ventes totales"] / (1 + df["TVA"] / 100), 2) * df["TVA"] / 100,
        2,
    )
    df["Différence"] = df["Taxes"] - df["Taxes calculées"]
    df["Erreur de TVA"] = df["Différence"].apply(
        lambda x: "ERREUR" if abs(x) > 0.01 else ""
    )


def __clean_lines(df):
    rows_to_keep = []
    orders = df["Nom de la commande"].unique()
    for order in orders:
        order_df_all_days = df[df["Nom de la commande"] == order]
        for day in order_df_all_days["Jour"].unique():
            order_df = order_df_all_days[order_df_all_days["Jour"] == day]
            values = list(
                set([math.fabs(v) for v in order_df["Ventes totales"].unique()])
            )
            d = {v: {"+": 0, "-": 0} for v in values}
            for _, row in order_df.iterrows():
                sign = "+" if row["Ventes totales"] > 0 else "-"
                d[math.fabs(row["Ventes totales"])][sign] += 1
            for k, v in d.items():
                if v["+"] > v["-"]:
                    value_to_keep = float(k)
                elif v["+"] < v["-"]:
                    value_to_keep = -float(k)
                else:
                    continue
                sub_df = order_df[
                    order_df["Ventes totales"] == value_to_keep
                ].reset_index(drop=True)
                if len(sub_df) > 1:
                    sub_df = order_df[
                        (order_df["Ventes totales"] == value_to_keep)
                        & (
                            order_df.get("Titre de produit au moment de la vente")
                            | order_df.get("Titre du produit au moment de la vente")
                        )
                    ].reset_index(drop=True)
                    if len(sub_df) > 1:
                        counter = 0
                        for _, r in sub_df.iterrows():
                            counter += 1
                            rows_to_keep.append(r)
                            if counter == abs(v["+"] - v["-"]):
                                break
                    elif len(sub_df) == 1:
                        rows_to_keep.append(sub_df.iloc[0])
                    else:
                        sub_df = order_df[
                            (order_df["Ventes totales"] == value_to_keep)
                        ].reset_index(drop=True)
                        rows_to_keep.append(sub_df.iloc[0])

                else:
                    rows_to_keep.append(sub_df.iloc[0])
    return pd.DataFrame(rows_to_keep)


def clean_file(sales_file: str) -> pd.DataFrame:
    df = pd.read_csv(sales_file)
    df = df.replace({np.nan: None})
    df = __apply_rules(df)
    __calculate_tva(df)

    cleaned_df = __clean_lines(df)
    cleaned_df = cleaned_df[
        (
            cleaned_df.get("Titre de produit au moment de la vente")
            or cleaned_df.get("Titre du produit au moment de la vente")
        )
        != "Tote bag noir Swivells"
    ].reset_index(drop=True)
    return cleaned_df


def clean_sales(sales_file: str):
    final_df = clean_file(sales_file)
    final_df.to_excel("Ventes-nettoyées.xlsx", index=False)


def clean_sales_to_csv(sales_file: str, output_file: str):
    final_df = clean_file(sales_file)
    final_df.to_csv(output_file, index=False)
