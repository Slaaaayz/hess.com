# 🚀 Démarrage Rapide ChessBot Dashboard

## Problème: Le backend s'arrête immédiatement

### Solution étape par étape:

#### 1. Installation des dépendances
```bash
cd ChessBotSite
npm install
```

#### 2. Configuration de la base de données
```bash
npm run setup
```

#### 3. Démarrage du backend (version sécurisée)
```bash
npm run start-backend
```

**OU** méthode classique:
```bash
npm run dev:server
```

#### 4. Démarrage du frontend (dans un nouveau terminal)
```bash
npm run dev
```

### 🔍 Diagnostic des problèmes

#### Le serveur s'arrête avec "Cannot find module"
```bash
# Réinstaller les dépendances
rm -rf node_modules package-lock.json
npm install
```

#### Erreur "Port already in use"
```bash
# Windows
netstat -ano | findstr :5000
# Tuer le processus qui utilise le port

# Linux/Mac  
lsof -ti:5000 | xargs kill
```

#### Erreur Prisma
```bash
# Regenerer le client Prisma
npx prisma generate
npx prisma db push
```

#### Erreur TypeScript
```bash
# Installer tsx si manquant
npm install -D tsx
```

### 📋 Vérification que tout fonctionne

1. **Backend** : http://localhost:5000/api/health
   - Doit retourner `{"status": "OK"}`

2. **Frontend** : http://localhost:5173
   - Doit afficher la page d'accueil

3. **Dashboard** : http://localhost:5173/dashboard
   - Doit afficher le dashboard (après login)

### 🆘 Si ça ne fonctionne toujours pas

1. **Vérifiez la console** pour les erreurs spécifiques
2. **Redémarrez** votre terminal
3. **Vérifiez** que Node.js version ≥ 18
4. **Essayez** de supprimer `node_modules` et réinstaller

```bash
# Reset complet
rm -rf node_modules package-lock.json
npm install
npm run setup
npm run start-backend
```

### 📞 Commandes utiles

```bash
# Voir tous les processus sur les ports
netstat -ano | findstr :5000
netstat -ano | findstr :5173

# Version Node.js
node --version

# Logs détaillés
DEBUG=* npm run dev:server
``` 