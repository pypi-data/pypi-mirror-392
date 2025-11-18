import pandas as pd
import numpy as np
import os

from pySwivells.iomix import error


def __get_files(directory: str):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv") or filename.endswith(".xlsx"):
            files.append(os.path.join(directory, filename))
    return files


def __get_sales():
    if not os.path.exists("Ventes-nettoyées.xlsx"):
        error(
            "Le fichier 'Ventes-nettoyées.xlsx' est introuvable. Veuillez exécuter d'abord le nettoyage des ventes."
        )
    df = pd.read_excel("Ventes-nettoyées.xlsx")
    df = df.replace({np.nan: None})
    return df


def __process_payment_file(file_path: str, payments: dict):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        error(f"Format de fichier non pris en charge : {file_path}")
    df = df.replace({np.nan: None})
    payouts = df["Payout Date"].unique()
    for payout in payouts:
        payout_df = df[df["Payout Date"] == payout]
        for _, row in payout_df.iterrows():
            order = row["Order"]
            amount = row["Amount"]
            fee = row["Fee"]
            net = row["Net"]
            if order not in payments:
                payments[order] = []
            payments[order].append(
                {
                    "payout_date": payout,
                    "amount": amount,
                    "fee": fee,
                    "net": net,
                    "source_file": os.path.basename(file_path),
                }
            )


def reconcile(payments_dir: str):
    df = __get_sales()
    df["Date du paiement"] = ""
    df["Relevé"] = ""
    df["CA"] = ""
    df["SHP Payment fee"] = ""
    df["Net reçu"] = ""
    payment_files = __get_files(payments_dir)
    payments = {}
    final_df = []
    for p in payment_files:
        __process_payment_file(p, payments)
    df = pd.read_excel("Ventes-nettoyées.xlsx")
    order_without_payment = set()
    order_to_check = set()
    for _, row in df.iterrows():
        row["Réconciliation"] = "✅"
        order = row["Nom de la commande"]
        payouts = payments.get(order, [])
        if len(payouts) == 0:
            row["Réconciliation"] = "❌"
            row["Commentaire"] = "Pas de paiement trouvé"
            order_without_payment.add(order)
        elif len(payouts) == 1:
            order_df = df[df["Nom de la commande"] == order]
            total_amount = order_df["Ventes totales"].sum()
            row["Date du paiement"] = payouts[0]["payout_date"]
            row["Relevé"] = payouts[0]["source_file"]
            row["CA"] = payouts[0]["amount"]
            row["SHP Payment fee"] = payouts[0]["fee"]
            row["Net reçu"] = payouts[0]["net"]
            if abs(payouts[0]["amount"] - total_amount) > 0.01:
                row["Réconciliation"] = "❌"
                row["Commentaire"] = "Montant du paiement incorrect"
                order_to_check.add(order)
        else:
            order_df = df[df["Nom de la commande"] == order]
            for d in order_df["Jour"].unique():
                sub_order_df = order_df[order_df["Jour"] == d]
                total_amount = sub_order_df["Ventes totales"].sum()
                matched = __find_matching_payment(total_amount, payouts, row)
                if not matched:
                    payout_df = pd.DataFrame(payouts)
                    grouped = (
                        payout_df.groupby("payout_date")
                        .agg(
                            {
                                "amount": "sum",
                                "fee": "sum",
                                "net": "sum",
                                "source_file": lambda x: ",".join(
                                    x.unique()
                                ),  # optional: combine unique source files
                            }
                        )
                        .reset_index()
                    )
                    payouts = grouped.to_dict(orient="records")
                    matched = __find_matching_payment(total_amount, payouts, row)
                    if not matched:
                        print("no match after grouping...")
                        row["Réconciliation"] = "❌"
                        row["Commentaire"] = "Montant du paiement incorrect"
                        order_to_check.add(order)
        final_df.append(row)
    print(f"{len(order_without_payment)} commandes sans paiement trouvé")
    print(f"{len(order_to_check)} commandes avec des montants à vérifier")
    print("Fichier Excel sauvegardé sous 'Reconciliation.xlsx'")
    final_df = pd.DataFrame(final_df)
    final_df.to_excel("Reconciliation.xlsx", index=False)


def __find_matching_payment(total_amount: float, payouts: list, row) -> bool:
    for p in payouts:
        if abs(p["amount"] - total_amount) < 0.01:
            row["Date du paiement"] = p["payout_date"]
            row["Relevé"] = p["source_file"]
            row["CA"] = p["amount"]
            row["SHP Payment fee"] = p["fee"]
            row["Net reçu"] = p["net"]
            return True
    return False
