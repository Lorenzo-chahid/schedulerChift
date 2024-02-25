import schedule
import time
import xmlrpc.client
import json
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Paramètres de connexion Odoo
url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_PASSWORD")


def fetch_and_save_contacts():
    print("Récupération des contacts...")

    # Connexion au serveur Odoo
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})

    if uid is False:
        raise Exception("Échec de l'authentification, mauvais identifiants")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    # Récupération des contacts
    contacts = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [[]],
        {"fields": ["name", "email", "phone"]},
    )

    # Sauvegarde des contacts dans un fichier JSON
    with open("contacts.json", "w") as json_file:
        json.dump(contacts, json_file, indent=4)

    print("Contacts récupérés et sauvegardés.")


# Planification de la tâche
schedule.every(30).seconds.do(fetch_and_save_contacts)

# Boucle pour exécuter les tâches planifiées
while True:
    schedule.run_pending()
    time.sleep(1)
