-- Fichier: tests/schema.sql

-- On s'assure de supprimer les tables si elles existent, pour un nettoyage parfait
DROP TABLE IF EXISTS historique;
DROP TABLE IF EXISTS titres;

-- On recrée les tables à partir de zéro
CREATE TABLE titres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    nom_entreprise VARCHAR(255)
);

CREATE TABLE historique (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre_id INT NOT NULL,
    date DATE NOT NULL,
    valeur DECIMAL(15, 2),
    FOREIGN KEY (titre_id) REFERENCES titres(id) ON DELETE CASCADE
);