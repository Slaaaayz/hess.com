#!/usr/bin/env python3
"""
Script pour télécharger automatiquement Stockfish pour Windows
"""
import os
import requests
import zipfile
import sys
from pathlib import Path

def download_stockfish():
    """Télécharge Stockfish automatiquement"""
    print("📥 Téléchargement de Stockfish...")
    
    # URL de Stockfish pour Windows
    stockfish_url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64-avx2.zip"
    
    # Créer le dossier de destination
    desktop_path = Path.home() / "Desktop" / "stockfish"
    desktop_path.mkdir(parents=True, exist_ok=True)
    
    zip_path = desktop_path / "stockfish.zip"
    
    try:
        print(f"📡 Téléchargement depuis: {stockfish_url}")
        response = requests.get(stockfish_url, stream=True)
        response.raise_for_status()
        
        # Sauvegarder le zip
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Téléchargé: {zip_path}")
        
        # Extraire le zip
        print("📦 Extraction en cours...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(desktop_path)
        
        # Trouver l'exécutable
        exe_files = list(desktop_path.rglob("stockfish*.exe"))
        if exe_files:
            stockfish_exe = exe_files[0]
            final_path = desktop_path / "stockfish.exe"
            
            # Déplacer vers le nom attendu
            if stockfish_exe != final_path:
                stockfish_exe.rename(final_path)
            
            print(f"✅ Stockfish installé: {final_path}")
            
            # Nettoyer
            zip_path.unlink()
            
            return True
        else:
            print("❌ Erreur: stockfish.exe non trouvé dans l'archive")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Installation automatique de Stockfish")
    
    # Vérifier si Stockfish existe déjà
    stockfish_path = Path.home() / "Desktop" / "stockfish" / "stockfish.exe"
    
    if stockfish_path.exists():
        print(f"✅ Stockfish déjà installé: {stockfish_path}")
        print("Rien à faire !")
    else:
        success = download_stockfish()
        
        if success:
            print("\n🎉 Installation réussie !")
            print("🔄 Vous pouvez maintenant redémarrer l'API")
        else:
            print("\n❌ Installation échouée")
            print("💡 Téléchargez manuellement depuis: https://stockfishchess.org/download/")
    
    input("\nAppuyez sur Entrée pour continuer...") 