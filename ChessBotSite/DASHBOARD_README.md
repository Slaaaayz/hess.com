# 🏆 ChessBot Dashboard - Documentation Complète

## 📋 Vue d'ensemble

Le Dashboard ChessBot est une interface web en temps réel qui vous permet de surveiller, contrôler et analyser votre bot d'échecs. Il offre une vue d'ensemble complète de l'activité de votre bot avec des statistiques détaillées, des logs en temps réel et des contrôles avancés.

## ✨ Fonctionnalités Principales

### 🎮 Contrôles du Bot
- **Démarrage/Arrêt** : Contrôlez l'état de votre bot en un clic
- **Auto-Play** : Activez/désactivez l'exécution automatique des coups
- **Reconnaissance Vocale** : Contrôlez le bot par commandes vocales
- **Paramètres Avancés** : Ajustez le niveau de compétence (0-3000) et la profondeur de recherche (1-20)

### 📊 Statistiques en Temps Réel
- **Parties Jouées** : Nombre total de parties
- **Taux de Victoire** : Pourcentage de victoires
- **Durée Moyenne** : Temps moyen par partie
- **Score Moyen** : Performance en centipions
- **Graphiques de Performance** : Visualisation des résultats récents

### 📝 Logs en Temps Réel
- **Filtrage par Type** : Info, Succès, Avertissement, Erreur
- **Horodatage Précis** : Chaque log avec timestamp
- **Auto-scroll** : Défilement automatique des nouveaux logs
- **Effacement** : Nettoyage des logs en un clic

### ⚙️ Paramètres Utilisateur
- **Profil** : Gestion des informations utilisateur
- **Sécurité** : Changement de mot de passe
- **Notifications** : Configuration des alertes
- **Clé API** : Gestion de l'accès API

## 🚀 Installation et Configuration

### Prérequis
```bash
# Node.js et npm
node --version  # v18.0.0 ou plus récent
npm --version   # v8.0.0 ou plus récent

# Python (pour l'intégration)
python --version  # v3.8 ou plus récent
```

### Installation du Dashboard
```bash
# 1. Naviguer vers le dossier ChessBotSite
cd ChessBotSite

# 2. Installer les dépendances
npm install

# 3. Démarrer le frontend (port 5173)
npm run dev

# 4. Dans un nouveau terminal, démarrer le backend (port 5000)
npm run dev:server
```

### Intégration avec ChessBotApp

```bash
# 1. Copier le script d'intégration
cp ChessBotSite/dashboard_integration.py ChessBotApp/

# 2. Naviguer vers ChessBotApp
cd ChessBotApp

# 3. Installer les dépendances Python nécessaires
pip install requests

# 4. Patcher main.py pour l'intégration dashboard
python dashboard_integration.py patch

# 5. Tester l'intégration
python dashboard_integration.py test
```

## 🎯 Utilisation

### Accès au Dashboard
1. Ouvrez votre navigateur
2. Allez à `http://localhost:5173`
3. Connectez-vous ou créez un compte
4. Accédez au dashboard via `http://localhost:5173/dashboard`

### Navigation
- **Vue d'ensemble** : Aperçu rapide de l'état du bot
- **Contrôles** : Paramètres et commandes du bot
- **Statistiques** : Analyse détaillée des performances
- **Logs** : Surveillance en temps réel
- **Paramètres** : Configuration utilisateur

### Démarrage du Bot avec Dashboard
```bash
# 1. Démarrer le dashboard web
cd ChessBotSite
npm run dev &
npm run dev:server &

# 2. Lancer votre bot (main.py modifié)
cd ChessBotApp
python main.py
```

## 📱 Interface Utilisateur

### Header
- **Informations Utilisateur** : Nom et statut d'abonnement
- **Actions Rapides** : Boutons Démarrer/Arrêter, Auto-Play, Voix
- **Indicateurs d'État** : Statut en temps réel du bot

### Cartes de Statut
- **État du Bot** : En marche / Arrêté
- **Dernier Coup** : Notation algébrique du dernier mouvement
- **Score Actuel** : Évaluation en centipions
- **Parties Jouées** : Compteur total

### Contrôles Avancés
- **Curseurs de Réglage** : Ajustement précis des paramètres
- **Interrupteurs Visuels** : Interface moderne pour les options
- **Validation en Temps Réel** : Sauvegarde automatique des changements

## 🔧 Configuration Avancée

### Variables d'Environnement
Créez un fichier `.env` dans `ChessBotSite/` :
```env
# Base de données
DATABASE_URL="mysql://hess_user:hess_password@localhost:3307/hess_db"

# JWT Secret
JWT_SECRET="votre_secret_jwt_super_securise"

# API Configuration
API_PORT=5000
DASHBOARD_PORT=5173

# Dashboard Integration
DASHBOARD_API_URL="http://localhost:5000"
```

### Personnalisation du Dashboard

#### Couleurs et Thème
Modifiez `ChessBotSite/src/components/Dashboard.css` :
```css
:root {
    --primary-color: #22c55e;    /* Vert principal */
    --bg-gradient: linear-gradient(135deg, #0a0b0f 0%, #1a1c25 100%);
    --glass-bg: rgba(255, 255, 255, 0.05);
    --border-color: rgba(255, 255, 255, 0.1);
}
```

#### Paramètres Bot Personnalisés
Modifiez `ChessBotApp/dashboard_integration.py` :
```python
# Personnaliser les paramètres par défaut
class DashboardIntegration:
    def __init__(self):
        self.default_skill_level = 1500  # Votre niveau préféré
        self.default_search_depth = 3    # Votre profondeur préférée
        self.update_interval = 5         # Secondes entre les mises à jour
```

## 🐛 Dépannage

### Problèmes Courants

#### Le Dashboard ne se charge pas
```bash
# Vérifier que les services sont démarrés
netstat -an | grep :5173  # Frontend
netstat -an | grep :5000  # Backend

# Redémarrer les services
npm run dev
npm run dev:server
```

#### Erreurs de Connexion WebSocket
```bash
# Vérifier les ports
lsof -i :5001

# Relancer l'intégration
cd ChessBotApp
python dashboard_integration.py test
```

#### Bot non détecté
```bash
# Vérifier que main.py est patché
grep "dashboard_integration" main.py

# Re-patcher si nécessaire
python dashboard_integration.py patch
```

### Logs de Débogage

#### Frontend (React)
```bash
# Ouvrir les outils développeur (F12)
# Onglet Console pour voir les erreurs JavaScript
# Onglet Network pour vérifier les appels API
```

#### Backend (Express)
```bash
# Activer les logs détaillés
DEBUG=* npm run dev:server
```

#### Integration Python
```python
# Ajouter dans dashboard_integration.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Sécurité

### Authentification
- **JWT Tokens** : Authentification sécurisée
- **Hachage bcrypt** : Mots de passe protégés
- **Sessions Expirables** : Déconnexion automatique

### Recommandations
1. **Changez le JWT_SECRET** en production
2. **Utilisez HTTPS** pour l'accès distant
3. **Configurez un firewall** pour les ports 5000 et 5173
4. **Sauvegardez régulièrement** la base de données

## 📈 Optimisation des Performances

### Frontend
```bash
# Build optimisé pour production
npm run build

# Servir les fichiers statiques
npm run preview
```

### Backend
```javascript
// Optimisation Express dans auth.ts
app.use(compression());
app.use(helmet());
```

### Base de Données
```sql
-- Index pour optimiser les requêtes
CREATE INDEX idx_user_email ON Users(email);
CREATE INDEX idx_game_date ON GameHistory(date);
```

## 🤝 Contribution

### Structure du Projet
```
ChessBotSite/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx          # Composant principal
│   │   ├── Dashboard.css          # Styles
│   │   └── dashboard/
│   │       ├── BotControls.tsx    # Contrôles du bot
│   │       ├── GameStats.tsx      # Statistiques
│   │       ├── RealTimeLogs.tsx   # Logs en temps réel
│   │       └── SettingsPanel.tsx  # Paramètres
│   ├── server/
│   │   ├── auth.ts               # API backend
│   │   └── websocket.ts          # WebSocket (optionnel)
│   └── utils/
├── prisma/
│   └── schema.prisma             # Schéma base de données
└── dashboard_integration.py      # Script d'intégration Python
```

### Développement
```bash
# Installer en mode développement
npm install --save-dev

# Lancer les tests
npm test

# Linter le code
npm run lint
```

## 📞 Support

### Documentation
- **React** : https://react.dev/
- **Framer Motion** : https://www.framer.com/motion/
- **Prisma** : https://www.prisma.io/docs/

### Communauté
- **Issues GitHub** : Pour signaler des bugs
- **Discussions** : Pour poser des questions
- **Wiki** : Documentation communautaire

---

## 🎉 Félicitations !

Vous avez maintenant un dashboard complet pour surveiller et contrôler votre bot d'échecs en temps réel. Le système est conçu pour être extensible et vous pouvez facilement ajouter de nouvelles fonctionnalités selon vos besoins.

**Bon jeu ! ♟️** 