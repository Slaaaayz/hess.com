# HoneyPot Project

Un système de honeypot avancé avec analyse d'attaques et interface de gestion.

## Fonctionnalités principales

- Communication sécurisée TLS/SSL entre le honeypot et le serveur d'analyse
- Support de multiples services simulés (SSH, HTTP, FTP)
- Base de données relationnelle avec audit des actions
- Détection d'attaques basée sur l'IA
- Interface utilisateur pour la gestion et la visualisation
- Système de logs avancé avec archivage automatique

## Installation

1. Cloner le repository
2. Créer un environnement virtuel Python
3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration

1. Copier `.env.example` vers `.env`
2. Configurer les variables d'environnement dans `.env`

## Structure du projet

```
honeypot/
├── app/                    # Application principale
│   ├── models/            # Modèles de données
│   ├── services/          # Services (honeypot, analyse, etc.)
│   ├── utils/             # Utilitaires
│   └── templates/         # Templates HTML
├── config/                # Configuration
├── tests/                 # Tests
└── docs/                  # Documentation
```

## Démarrage

```bash
python app.py
```

## Licence

MIT 