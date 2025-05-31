#!/bin/bash

# Fonction pour afficher les messages
print_message() {
    echo -e "\e[1;34m==>\e[0m $1"
}

print_success() {
    echo -e "\e[1;32m==>\e[0m $1"
}

print_message "Arrêt des conteneurs Docker..."
sudo docker compose down
print_success "Conteneurs Docker arrêtés."

print_message "Arrêt des serveurs Node.js (dev:server et dev)..."
# Tue tous les processus node qui contiennent dev:server ou dev
pkill -f "npm run dev:server"
pkill -f "npm run dev"
print_success "Serveurs Node.js arrêtés."

print_message "Arrêt de l'API Python..."
pkill -f "python3 -m ChessBotApi.api"
print_success "API Python arrêtée."

print_message "Arrêt du bot Python..."
pkill -f "python3 ChessBotApp/main.py"
print_success "Bot Python arrêté."

print_message "Tous les services ont été arrêtés !" 