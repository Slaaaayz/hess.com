# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import os

CHESS_URL = "https://www.chess.com/play/online"
# Sélecteur plus précis pour l'échiquier
CHESSBOARD_SELECTOR = 'wc-chess-board.board'  # Sélecteur précis pour l'échiquier
OUTPUT_IMAGE = "chessboard_capture.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("🌐 Navigation vers Chess.com...")
        await page.goto(CHESS_URL)
        
        print("➡️ Connecte-toi et lance une partie dans la fenêtre qui s'ouvre.")
        input("✅ Quand l'échiquier est bien visible, appuie sur Entrée ici pour démarrer la capture continue...")

        # Attendre que l'échiquier soit visible avec un timeout plus long
        print("🔍 Recherche de l'échiquier...")
        try:
            await page.wait_for_selector(CHESSBOARD_SELECTOR, timeout=60000)  # 60 secondes
            print("✅ Échiquier trouvé!")
        except Exception as e:
            print(f"❌ Erreur lors de la recherche de l'échiquier: {e}")
            await page.screenshot(path="debug_full_page.png")
            print("📸 Capture d'écran de debug sauvegardée sous 'debug_full_page.png'")
            await browser.close()
            return

        # Boucle de capture continue
        print("🔄 Début de la capture continue. Ferme la fenêtre pour arrêter.")
        i = 0
        try:
            while True:
                chessboard = await page.query_selector(CHESSBOARD_SELECTOR)
                if chessboard:
                    await chessboard.screenshot(path=OUTPUT_IMAGE)
                    print(f"[{i}] ✅ Capture enregistrée sous {OUTPUT_IMAGE}")
                else:
                    print(f"[{i}] ❌ Échiquier non trouvé.")
                i += 1
                await asyncio.sleep(1)  # Pause d'1 seconde
        except Exception as e:
            print(f"❌ Erreur pendant la capture continue : {e}")
        finally:
            await browser.close()
            print("🚪 Fenêtre fermée, capture arrêtée.")

    # Vérification de l'existence du fichier
    if os.path.exists(OUTPUT_IMAGE):
        print("✅ Capture réussie : le fichier existe.")
    else:
        print("❌ Erreur : le fichier n'a pas été créé.")

if __name__ == "__main__":
    asyncio.run(main()) 