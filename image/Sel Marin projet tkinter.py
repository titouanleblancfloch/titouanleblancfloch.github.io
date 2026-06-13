import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
import pandas as pd
import ctypes
import threading
import subprocess
from q4 import importer_tous_les_csv

# Activer le mode DPI pour éviter le flou sur Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print("DPI Scaling non supporté :", e)

# Connexion MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'selmarin-tdb-te'
}

# Requêtes prédéfinies
REQUETES = {
    "Total des quantités entrées par produit":
        "SELECT numPdt, SUM(qteEnt) AS total_entree FROM ENTREE GROUP BY numPdt",
    "Produits avec plus de 1000 en stock":
        "SELECT numPdt, SUM(qteEnt) AS total_entree FROM ENTREE GROUP BY numPdt HAVING total_entree > 1000",
    "Clients sans achat":
        "SELECT * FROM CLIENT WHERE numCli NOT IN (SELECT numCli FROM SORTIE)",
    "Augmenter stock produit 1 de 500 unités":
        "UPDATE PRODUIT SET stockPdt = stockPdt + 500 WHERE numPdt = 1",
    "Ajouter une nouvelle entrée":
        "INSERT INTO ENTREE (numEnt, dateEnt, qteEnt, numSau, numPdt) VALUES (1, '2024-08-15', 700, 2, 1)",
    "Supprimer une sortie spécifique":
        "DELETE FROM SORTIE WHERE numSort = 20242;",
    "Créer une vue des produits et prix en 2024":
        """DROP VIEW IF EXISTS VUE_PRODUITS_PRIX;
        CREATE VIEW VUE_PRODUITS_PRIX AS 
        SELECT p.numPdt, p.libPdt, c.annee, c.prix_achat, c.prix_vente 
        FROM PRODUIT p 
        JOIN COUTE c ON p.numPdt = c.numPdt 
        WHERE c.annee = 2024""",
    "Afficher la vue des prix 2024":
        "SELECT * FROM VUE_PRODUITS_PRIX",
    "Chiffre d'affaires total par produit en 2024":
        "SELECT c.numPdt, SUM(c.qteSort * cp.prix_vente) AS chiffre_affaires FROM CONCERNER c JOIN COUTE cp ON c.numPdt = cp.numPdt WHERE cp.annee = 2024 GROUP BY c.numPdt",
    "Produits plus chers que la moyenne de 2024":
        "SELECT numPdt, prix_vente FROM COUTE WHERE annee = 2024 AND prix_vente > (SELECT AVG(prix_vente) FROM COUTE WHERE annee = 2024)"
}

# Exécution SQL
def executer_requete(query, callback=None):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.description:
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            if callback:
                callback(rows, columns)

        conn.commit()
        cursor.close()
        conn.close()

        # Afficher un message de succès
        messagebox.showinfo("Succès", "Requête exécutée avec succès !")

    except mysql.connector.Error as e:
        messagebox.showerror("Erreur SQL", f"Erreur : {e}")

# Affichage dans le Treeview
def afficher_resultats(rows, columns):
    for widget in frame_resultats.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(frame_resultats, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for row in rows:
        tree.insert("", "end", values=row)

    tree.pack(expand=True, fill="both")

# Afficher une table
def afficher_table(nom_table):
    executer_requete(f"SELECT * FROM {nom_table} LIMIT 100", afficher_resultats)

# Utiliser "q4.py" pour importer les CSV
  

def importer_csv():
    try:
        importer_tous_les_csv()  # appel correct
        messagebox.showinfo("Succès", "Les fichiers CSV ont été importés avec succès !")
    except FileNotFoundError as e:
        messagebox.showerror("Erreur", f"Fichier introuvable : {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

# Exécution requête dans thread
def executer_requete_predefinie():
    choix = combo_requetes.get()
    if choix in REQUETES:
        query = REQUETES[choix]
        if "UPDATE" in query or "INSERT" in query or "DELETE" in query:
            threading.Thread(target=executer_requete, args=(query, refresh_table)).start()
        else:
            executer_requete(query, afficher_resultats)

# Rafraîchir après modif
def refresh_table(rows=None, columns=None):
    root.after(0, afficher_table, 'PRODUIT')

# Fonction pour créer la base de données
def creer_base_de_donnees():
    try:
        # Connexion au serveur MySQL sans spécifier de base de données
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        # Commande SQL pour créer la base de données
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Succès", f"Base de données '{DB_CONFIG['database']}' créée avec succès !")
    except mysql.connector.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création de la base : {e}")

# Fonction pour créer les tables et insérer les données
def creer_tables_et_inserer_donnees():
    try:
        # Importer le script SQL pour créer les tables
        with open("selmarin_create.sql", "r", encoding="utf-8") as f:
            create_script = f.read()

        # Connexion à la base de données
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Exécuter chaque commande SQL pour créer les tables
        for statement in create_script.split(";"):
            if statement.strip():  # Ignorer les lignes vides
                cursor.execute(statement.strip())

        # Importer le script SQL pour insérer les données
        with open("selmarin_insert.sql", "r", encoding="utf-8") as f:
            insert_script = f.read()

        # Exécuter chaque commande SQL pour insérer les données
        for statement in insert_script.split(";"):
            if statement.strip():  # Ignorer les lignes vides
                cursor.execute(statement.strip())

        # Valider les modifications
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Succès", "Tables créées et données insérées avec succès !")
    except FileNotFoundError as e:
        messagebox.showerror("Erreur", f"Fichier introuvable : {e}")
    except mysql.connector.Error as e:
        messagebox.showerror("Erreur SQL", f"Erreur SQL : {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

# Interface principale
root = tk.Tk()
root.title("Gestion Sel Marin")
root.geometry("1400x800")
root.configure(bg="#f7f7f7")

# Logo
def charger_logo():
    try:
        image = Image.open("logo2.png")
        image = image.resize((100, 100))
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print("Erreur logo :", e)
        return None

logo = charger_logo()
if logo:
    tk.Label(root, image=logo, bg="#f7f7f7").pack(side="top", anchor="w", padx=20, pady=20)

# Bouton arrondi stylé
def bouton_arrondi(master, text, command, color, fg="white"):
    bouton = tk.Button(master, text=text, command=command, bg=color, fg=fg,
                       font=("Arial", 12, "bold"), relief="flat", bd=0)
    bouton.pack(fill="x", pady=10, padx=10)  # Réduire les marges pour économiser de l'espace
    bouton.config(width=25, highlightthickness=0,
                  activebackground=color, activeforeground=fg)
    return bouton

# Menu gauche sans barre de défilement
frame_tables_container = tk.Frame(root, bg="#ffffff", relief="sunken", bd=2)
frame_tables_container.pack(side="left", padx=20, pady=20, fill="y")

frame_tables = tk.Frame(frame_tables_container, bg="#ffffff")
frame_tables.pack(fill="both", expand=True)

# Titre du menu
tk.Label(frame_tables, text="Gestion de la Base de Données", font=("Arial", 16, "bold"),
         bg="#f7f7f7", fg="#333333").pack(pady=20)

# Boutons pour la gestion de la base de données
bouton_arrondi(frame_tables, "Créer Base de Données", creer_base_de_donnees, "#0077b6")
bouton_arrondi(frame_tables, "Créer Tables et Insérer Données", creer_tables_et_inserer_donnees, "#0077b6")

# Séparateur
tk.Label(frame_tables, text="", bg="#ffffff").pack(pady=10)

# Boutons pour afficher les tables
tk.Label(frame_tables, text="Tables principales", font=("Arial", 14, "bold"),
         bg="#f7f7f7", fg="#333333").pack(pady=10)

tables = ["SAUNIER", "CLIENT", "PRODUIT", "ENTREE", "SORTIE", "CONCERNER", "COUTE"]
for table in tables:
    bouton_arrondi(frame_tables, table, lambda t=table: afficher_table(t), "#29abe2")

# Séparateur
tk.Label(frame_tables, text="", bg="#ffffff").pack(pady=10)

# Boutons pour l'importation
tk.Label(frame_tables, text="Importation", font=("Arial", 14, "bold"),
         bg="#f7f7f7", fg="#333333").pack(pady=10)

bouton_arrondi(frame_tables, "Importer fichiers CSV", importer_csv, "#0077b6")

# Requêtes prédéfinies
frame_requetes = tk.Frame(root, bg="#f7f7f7", relief="sunken", bd=2)
frame_requetes.pack(side="top", pady=10)

tk.Label(frame_requetes, text="Exécuter une requête SQL", font=("Arial", 14, "bold"),
         bg="#f7f7f7", fg="#333333").pack(pady=10)

combo_requetes = ttk.Combobox(frame_requetes, width=80, values=list(REQUETES.keys()), font=("Arial", 12))
combo_requetes.pack(pady=5)

# Bouton Exécuter (bleu clair)
bouton_arrondi(frame_requetes, "Exécuter", executer_requete_predefinie, "#29abe2")

# Zone des résultats
frame_resultats = tk.Frame(root, bg="white", relief="sunken", bd=2)
frame_resultats.pack(side="bottom", expand=True, fill="both", padx=20, pady=20)

root.mainloop()




