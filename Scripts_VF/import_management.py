import pickle
from datetime import date
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning, showinfo
import sqlalchemy
import import_api as ia


def load_profil_token(liste_colonnes, tab2_v1, tkinter_tab, tkinter_root):
    """
    Création de la suite de l'interface graphique en fonction de l'avancement de l'enregistrement du profil chargé :
        - si premier chargement : enregistrement total des données API,
        - si chargement terminé : possibilité d'enregistrer totalement à nouveau ou de faire une mise à jour,
        - sinon : reprendre le chargement là où il s'est arrêté.
        
    :param liste_colonnes: Liste des données à récupérer dans l'API SIRENE.
    :param tkinter_tab: Onglet tkinter à modifier.
    :param tkinter_root: Fenêtre principale à modifier.
    :return: None.
    """

    # on récupere le nom du profil utilisateur (dans l'onglet 2)
    profil = tab2_v1.get()

    # déclaration du fichier contenant les informations de connexion à dbeaver
    profil_gene = "./save/" + profil + ".pkl"

    # déclaration du fichier contenant les informations du dernier token API du profil correspondant
    profil_token = "./save/" + profil + "_token.pkl"

    # déclaration du fichier de la dernière sauvegarde de l'import depuis l'API SIRENE
    profil_curseur = "./save/" + profil + "_curseur .pkl"

    # déclaration du nom de la table dbeaver où seront enregistrées les données de l'API
    table_enregistrement = "siren_" + profil

    # on essaie de charger les données profils et de faire la connexion avec dBeaver
    try:
        with open(profil_gene, 'rb') as file:
            # Chargement des données profil utilisateur dbeaver
            password, dbeaver_username, dbeaver_server, dbeaver_database = \
                pickle.load(file)

            # Création du moteur de connexion à dbeaver avec sqlalchemy
            dbeaver = "postgresql+psycopg2://" + dbeaver_username + \
                      ":" + password + "@" + \
                      dbeaver_server + "/" + dbeaver_database
            engine = sqlalchemy.create_engine(dbeaver, echo=False)

    except:
        # si ca ne marche pas, on affiche un warning
        text = "Nom d'utilisateur ou informations de connexion à DBeaver erronés."
        showwarning(title=None, message=text)

        # Si la connexion DBeaver n'a pas été établie, la fonction se termine ici avec la commande "return"
        return

    # si ça fonctionne on essaie de charger le nom du dernier token utilisé afin de ne pas le re-taper à chaque fois
    try:
        with open(profil_token, 'rb') as file:
            # chargement du fichier contenant le token sauvegardé
            token = pickle.load(file)
    except:
        token = ""

    # on ajoute des informations/sélections à l'onglet 2
    # ============= ligne 2  tab 2 ==================
    # affichage/sélection du token
    ttk.Label(tkinter_tab, text="Token API SIRENE") \
        .grid(column=0, row=1, padx=30, pady=10)

    # input box
    tab2_v2 = tk.StringVar()
    tab2_v2.set(token)  # valeur par défaut dans l'input box : token
    ttk.Entry(tkinter_tab, textvariable=tab2_v2, width=50) \
        .grid(row=1, column=1, padx=60, pady=10)

    # on essaie de charger les dernieres données utilisateur
    try:
        with open(profil_curseur, 'rb') as file:
            # récupération des informations du dernier enregistrement
            curseur, date_start, date_end, fini, nb_tot = pickle.load(file)

            if fini == 0:  # 0 = False

                # Si les données n'ont pas fini de charger, on continue l'enregistrement
                ttk.Button(tkinter_tab, text="Reprendre l'enregistrement",
                           command=lambda: enregistrement_total(tab2_v2.get(), engine, liste_colonnes, profil_token,
                                                                profil_curseur, table_enregistrement, tkinter_tab, tkinter_root)) \
                    .grid(row=7, column=1, padx=30, pady=10)
            else:
                # sinon, l'enregistrement n'est pas terminé :
                # on a le choix entre reprendre à 0 ou continuer l'enregistrement deuis le dernier point de sauvegarde

                # ================= ligne 3 tab 2 =================
                # texte
                ttk.Label(tkinter_tab, text="Mise à jour?") \
                    .grid(column=0, row=2, padx=30, pady=10)

                # déclaration de la variable pour les radio-boutons
                v = tk.IntVar()
                v.set(1)

                # déclaration des tuples radio-boutons
                languages = [("Mise à jour de la base", 1),
                             ("Importation totale de la base", 0)]

                # affichage des radio-boutons
                i_pos = 0
                for language, val in languages:
                    i_pos += 1
                    tk.Radiobutton(tkinter_tab,
                                   text=language,
                                   padx=10,
                                   variable=v,
                                   value=val).grid(row=2, column=i_pos, padx=10, pady=10)

                # affichage du bouton de lancement de l'enregistrement
                ttk.Button(tkinter_tab, text="Lancer l'enregistrement",
                           command=lambda: enregistrement_partiel(v.get(), tab2_v2.get(), engine, liste_colonnes,
                                                                  profil_token, profil_curseur, table_enregistrement, tkinter_tab, tkinter_root))\
                    .grid(row=4, column=1, padx=30, pady=10)

    except:
        # S'il n'y a pas de donnée utilisateur on doit repartir de 0 niveau sauvegarde et on lance juste l'import total
        ttk.Button(tkinter_tab, text="Lancement de l'enregistrement",
                   command=lambda: enregistrement_total(tab2_v2.get(), engine, liste_colonnes, profil_token,
                                                        profil_curseur,
                                                        table_enregistrement, tkinter_tab, tkinter_root)) \
            .grid(row=7, column=1, padx=30, pady=10)


def enregistrement_partiel(update, token, engine, liste_colonnes, token_path, profil_curseur, table_enregistrement, tkinter_tab, tkinter_root):
    """
    Nouvel enregistrement total ou mise à jour des données de l'API SIRENE et modifications d'affichage de la fenêtre utilisateur.
    
    :param update: 0 pour un nouvel enregistrement total. 1 pour une mise à jour de l'enregistrement.
    :param token: Token API SIRENE.
    :param engine: Moteur de connexion à dbeaver.
    :param liste_colonnes: Liste des données à récupérer dans l'API SIRENE.
    :param token_path: Chemin d'accès au fichier pickle contenant le token.
    :param profil_curseur: Chemin d'accès au fichier pickle contenant le curseur.
    :param table_enregistrement: Nom de la table DBeaver qui contiendra les données de l'API SIRENE.
    :param tkinter_tab: Onglet tkinter à modifier.
    :param tkinter_root: Fenêtre principale à modifier.
    :return:
    """
    # récupération de la date du jour
    today = date.today()

    # nouvel enregistrement du token en cas de modification
    ia.save_token(token, token_path)

    # déclaration de la variable de la barre de progression
    progress_var = tk.DoubleVar()
    # affichage de la barre de progression
    ttk.Progressbar(
        tkinter_tab,
        orient='horizontal',
        variable=progress_var,
        mode='determinate',
        length=500
    ).grid(column=1, row=10, padx=30, pady=10)

    # déclaration de la variable du texte de progression
    pourc_avcmt = tk.StringVar()
    # déclaration du texte de progression
    text_avcmt = "Progression : " + str(0) + " %"
    # affectation du texte à la variable de progression
    pourc_avcmt.set(text_avcmt)

    # affichage du texte de progression
    ttk.Label(tkinter_tab, textvariable=pourc_avcmt) \
        .grid(column=1, row=11, padx=30, pady=10)

    # actualisation de la fenêtre
    tkinter_root.update_idletasks()

    if update == 1:
        update_basis = True
    else:
        update_basis = False

    # lancement de l'import des données de l'API SIRENE
    ia.stockEtablissements_transfer(token, engine, liste_colonnes, update_basis,
                                     today, profil_curseur, table_enregistrement, progress_var, pourc_avcmt, tkinter_root, 1000)

    # affichage de la barre de progression complète une fois le chargement terminé
    text_avcmt = "Progression : " + str(100) + " %"
    pourc_avcmt.set(text_avcmt)
    progress_var.set(100)
    tkinter_root.update_idletasks()

    # affichage d'un message de confirmation de fin de chargement
    text = "Chargement des données API SIRENE terminé."
    showinfo(title=None, message=text)


def enregistrement_total(token, engine, liste_colonnes, token_path, profil_curseur, table_enregistrement, tkinter_tab, tkinter_root):
    """
    Enregistrement total des données de l'API SIRENE et modifications d'affichage de la fenêtre utilisateur.
    
    :param token: Token API SIRENE.
    :param engine: Moteur de connexion à dbeaver.
    :param liste_colonnes: Liste des données à récupérer dans l'API SIRENE.
    :param token_path: Chemin d'accès au fichier pickle contenant le token.
    :param profil_curseur: Chemin d'accès au fichier pickle contenant le curseur.
    :param table_enregistrement: Nom de la table DBeaver qui contiendra les données de l'API SIRENE.
    :param tkinter_tab: Onglet tkinter à modifier.
    :param tkinter_root: Fenêtre principale à modifier.
    :return: None.
    """
    # récupération de la date du jour
    today = date.today()

    # sauvegarde du token dans le fichier ./save/profil_token.pkl
    ia.save_token(token, token_path)

    # déclaration de la variable de la barre de progression
    progress_var = tk.DoubleVar()
    # affichage de la barre de progression
    ttk.Progressbar(
        tkinter_tab,
        orient='horizontal',
        variable=progress_var,
        mode='determinate',
        length=500
    ).grid(column=1, row=10, padx=30, pady=10)

    # déclaration de la variable du texte de progression
    pourc_avcmt = tk.StringVar()
    # déclaration du texte de progression
    text_avcmt = "Progression : " + str(0) + " %"
    # affectation du texte à la variable de progression
    pourc_avcmt.set(text_avcmt)

    # affichage du texte de progression
    ttk.Label(tkinter_tab, textvariable=pourc_avcmt) \
        .grid(column=1, row=11, padx=30, pady=10)

    # actualisation de la fenêtre
    tkinter_root.update_idletasks()

    # lancement de l'import des données de l'API SIRENE
    ia.stockEtablissements_transfer(token, engine, liste_colonnes, False,
                                     today, profil_curseur, table_enregistrement, progress_var, pourc_avcmt, tkinter_root,
                                     1000)

    # affichage de la barre de progression complète une fois le chargement terminé
    text_avcmt = "Progression : " + str(100) + " %"
    pourc_avcmt.set(text_avcmt)
    progress_var.set(100)
    tkinter_root.update_idletasks()

    # affichage d'un message de confirmation de fin de chargement
    text = "Chargement des données API SIRENE terminé."
    showinfo(title=None, message=text)
