# ♟️ ChessBot – Projet B2 Ynov

> ⚠️ **Avertissement : Ce projet est un logiciel de triche pour chess.com, développé uniquement à des fins éducatives et de recherche. Il est strictement interdit d'utiliser ce logiciel sur des plateformes réelles, en compétition ou contre d'autres joueurs sans leur consentement. L'auteur décline toute responsabilité en cas d'usage abusif.**

## 🚀 Présentation
ChessBot est un assistant d'échecs complet pour [chess.com](https://chess.com), combinant vision par ordinateur, intelligence artificielle (Stockfish), interface graphique personnalisable, commandes vocales et gestion de profils utilisateurs.

---

## 🛠️ Prérequis
- **Docker** (Pour la base de données et phpmyadmin)
- **Python 3.9+** (pour les modules ScreenBot, API, IHM)
- **Node.js + npm** (pour le backend et frontend web)
- **Fichier** `.env à placer dans `ChessBotSite/ (voir plus bas)

---

## ⚡ Installation & Lancement

### 1. **Lancer la base de données (Docker)**
Assure toi d'avoir lancer la base de données avec docker compose a la racine du projet:
```bash
docker compose up -d
```

### 2. **Configurer l'environnement web**
- Place le fichier `.env` à la racine de `ChessBotSite/` :
```env
DATABASE_URL="mysql://hess_user:hess_password@localhost:3307/hess_db"
PORT=5000
```

### 3. **Installer les dépendances web**
```bash
cd ChessBotSite
npm install
```

### 4. **Lancer le backend et le frontend web**
Dans `ChessBotSite/` :
```bash
npm run dev:server   # Lance le backend (API Node.js)
npm run dev          # Lance le frontend (React.js)
```

### 5. **Lancer l'API Python (analyse d'échiquier, Stockfish, etc.)**
Dans la racine du projet :
```bash
python3 -m ChessBotApi.api 
```

### 6. **Lancer le bot (IHM PyQt, overlay)**
Toujours à la racine du projet :
```bash
python3 ChessBotApp/main.py
```

---
## 🔑 Obtention de la clé API (obligatoire)

Avant de pouvoir utiliser ChessBot, vous devez d'abord obtenir une **clé API** via le site web du projet :

1. **Lancez le site web** (voir étapes plus bas pour lancer le backend et le frontend).
2. Rendez-vous sur l'URL du site (ex : http://localhost:5173).
3. Créez un compte ou connectez-vous.
4. Achetez une clé API via l'interface prévue.
5. Récupérez votre clé API personnelle.
6. **Dans l'application ChessBotApp (PyQt), allez dans l'onglet Options et renseignez votre clé API.**

> ⚠️ **Sans clé API valide, l'API refusera toute requête et l'application ne fonctionnera pas.**

---

## 📝 Conseils pour le premier lancement
- Vérifie que tous les ports nécessaires sont libres (3307 pour MySQL, 5000 pour le backend, 5173 pour le frontend, 5001 pour l'API Python).
- Si tu rencontres des problèmes de dépendances Python, installe-les avec :
  ```bash
  pip install -r requirements.txt
  ```
- Pour la reconnaissance vocale, un micro fonctionnel et de bonne qualité est necessaire, si le microphone de votre laptop est utilisable alors assurez vous de baisser la sensibilité de votre micro afin de ne pas perturber l'ia quand vous allez annoncer vos coup.
- Les logs et erreurs sont affichés dans l'IHM et dans les consoles respectives.

---

## 📂 Structure du projet
- `ChessBotSite/` : Frontend & backend web (Node.js, React, API REST)
- `ChessBotApi/`   : API Python (analyse image, Stockfish, endpoints)
- `ChessBotApp/`   : Application PyQt (IHM, overlay, commandes vocales)

---

## 🔗 Liens utiles
- [Chess.com](https://chess.com)
- [Stockfish](https://stockfishchess.org/)

---
**Bon jeu !**