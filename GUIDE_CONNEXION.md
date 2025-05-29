# 🔧 Guide de Résolution des Problèmes de Connexion

## Problème: ChessBotApp ne peut pas se connecter à l'API

### ✅ Solutions testées et corrigées :

1. **Import du module ChessBotApi** ✅ RÉSOLU
   - Changé l'import relatif dans `api.py`
   - Installé le package en mode développement

2. **Problème de commande Python** ✅ RÉSOLU  
   - Créé `start_api.ps1` qui trouve automatiquement Python
   - Corrigé les chemins Windows

3. **Chemin Stockfish** ✅ RÉSOLU
   - Configuré pour Windows: `C:\Users\trist\Desktop\stockfish\stockfish.exe`

### 🚀 Comment démarrer l'API :

**Méthode recommandée (PowerShell):**
```powershell
PowerShell -ExecutionPolicy Bypass -File start_api.ps1
```

**Méthode alternative:**
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" run_api.py
```

### 🔍 Diagnostic des problèmes :

1. **Vérifier que l'API est démarrée:**
   ```powershell
   netstat -an | findstr :5000
   ```

2. **Vérifier les logs:**
   ```powershell
   Get-Content chessbot_api.log -Tail 10
   ```

3. **Tester la connexion:**
   ```powershell
   & "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" test_api_connection.py
   ```

### 🛠️ Solutions aux problèmes courants :

#### Problème: "Connexion refusée"
- Vérifiez que l'API est démarrée
- Vérifiez le pare-feu Windows
- Essayez de redémarrer l'API

#### Problème: "Module not found"
- Réinstallez le package : `pip install -e .`
- Vérifiez le PYTHONPATH

#### Problème: "Stockfish non trouvé"
- Téléchargez Stockfish depuis stockfishchess.org
- Placez `stockfish.exe` dans `C:\Users\trist\Desktop\stockfish\`

### 📋 Checklist de fonctionnement :

- [ ] Python installé et accessible
- [ ] API démarrée (port 5000 ouvert) 
- [ ] Stockfish installé au bon endroit
- [ ] Pare-feu Windows autorise localhost:5000
- [ ] ChessBotApp utilise la bonne URL (http://localhost:5000/analyze)

### 🎯 État actuel :

✅ L'API fonctionne (logs montrent des réponses HTTP 200)  
✅ Stockfish calcule correctement les coups  
✅ Format de réponse JSON correct  
⚠️  Problème de connexion réseau local à diagnostiquer

### 🔗 Prochaines étapes :

1. Vérifier le pare-feu Windows
2. Tester avec curl ou Postman
3. Redémarrer l'API si nécessaire
4. Vérifier la configuration réseau locale 