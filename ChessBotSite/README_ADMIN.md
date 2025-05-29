# 🛡️ ChessBot Admin Dashboard

## Configuration Admin

### Compte Administrateur
- **Email**: `admin`
- **Mot de passe**: `admin`
- **ID en base**: `4`
- **Rôle**: `admin`

## Démarrage du Système

### 1. Démarrer le Backend
```bash
cd ChessBotSite
node start-server.js
```

### 2. Démarrer le Frontend
```bash
cd ChessBotSite
npm run dev
```

### 3. Accès Admin
- **Page de connexion admin**: `admin-login.html`
- **Dashboard principal**: `index.html` (auto-détection du rôle admin)

## Fonctionnalités Admin

### 📊 Statistiques Générales
- Nombre total d'utilisateurs
- Utilisateurs standard vs administrateurs
- Nombre de clés API actives
- Utilisateurs récents

### 👥 Gestion des Utilisateurs
- **Voir tous les utilisateurs** avec leurs informations complètes
- **Supprimer des utilisateurs** (sauf son propre compte admin)
- Voir les clés API associées à chaque utilisateur
- Informations sur les abonnements

### 🔑 Gestion des Clés API
- **Voir toutes les clés API** de tous les utilisateurs
- **Supprimer des clés API** spécifiques
- Voir le statut (active/inactive) de chaque clé
- Informations sur le propriétaire de chaque clé

## API Endpoints Admin

### Authentification
- Header requis: `x-user-id: 4` (ID de l'admin)

### Routes Utilisateurs
- `GET /api/admin/users` - Liste tous les utilisateurs
- `GET /api/admin/users/:id` - Détails d'un utilisateur
- `PUT /api/admin/users/:id` - Modifier un utilisateur
- `DELETE /api/admin/users/:id` - Supprimer un utilisateur

### Routes Clés API
- `GET /api/admin/apikeys` - Liste toutes les clés API
- `DELETE /api/admin/apikeys/:id` - Supprimer une clé API

### Routes Statistiques
- `GET /api/admin/stats` - Statistiques générales

## Base de Données

### Table User (modifiée)
```sql
ALTER TABLE User ADD COLUMN role VARCHAR(50) DEFAULT 'user';
```

### Utilisateur Admin créé
```sql
INSERT INTO User (username, email, password, role, subscriptionEndDate) 
VALUES ('Administrateur', 'admin', 'admin', 'admin', '2026-05-29');
```

## Sécurité

⚠️ **Important**: Ce système est pour démonstration. En production :
- Hasher les mots de passe
- Implémenter une authentification JWT robuste
- Ajouter des logs d'audit
- Validation des entrées côté serveur
- Rate limiting

## Structure des Fichiers

```
ChessBotSite/
├── admin-login.html          # Page de connexion admin
├── start-server.js           # Script de démarrage serveur
├── src/
│   ├── components/
│   │   ├── AdminDashboard.tsx    # Dashboard admin React
│   │   └── Dashboard.tsx         # Dashboard principal (détection auto)
│   └── server/
│       ├── admin.ts              # Routes API admin
│       └── server.ts             # Serveur principal
└── README_ADMIN.md           # Ce fichier
```

## Workflow d'utilisation

1. **Se connecter en tant qu'admin** via `admin-login.html`
2. **Être redirigé automatiquement** vers le dashboard admin
3. **Gérer les utilisateurs et clés API** via l'interface web
4. **Voir les statistiques** en temps réel

Le système détecte automatiquement si l'utilisateur connecté est un admin (rôle `admin` ou email `admin`) et affiche l'interface d'administration au lieu du dashboard utilisateur standard. 