import requests
import pandas as pd
import warnings
import pickle
import numpy as np
from tkinter.messagebox import showerror


def copy2dbeaver(df, name_table, app_repl, engine):
    """
    Exporte un dataframe dans une table de données DBeaver.
    
    :param df: DataFrame à exporter.
    :param name_table: string. Nom de la table de données DBeaver.
    :param app_repl: Méthode d'export dans la table : "replace" ou "append".
    :param engine: Moteur de connexion à la base de données DBeaver.
    :return: None.
    """

    df.to_sql(name=name_table, con=engine, if_exists=app_repl, index=False)


def save_token(token, token_path):
    """
    Enregistre le token de l'API SIRENE dans un fichier pickle nommé token_path.pkl.
    
    :param token: string. Token à enregistrer.
    :param token_path: string. Chemin d'accès et nom du fichier pickle.
    :return: None.
    """
    with open(token_path, 'wb') as file:
        # A new file will be created
        pickle.dump(token, file)


def link_creation(liste, nombre, curseur, update_bases, date_start, date_end):
    """
    Fonction de création du lien pour l'import de données depuis l'API SIRENE.
    
    :param liste: Liste des données à charger depuis l'API SIRENE.
    :param nombre: Nombre de lignes de l'API SIRENE à charger à chaque itération.
    :param curseur: Information sur l'avancement de la récupération des données (voir documentation API SIRENE "curseur").
    :param update_bases: Booléen. Si False on télécharge toutes les données de l'API. Si True on fait une mise à jour.
    :param date_start: En cas de mise à jour : date à partir de laquelle les données sont chargées.
    :param date_end: En cas de mise à jour : date jusqu'à laquelle les données sont chargées.
    :return: string. Le lien pour la requête à l'API SIRENE.
    """

    if not update_bases:
        # si on ne fait pas de mise à jour, les variables date_start et date_end ne sont pas utilisées
        address_start = 'https://api.insee.fr/entreprises/sirene/V3/siret?date=2023-01-01&champs='
    else:
        # sinon, c'est une mise à jour, on intègre les variables date_start et date_end
        address_start = "https://api.insee.fr/entreprises/sirene/V3/siret?q=dateCreationUniteLegale:[" + str(
            date_start) + " TO " \
                        + str(date_end) + "]&champs="

    # déclaration du texte du lien qui contient la liste des données à charger depuis l'API SIRENE
    address_middle = ''
    for ilist in liste:
        if ilist == liste[-1]:
            address_middle += ilist
        else:
            address_middle += ilist + '%2C%20'

    # déclaration du texte du lien qui contient le type de tri, le nombre de données à charger et le curseur
    address_end = '&tri=siren%20asc' \
                  '&nombre=' + str(nombre) \
                  + '&curseur=' + curseur

    # concaténation des trois parties du lien
    address = address_start + address_middle + address_end

    return address


def stockEtablissements_transfer(token: str, engine, liste,
                                 update_bases,
                                 today, profil_curseur,
                                 table_enregistrement,
                                 progress_var,
                                 pourc_avcmt,
                                 tkinter_root,
                                 nombre: int = 1000):
    """
    Transfert des données de l'API SIRENE vers la base de données locale d'Urbanease.
    
    :param token: Token de connexion à l'API SIRENE (délai de péremption: 1 semaine).
    :param engine: Moteur de connexion à la base de données DBeaver.
    :param liste: Liste des données à charger depuis l'API SIRENE.
    :param update_bases: Booléen. Si False on télécharge toutes les données de l'API. Si True on fait une mise à jour.
    :param today: Date du jour.
    :param profil_curseur: Fichier .pkl contenant les informations permettant d'obtenir l'état d'avancement de l'enregistrement.
    :param table_enregistrement: Nom de la table DBeaver qui va contenir les données de l'API.
    :param progress_var: Variable d'affichage de la barre de progression.
    :param pourc_avcmt: Variable d'affichage du texte de progression.
    :param tkinter_root: Fenêtre principale.
    :param nombre: Nombre de lignes de l'API SIRENE à charger à chaque itération.
    :return: None.
    """
    # EXCEPTION si nombre demandé supérieur à 1000
    if nombre > 1000:
        warnings.warn(
            "Vous avez demandé un nombre de lignes supérieur à 1000 mais ce n'est pas autorisé par l'API SIRENE."
            "Les données ont été chargées pour 1000 lignes.")
        nombre = 1000

    curseur = '*'  # curseur initial
    stop_curseur = ''  # curseur qui stoppe la boucle while quand il est égal à curseur (voir documentation API SIRENE curseur)

    # BOUCLE
    while curseur != stop_curseur:
        try:
            # récupération des informations de dernière sauvegarde dans le pickle
            with open(profil_curseur, 'rb') as file:
                # récupération des informations permettant d'obtenir l'état d'avancement de l'enregistrement
                curseur, date_start, date_end, fini, nb_tot = pickle.load(file)

            # vérification de l'état du dernier import : est-il complet jusqu'à la date_end ?
            # si oui, on passe en mode mise à jour : les filtres de dates changent et le curseur est réinitialisé
            if fini:
                date_start = date_end
                date_end = today
                fini = False
                curseur = "*"
                nb_tot = 0

            # déclaration de la variable de réinitialisation de la table : si égale à 1 on ajoute les données à la table
            tab_reinitialisation = 1

        except:
            # s'il n'est pas possible d'ouvrir le pickle c'est qu'il s'agit d'un premier import
            # les filtres sont initialisés par défaut pour un import complet jusqu'à "aujourd'hui"
            curseur = "*"
            # déclaration de la variable de réinitialisation de la table : si égale à 0 on réinitialise toutes les données
            tab_reinitialisation = 0
            date_start = ""
            date_end = today
            fini = False
            nb_tot = 0

        # déclaration du lien sans curseur
        link = link_creation(liste, nombre, curseur, update_bases, date_start, date_end)

        # requête à l'API SIRENE
        r = requests.get(link,
                         headers={'Authorization': "Bearer " + token,
                                  'Accept': 'application/json'})

        # exception si le statut de réponse de la requête est différent de 200 (code de réponse OK)
        if r.status_code != 200:
            text = "La connexion à l'API ne fonctionne pas, vérifiez le TOKEN"
            showerror(title=None, message= text)
            return

        # incrément nb_tot pour l'état d'avancement (barre de progression + pourcentage avancement)
        nb_tot += r.json()['header']['nombre']

        # calcul du pourcentage d'avancement
        rempl_temp = 100 - ((r.json()["header"]["total"] - nb_tot) / r.json()["header"]["total"] * 100)
        # déclaration de la valeur d'avancement pour la barre de progression
        progess_value = np.round(rempl_temp)
        # déclaration de la valeur d'avancement pour le texte de progression
        progess_value_pourc = "Progression : " + str(np.round(rempl_temp, 2)) + "  %"

        # modification de la valeur du texte de progression
        pourc_avcmt.set(progess_value_pourc)
        # modification de la valeur de la barre de progression
        progress_var.set(progess_value)

        # mise à jour de la fenêtre
        tkinter_root.update_idletasks()

        # nouveaux curseurs
        stop_curseur = curseur
        curseur = r.json()['header']['curseurSuivant']
        # curseur change à chaque iter pour accéder à de nouvelles données de l'API

        if r.json()['header']['nombre'] != 0:

            # récupération du json avec les informations souhaitées dans un dataframe temporaire
            df_temp = pd.json_normalize(r.json()['etablissements'])

            # phase de renommage des colonnes de typo 'uniteLegale.etc'
            df_temp.columns = df_temp.columns.map(lambda x: x[12:] if x not in ['siren', 'nic', 'siret'] else x)

            # aggrégation des numéros siret et nic
            df_temp = df_temp.groupby('siren').agg({'nic': ', '.join,
                                                    'siret': ', '.join,
                                                    'dateCreationUniteLegale': 'first',
                                                    'denominationUniteLegale': 'first',
                                                    'nomUniteLegale': 'first',
                                                    'nomUsageUniteLegale': 'first',
                                                    'prenom1UniteLegale': 'first',
                                                    'prenom2UniteLegale': 'first',
                                                    'prenom3UniteLegale': 'first',
                                                    'prenom4UniteLegale': 'first',
                                                    'prenomUsuelUniteLegale': 'first'
                                                    }
                                                   ).reset_index()

            if tab_reinitialisation == 0:
                # on réinitialise toutes les données
                copy2dbeaver(df_temp, table_enregistrement, "replace", engine)

            else:
                # on ajoute les données à la table
                copy2dbeaver(df_temp, table_enregistrement, "append", engine)

        if curseur == stop_curseur:
            # fin de l'import des données de l'API SIRENE lorsque le curseur est toujours le même
            fini = True
            date_start = date_end
            date_end = today

        with open(profil_curseur, 'wb') as file:
            # sauvegarde des informations d'avancement de l'import
            save_file = [curseur, date_start, date_end, fini, nb_tot]
            pickle.dump(save_file, file)
