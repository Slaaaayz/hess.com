# 🎯 Dashboard ChessBot - Interface Simplifiée

## 📋 Vue d'ensemble

Le Dashboard ChessBot a été simplifié pour se concentrer sur l'essentiel : **la gestion de votre clé API**. 

## 🚀 Démarrage Rapide

### 1. Installation et lancement
```bash
cd ChessBotSite
npm install
npm run setup
npm run start-backend
```

Dans un autre terminal :
```bash
npm run dev
```

### 2. Accès au Dashboard
- Ouvrez votre navigateur : `http://localhost:5173`
- Cliquez sur "Dashboard" ou allez directement à `http://localhost:5173/dashboard`

## 🔑 Fonctionnalités

### Clé API (Section principale)
- **Affichage sécurisé** : Votre clé API personnelle
- **Copie en un clic** : Bouton pour copier la clé dans le presse-papier
- **Régénération** : Possibilité de créer une nouvelle clé si nécessaire
- **Exemples d'usage** : Code prêt à utiliser en Curl et Python

### Sections supplémentaires
- **Profil** : Gestion des informations utilisateur
- **Sécurité** : Changement de mot de passe
- **Notifications** : Paramètres d'alertes

## 💻 Utilisation de la Clé API

### Exemple Curl
```bash
curl -H "Authorization: Bearer VOTRE_CLE_API" \
     http://localhost:5000/api/bot/status
```

### Exemple Python
```python
import requests

headers = {'Authorization': 'Bearer VOTRE_CLE_API'}
response = requests.get('http://localhost:5000/api/bot/status', headers=headers)
print(response.json())
```

### Intégration avec ChessBotApp
Copiez votre clé API et utilisez-la dans vos scripts Python :

```python
from dashboard_integration import dashboard_integration

# Utiliser votre clé API
API_KEY = "sk-chessbot-xxxxxxxxxxxxx"  # Votre clé copiée du dashboard

# Envoyer des données au dashboard
dashboard_integration.log_message("Bot démarré", "info")
dashboard_integration.execute_move("e2e4", "fen_position", 25)
```

## 🎨 Interface

- **Design moderne** : Interface sombre avec thème glassmorphism
- **Responsive** : S'adapte aux écrans mobiles et desktop
- **Animations fluides** : Transitions et effets visuels
- **Accessibilité** : Navigation intuitive et claire

## 🔧 Configuration

Le Dashboard utilise un utilisateur test par défaut. Pour personnaliser :

1. **Nom d'utilisateur** : Modifiable dans la section Profil
2. **Email** : Changeable dans les paramètres
3. **Abonnement** : Configuré pour 30 jours par défaut

## 📱 Navigation Simplifiée

Le Dashboard se concentre sur 4 sections essentielles :

1. **🔑 Clé API** (par défaut) - Gestion de votre accès API
2. **👤 Profil** - Informations personnelles  
3. **🛡️ Sécurité** - Mot de passe et authentification
4. **🔔 Notifications** - Paramètres d'alertes

## ✨ Avantages de cette version simplifiée

- **Focus sur l'essentiel** : Clé API directement accessible
- **Interface épurée** : Moins de distractions
- **Performance optimisée** : Chargement plus rapide
- **Maintenance facilitée** : Code simplifié et modulaire

## 🎯 Utilisation Typique

1. **Ouvrir le Dashboard**
2. **Copier la clé API** (section par défaut)
3. **Intégrer dans vos projets** avec les exemples fournis
4. **Gérer votre profil** si nécessaire

---

**✅ Prêt à utiliser !** Votre Dashboard simplifié est optimisé pour une utilisation rapide et efficace de l'API ChessBot. 