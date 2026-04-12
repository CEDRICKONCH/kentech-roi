-- Script d'initialisation de la base de données Kentech ROI
-- Exécuter : mysql -u root -p < init_db.sql

CREATE DATABASE IF NOT EXISTS kentech_roi
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE kentech_roi;

-- La table est créée automatiquement par SQLAlchemy au démarrage.
-- Ce script sert uniquement à créer la base si elle n'existe pas.

SHOW DATABASES LIKE 'kentech_roi';
