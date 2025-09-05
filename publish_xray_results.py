# Fichier: publish_xray_results.py (Version finale pour reportlog)
import json
import os
import requests
from dotenv import load_dotenv
import re

load_dotenv()

# --- Configuration ---
JIRA_BASE_URL = "https://monwebmestre.atlassian.net"
PROJECT_KEY = "II"
REPORT_FILE = ".report.json" # Le nouveau nom de fichier

def get_xray_token():
    """Obtient un token d'authentification depuis l'API Xray."""
    client_id = os.getenv("XRAY_CLIENT_ID")
    client_secret = os.getenv("XRAY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("XRAY_CLIENT_ID et XRAY_CLIENT_SECRET doivent être définis dans .env")

    token_endpoint = "https://xray.cloud.getxray.app/api/v2/authenticate"
    payload = {"client_id": client_id, "client_secret": client_secret}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(token_endpoint, json=payload, headers=headers)
    response.raise_for_status() # Lève une erreur si la requête échoue
    return response.json()

def parse_pytest_report():
    try:
        with open(REPORT_FILE) as f:
            report = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Erreur: Le fichier de rapport '{REPORT_FILE}' est introuvable ou invalide.")
        return []

    tests = []
    # Le regex pour trouver les IDs dans le nom du test (ex: test_II_61_...)
    pattern = re.compile(rf"test_({PROJECT_KEY}_\d+)_")

    for test in report.get('tests', []):
        match = pattern.search(test['nodeid'])
        if match:
            # On a trouvé un ID ! On remplace l'underscore par un tiret
            test_key = match.group(1).replace('_', '-')
            status = 'PASS' if test['outcome'] == 'passed' else 'FAIL'
            tests.append({'testKey': test_key, 'status': status})
    return tests
    
def publish_to_xray(tests, token):
    if not tests:
        print("Aucun test marqué trouvé. Rien à publier.")
        return

    endpoint = f"https://xray.cloud.getxray.app/api/v2/import/execution/junit?projectKey={PROJECT_KEY}"
    
    # On lit le contenu brut du rapport XML
    with open("report.xml", "r") as f: # Assure-toi d'avoir généré report.xml
        report_data = f.read()

    # L'authentification se fait avec un "Bearer Token"
    headers = {
        'Content-Type': 'application/xml',
        'Authorization': f'Bearer {token}'
    }
    
    print(f"Publication des résultats vers Xray pour le projet {PROJECT_KEY}...")
    response = requests.post(endpoint, data=report_data, headers=headers)

    if response.status_code == 200:
        test_exec_key = response.json().get('key')
        print(f"Succès ! Résultats publiés dans l'exécution de test : {test_exec_key}")
        print(f"URL: {JIRA_BASE_URL}/browse/{test_exec_key}")
    else:
        print(f"Erreur lors de la publication (Status Code: {response.status_code}):")
        print(response.text)

if __name__ == "__main__":
    # On utilise le rapport XML, plus simple pour cette API
    print("Génération du rapport JUnit XML...")
    os.system('pytest -v --junitxml="report.xml"')

    print("Obtention du token d'authentification Xray...")
    auth_token = get_xray_token()
    
    # Le parsing n'est plus nécessaire, on envoie le fichier brut
    publish_to_xray(True, auth_token) # On passe True juste pour indiquer qu'il y a des tests