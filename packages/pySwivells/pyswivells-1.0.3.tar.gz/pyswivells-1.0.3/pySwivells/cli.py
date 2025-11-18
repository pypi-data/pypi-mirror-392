import fire

from pySwivells import accounting

from pySwivells.iomix import log, Colors
from pySwivells import __version__


class PySwivellsCLI:
    f"""PySwivells {{__version__}} command-line interface."""

    def version(self):
        print(f"PySwivells version: {__version__}")

    class compta:
        """Fonctions de comptabilité.

        Étapes :
        1. Récupérer le tableau des balises des commandes
        2. Lancer le script de lecture des balises : pyswivells compta tags <TABLEAU-DES-BALISES.csv>
        3. Récupérer du tableau des ventes Shopify.
        4. Lancer le nettoyage : pyswivells compta clean <TABLEAU-DES-VENTES.csv>
        5. Vérifier le tableau nettoyé pour d'éventuelles erreurs de TVA.
        6. Exporter les relevés d'encaissement Shopify.
        7. Placer tous les relevés d'encaissement Shopify dans un seul dossier <DOSSIER>.
        8. Vérifier la correspondance entre les ventes et les encaissements : pyswivells compta reconcile <DOSSIER>
        """

        def tags(self, TABLEAU_DES_BALISES_CSV: str):
            """Lit les balises des commandes depuis un fichier CSV.

            Args:
                TABLEAU_DES_BALISES_CSV: Chemin vers le fichier CSV des balises des commandes.
            """
            accounting.read_tags(TABLEAU_DES_BALISES_CSV)
            log(
                f"Balises lues et enregistrées depuis {TABLEAU_DES_BALISES_CSV} ✅",
            )

        def clean(self, TABLEAU_DES_VENTES_EXCEL: str):
            """Nettoie le tableau des ventes Shopify.

            Args:
                TABLEAU_DES_VENTES: Chemin vers le fichier Excel des ventes Shopify.
            """
            accounting.clean_sales(TABLEAU_DES_VENTES_EXCEL)

        def reconcile(self, DOSSIER: str):
            """Vérifie la correspondance entre les ventes et les encaissements.

            Args:

                DOSSIER: Chemin vers le dossier contenant les relevés d'encaissement.
            """
            accounting.reconcile(
                DOSSIER,
            )


def main():
    # Fire automatically exposes all methods as CLI commands
    fire.Fire(PySwivellsCLI)
