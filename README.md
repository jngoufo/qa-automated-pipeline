(English version will follow)

# Cadre de test automatisé pour un pipeline de données ETL

![Python version](https://img.shields.io/badge/python-3.11+-blue.svg)
![Framework](https://img.shields.io/badge/framework-Pytest-blue)
![Infrastructure](https://img.shields.io/badge/infra-Docker-blue)

## 📖 Résumé du projet

Ce projet est un cadre de test (`framework`) complet et de niveau professionnel, conçu et construit pour garantir la qualité, la fiabilité et la robustesse d'un pipeline de traitement de données (ETL).

L'objectif était de créer une suite de tests automatisés pour un script Python qui importe, nettoie, enrichit et stocke des données financières. Pour ce faire, j'ai mis en place une infrastructure de test conteneurisée, portable et entièrement isolée en utilisant **Docker** et **Pytest**.

## ✨ Fonctionnalités clés & points techniques

Ce framework a été construit en suivant les meilleures pratiques de l'industrie du test logiciel et du DevOps.

*   **🧪 Tests unitaires et d'intégration rigoureux :**
    *   **Tests unitaires :** ils valident la logique métier de fonctions pures en isolation (ex: nettoyage de données) en testant les cas nominaux et les cas d'erreur ("sad paths").
    *   **Tests d'intégration :** ils valident l'interaction correcte entre le code applicatif et les services externes, notamment la base de données.

*   **🐳 Environnement de test conteneurisé avec Docker :**
    *   Utilisation de `docker-compose` pour définir et lancer un environnement de test éphémère et totalement reproductible.
    *   Chaque session de test s'exécute contre une base de données MySQL neuve, garantissant qu'il n'y a aucune interférence entre les tests.
    *   Cette approche résout définitivement le problème du "ça marche sur ma machine" et assure une cohérence parfaite entre l'environnement de développement local et le futur environnement d'intégration continue (CI/CD).

*   **🛠️ Gestion avancée de l'environnement avec les fixtures Pytest :**
    *   Création d'une `fixture` personnalisée (`db_engine`) qui prépare et nettoie la base de données avant chaque test. Elle se connecte à la base de données Docker, détruit les anciennes tables et recrée le schéma à partir d'un fichier `.sql`, garantissant un état de départ propre pour chaque test.

*   **🔒 Gestion sécurisée des secrets :**
    *   Aucune information sensible (mots de passe, adresses de BDD) n'est écrite en dur dans le code.
    *   Le projet utilise des **variables d'environnement** lues depuis un fichier `.env` (ignoré par Git) grâce au plugin `pytest-dotenv`, suivant les meilleures pratiques de sécurité.

## 💻 Technologies utilisées

*   **Langage :** Python
*   **Framework de test :** Pytest
*   **Conteneurisation :** Docker, Docker compose
*   **Base de données :** MySQL
*   **Librairies clés :** SQLAlchemy, PyMySQL, Pandas, `pytest-mock`, `pytest-dotenv`
*   **Contrôle de version :** Git, GitHub

## 🚀 Démarrage Rapide (Comment lancer les tests)

Ce projet est conçu pour être simple à lancer, grâce à Docker.

### Prérequis

*   [Git](https://git-scm.com/)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et en cours d'exécution.

### Étapes

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/[!]VotreNomUtilisateur/pipeline-test-framework.git
    cd pipeline-test-framework
    ```

2.  **Lancer l'environnement de test (base de données) :**
    *ouvrez un premier terminal.* Cette commande va télécharger l'image MySQL et démarrer la base de données. Laissez ce terminal ouvert.
    ```bash
    docker-compose up
    ```

3.  **Lancer les tests :**
    *ouvrez un second terminal.*
    ```bash
    # Créer et activer l'environnement virtuel
    python -m venv venv
    .\venv\Scripts\activate

    # Installer les dépendances
    pip install -r requirements.txt

    # Lancer la suite de tests
    pytest
    ```
    Vous devriez voir les 4 tests passer avec succès.

4.  **Arrêter l'environnement :**
    retournez au premier terminal et appuyez sur `Ctrl + C`, puis lancez :
    ```bash
    docker-compose down -v
    ```

## 🎯 Ce que ce projet démontre

*   **Stratégie d'automatisation QA :** ma capacité à analyser une application backend, à définir une stratégie de test (unitaire, intégration) et à la mettre en œuvre.
*   **Compétences DevOps :** maîtrise de Docker pour créer des environnements fiables et portables, une compétence fondamentale pour l'intégration continue (CI/CD).
*   **Excellence technique en Python :** utilisation de `pytest`, de la gestion de dépendances (`requirements.txt`) et des meilleures pratiques de structuration de projet.
*   **Rigueur et résolution de problèmes :** capacité à déboguer des problèmes complexes à travers plusieurs couches technologiques (code, base de données, réseau, configuration d'environnement).

## 🔮 Améliorations futures

*   **Intégration continue (CI/CD) :** mettre en place un workflow GitHub Actions pour lancer automatiquement cette suite de tests à chaque `push` sur le dépôt.
*   **Rapports de test :** intégrer la génération de rapports de test (ex: `pytest-html`) et la couverture de code (`pytest-cov`).

## ✍️ Auteur

**[!] Justin N**
*   **LinkedIn :** [!] [Linkedin](https://www.linkedin.com/in/tester-software/)
*   **Email :** [!] justingoufo-tester@yahoo.com

*****************************************************************************************************************************************************************************************************************************************************
(English version)

# Automated testing framework for an ETL data pipeline

![Python version](https://img.shields.io/badge/python-3.11+-blue.svg)
![Framework](https://img.shields.io/badge/framework-Pytest-blue)
![Infrastructure](https://img.shields.io/badge/infra-Docker-blue)

## 📖 Project summary

This project is a complete, professional-grade testing framework designed and built to ensure the quality, reliability, and robustness of an ETL data processing pipeline.

The goal was to create an automated test suite for a Python script that imports, cleanses, enriches, and stores financial data. To achieve this, I set up a containerized, portable, and fully isolated testing infrastructure using Docker and Pytest.

## ✨ Key features & technical highlights

This framework was built following industry best practices in software testing and DevOps.

* **🧪 Rigorous unit and integration tests:**
* **Unit tests:** these validate the business logic of pure functions in isolation (e.g., data cleaning) by testing both nominal and error cases ("sad paths").
* **Integration tests:** these validate the correct interaction between the application code and external services, including the database.

* **🐳 Containerized test environment with Docker:**
* Use of `docker-compose` to define and launch an ephemeral and fully reproducible test environment.
* Each test session runs against a fresh MySQL database, ensuring no interference between tests.
* This approach definitively solves the "it works on my machine" problem and ensures perfect consistency between the local development environment and the future continuous integration (CI/CD) environment.

* **🛠️ Advanced environment management with Pytest fixtures:**
* Creation of a custom fixture (`db_engine`) that prepares and cleans the database before each test. It connects to the Docker database, destroys old tables, and recreates the schema from a `.sql` file, ensuring a clean starting state for each test.

* **🔒 Secure secrets management:**
* No sensitive information (passwords, database addresses) is hard-coded in the code.
* The project uses **environment variables** read from a `.env` file (ignored by Git) using the `pytest-dotenv` plugin, following security best practices.

## 💻 Technologies used

* **Language:** Python
* **Test Framework:** Pytest
* **Containerization:** Docker, Docker Compose
* **Database:** MySQL
* **Key Libraries:** SQLAlchemy, PyMySQL, Pandas, `pytest-mock`, `pytest-dotenv`
* **Version Control:** Git, GitHub

## 🚀 Quick start (how to run tests)

This project is designed to be easy to launch, thanks to Docker.

### Requirements

* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/[!]YourUserName/pipeline-test-framework.git
cd pipeline-test-framework
```

2. **Launch the test environment (database):**
*open a first terminal.* This command will download the MySQL image and start the database. Leave this terminal open.
```bash
docker-compose up
```

3. **Run the tests:**
*open a second terminal.*
```bash
# Create and activate the virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install the dependencies
pip install -r requirements.txt

# Run the test suite
pytest
```
You should see all 4 tests pass successfully.

4. **Stop the environment:**
return to the first terminal and press `Ctrl + C`, then launch:
```bash
docker-compose down -v
```

## 🎯 What this project demonstrates

* **QA automation strategy:** my ability to analyze a backend application, define a testing strategy (unit, integration), and implement it.
* **DevOps skills:** proficiency in Docker to create reliable and portable environments, a fundamental skill for continuous integration (CI/CD).
* **Technical excellence in Python:** use of `pytest`, dependency management (`requirements.txt`), and project structuring best practices.
* **Rigor and problem solving:** ability to debug complex problems across multiple technology layers (code, database, network, environment configuration).

## 🔮 Future improvements

* **Continuous integration (CI/CD):** set up a GitHub Actions workflow to automatically launch this test suite with each push to the repository.
* **Test reports:** integrate test report generation (e.g., `pytest-html`) and code coverage (`pytest-cov`).

## ✍️ Author

**[!] Justin N.**
* **LinkedIn:** [!] [Linkedin](https://www.linkedin.com/in/tester-software/)
* **Email:** [!] justingoufo-tester@yahoo.com
