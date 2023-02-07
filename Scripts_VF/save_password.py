import pickle
from tkinter.messagebox import showinfo
import os


def get_var_tab1(tab1_v1, tab1_v2, tab1_v3, tab1_v4, tab1_v5):
    """
    Récupère les données des cases de l'onglet 1  et les enregistre dans profil.pkl.
    
    :param tab1_v1: Valeur de l'input en ligne 1 : nom utilisateur.
    :param tab1_v2: Valeur de l'input en ligne 2 : dbeaver_username.
    :param tab1_v3: Valeur de l'input en ligne 3 : dbeaver_server.
    :param tab1_v4: Valeur de l'input en ligne 4 : dbeaver_database.
    :param tab1_v5: Valeur de l'input en ligne 5 : dbeaver_password.
    :return: None.
    """
    user = tab1_v1.get()
    dbeaver_username = tab1_v2.get()
    dbeaver_server = tab1_v3.get()
    dbeaver_database = tab1_v4.get()
    password = tab1_v5.get()

    save_password(
        user,
        dbeaver_username,
        dbeaver_server,
        dbeaver_database,
        password
    )

    # affichage d'un message de confirmation de sauvegarde
    text = "Sauvegarde réussie"
    showinfo(title=None, message=text)


def save_password(username, dbeaver_username, dbeaver_server, dbeaver_database, password):
    """
    Enregistre les informations de connexion à la table de données DBeaver.
    
    :param username: Nom du profil à créer lié à l'interface graphique.
    :param dbeaver_username: Nom utilisateur du profil DBeaver.
    :param dbeaver_server: Nom du serveur DBeaver.
    :param dbeaver_database: Nom de la base de données DBeaver contenant la nouvelle table de données.
    :param password: Mot de passe du profil DBeaver correspondant.
    """

    # si le fichier save n'extite pas on le crée
    if not os.path.isdir("./save"):
        os.mkdir("./save")


    var2save = [password, dbeaver_username, dbeaver_server, dbeaver_database]

    # déclaration du chemin et du nom du fichier
    username = "./save/" + username + ".pkl"

    with open(username, 'wb') as file:
        # création du fichier
        pickle.dump(var2save, file)
