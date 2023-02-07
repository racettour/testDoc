import tkinter as tk
from tkinter import ttk
import save_password as sp
import import_management as im
import merge as mg


if __name__ == "__main__":
    """
    Le main.py gère l'interface graphique qui permet de :
    - récupérer les informations de connexion à DBeaver
    - lancer l'enregistrement des données de l'API SIRENE via des requêtes en boucle
    - effectuer la jointure des informations dans la table de données DBeaver choisie
    """
    # liste des données à récupérer dans l'API SIRENE
    liste_colonnes = ['siren',
                      'nic',
                      'siret',
                      'dateCreationUniteLegale',
                      'prenomUsuelUniteLegale',
                      'prenom1UniteLegale',
                      'prenom2UniteLegale',
                      'prenom3UniteLegale',
                      'prenom4UniteLegale',
                      'nomUniteLegale',
                      'nomUsageUniteLegale',
                      'denominationUniteLegale'
                      ]

    # Création de la fenêtre main et gestion de la taille de la fenêtre
    root = tk.Tk()
    root.geometry("800x400")

    # ajout du titre de la fenêtre
    root.title("URBANEASE")

    # création du widjet onglet
    tabControl = ttk.Notebook(root)

    # ajout des onglets
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)

    # Titre des onglets
    tabControl.add(tab1, text='Création profil DBeaver')
    tabControl.add(tab2, text='Import données depuis l\'API SIRENE')
    tabControl.add(tab3, text='Jointure des tables Urbanease et Siren')

    # affichage des onglets
    tabControl.pack(expand=1, fill="both")

    # ============== ONGLET 1 ==================

    # ============= ligne 1 ==================
    # text 1
    ttk.Label(tab1, text="Nom Utilisateur") \
        .grid(column=0, row=0, padx=30, pady=10)

    # input box 1
    tab1_v1 = tk.StringVar()
    ttk.Entry(tab1, textvariable=tab1_v1) \
        .grid(row=0, column=1)

    # ============= ligne 2 ==================
    # text
    ttk.Label(tab1, text="dbeaver_username") \
        .grid(column=0, row=1, padx=30, pady=10)

    # input box
    tab1_v2 = tk.StringVar()
    tab1_v2.set("postgres")
    ttk.Entry(tab1, textvariable=tab1_v2) \
        .grid(row=1, column=1, padx=30, pady=10)

    # ============= ligne 3 ==================
    # text
    ttk.Label(tab1, text="dbeaver_server") \
        .grid(column=0, row=2, padx=30, pady=10)

    # input box
    tab1_v3 = tk.StringVar()
    tab1_v3.set("localhost")
    ttk.Entry(tab1, textvariable=tab1_v3) \
        .grid(row=2, column=1, padx=30, pady=10)

    # ============= ligne 4 ==================
    # text
    ttk.Label(tab1, text="dbeaver_database") \
        .grid(column=0, row=3, padx=30, pady=10)

    # input box
    tab1_v4 = tk.StringVar()
    tab1_v4.set("projet3")
    ttk.Entry(tab1, textvariable=tab1_v4) \
        .grid(row=3, column=1, padx=30, pady=10)

    # ============= ligne 5 ==================
    # text
    ttk.Label(tab1, text="dbeaver_password") \
        .grid(column=0, row=4, padx=30, pady=10)

    # input box
    tab1_v5 = tk.StringVar()
    tab1_v5.set("")
    ttk.Entry(tab1, textvariable=tab1_v5, show='*') \
        .grid(row=4, column=1, padx=30, pady=10)

    # ============= ligne 6  ==================

    ttk.Button(tab1, text="Enregistrement du profil",
               command=lambda: sp.get_var_tab1(tab1_v1, tab1_v2, tab1_v3, tab1_v4, tab1_v5)) \
        .grid(row=5, column=0, padx=30, pady=10)

    # ============== ONGLET 2 ==================

    # ============= ligne 1 ==================
    # text
    ttk.Label(tab2, text="Nom utilisateur") \
        .grid(column=0, row=0, padx=30, pady=10)

    # input box
    tab2_v1 = tk.StringVar()
    tab2_v1.set("")
    ttk.Entry(tab2, textvariable=tab2_v1, width=50) \
        .grid(row=0, column=1, padx=60, pady=10)

    # bouton chargement profils
    ttk.Button(tab2, text="Chargement du profil",
               command=lambda: im.load_profil_token(liste_colonnes, tab2_v1, tab2, root)) \
        .grid(row=30, column=0, padx=30, pady=10)

    # ============== ONGLET 3 ==================

    # ============= ligne 1 ==================
    # text
    ttk.Label(tab3, text="Nom utilisateur") \
        .grid(column=0, row=0, padx=30, pady=10)

    # input box
    tab3_v1 = tk.StringVar()
    tab3_v1.set("")
    ttk.Entry(tab3, textvariable=tab3_v1) \
        .grid(row=0, column=1, padx=60, pady=10)

    # bouton chargement profils
    ttk.Button(tab3, text="Chargement du profil",
               command=lambda: mg.load_merge(liste_colonnes, tab3_v1, tab3, root)) \
        .grid(row=30, column=0, padx=30, pady=10)

    # commande qui permet l'affichage de la fenêtre
    root.mainloop()
