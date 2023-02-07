import pickle
import sqlalchemy
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning, showinfo


def load_merge(liste_colonnes, tab3_v1, tkinter_tab, tkinter_root):
    """
    Création de la suite de l'interface graphique et jointure dans tables siren_profil et companies_owning_parcels dans DBeaver.
    
    :param liste_colonnes: Liste des données à récupérer depuis l'API SIRENE.
    :param tkinter_tab: Onglet tkinter à modifier.
    :param tkinter_root: Fenêtre principale à modifier.
    :return: None.
    """
    # récupération du nom du profil
    profil = tab3_v1.get()
    # déclaration du chemin d'accès au fichier pickle contenant les informations du profil
    profil_gene = "./save/" + profil + ".pkl"
    # récupération du nom de la table siren_profil
    table_enregistrement = "siren_" + profil

    # on essaie de charger les données profil et de faire la connexion avec dBeaver
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

    # on ajoute des informations/sélections à l'onglet 3
    # ============= ligne 2  tab 3 ==================
    # affichage/sélection du nom de la table 'gauche' (celle qui reçoit les données de siren_profil)
    ttk.Label(tkinter_tab, text="Left table") \
        .grid(column=0, row=1, padx=30, pady=10)

    # input box
    tab3_v2 = tk.StringVar()
    text = "companies_owning_parcels"
    tab3_v2.set(text)
    ttk.Entry(tkinter_tab, textvariable=tab3_v2, width=30) \
        .grid(row=1, column=1, padx=60, pady=10)

    # ============= ligne 3  tab 3 ==================
    # affichage du nom de la table siren_profil
    ttk.Label(tkinter_tab, text="Right table") \
        .grid(column=0, row=2, padx=30, pady=10)

    ttk.Label(tkinter_tab, text=table_enregistrement) \
        .grid(column=1, row=2, padx=30, pady=10)

    # déclaration du bouton qui lance la jointure
    ttk.Button(tkinter_tab, text="Left join",
               command=lambda: merge(table_enregistrement, tab3_v2.get(), engine, liste_colonnes)) \
        .grid(row=7, column=1, padx=30, pady=10)

    tkinter_root.update_idletasks()


def merge(right_table, left_table, engine, liste_colonnes):
    """
    Jointure des tables siren_profil et companies_owning_parcels dans DBeaver.
    
    :param right_table: Table 'droite' siren_profil contenant les données API SIRENE à joindre à l'autre table.
    :param left_table: Table 'gauche' companies_owning_parcels qui reçoit les données API SIRENE.
    :param engine: Moteur de connexion à dbeaver.
    :param liste_colonnes: Liste des données à récupérer dans l'API SIRENE.
    :return: None.
    """
    # suppression de la colonne 'siren' dans la liste des colonnes à joindre
    liste_colonnes.remove('siren')

    # déclaration de la commande SQL permettant de créer les nouvelles colonnes des données de l'API SIRENE
    sql_commande1 = 'ALTER TABLE ' + left_table + \
                    ' ADD column IF NOT exists nic text,' + \
                    ' ADD column IF NOT exists siret text,' + \
                    ' ADD column IF NOT exists dateCreationUniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists denominationUniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists nomUniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists nomUsageUniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists prenom1UniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists prenom2UniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists prenom3UniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists prenom4UniteLegale varchar(255),' + \
                    ' ADD column IF NOT exists prenomUsuelUniteLegale varchar(255);'

    try:
        # exécution de la commande SQL avec le moteur sqlalchemy
        engine.execute(sql_commande1).fetchall()

    except:
        # bug constaté avec le 'engine.execute' mais la commande SQL est bien exécutée
        # ce subterfuge permet d'ignorer l'erreur
        pass

    # déclaration de la commande SQL permettant de mettre à jour (jointure)
    # les nouvelles colonnes des données de l'API SIRENE
    for i_list in liste_colonnes:
        sql_commande2 = 'UPDATE ' + left_table + \
                        ' SET  ' + i_list.lower() + '=' + right_table + '."' + i_list + '"' + \
                        ' FROM ' + right_table + \
                        ' WHERE ' + left_table + '.siren  = ' + right_table + '."siren";'

        try:
            # exécution de la commande SQL avec le moteur sqlalchemy
            engine.execute(sql_commande2).fetchall()

        except:
            # bug constaté avec le 'engine.execute' mais la commande SQL est bien exécutée
            # ce subterfuge permet d'ignorer l'erreur
            pass

    # affichage d'un message de confirmation de jointure
    text = "Jointure réussie"
    showinfo(title=None, message=text)
