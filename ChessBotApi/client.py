import requests
import sys
import os
from pathlib import Path

def analyze_chess_image(image_path):
    """
    Envoie une image d'échiquier à l'API et récupère la notation FEN.
    
    Args:
        image_path (str): Chemin vers l'image à analyser
        
    Returns:
        str: Notation FEN de la position
    """
    # Vérifier si le fichier existe
    if not os.path.exists(image_path):
        print(f"❌ Erreur: Le fichier {image_path} n'existe pas")
        return None
    
    # URL de l'API
    api_url = "http://localhost:5000/analyze"
    
    try:
        # Envoyer l'image
        print(f"📤 Envoi de l'image {image_path} à l'API...")
        with open(image_path, "rb") as f:
            files = {"image": f}
            response = requests.post(api_url, files=files)
        
        # Vérifier la réponse
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success":
                print("✅ Analyse réussie!")
                print(f"📋 Notation FEN: {result['fen']}")
                return result["fen"]
            else:
                print(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter à l'API. Vérifiez que le serveur est en cours d'exécution.")
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
    
    return None

def main():
    # Vérifier les arguments
    if len(sys.argv) != 2:
        print("Usage: python -m ChessBotApi.client <chemin_vers_image>")
        print("Exemple: python -m ChessBotApi.client test/image.png")
        sys.exit(1)
    
    # Analyser l'image
    image_path = sys.argv[1]
    fen = analyze_chess_image(image_path)
    
    if fen:
        # Sauvegarder le FEN dans un fichier
        output_file = Path(image_path).with_suffix('.fen')
        try:
            with open(output_file, 'w') as f:
                f.write(fen)
            print(f"💾 FEN sauvegardé dans {output_file}")
        except Exception as e:
            print(f"⚠️ Impossible de sauvegarder le FEN: {str(e)}")

if __name__ == "__main__":
    main() 