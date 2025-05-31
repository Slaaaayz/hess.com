#!/bin/bash

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Fonction pour afficher les messages
print_message() {
    echo -e "\e[1;34m==>\e[0m $1"
}

print_error() {
    echo -e "\e[1;31m==>\e[0m $1"
}

print_success() {
    echo -e "\e[1;32m==>\e[0m $1"
}

# Vérifier si le script est exécuté en tant que root
if [ "$EUID" -eq 0 ]; then
    print_error "Ne pas exécuter ce script en tant que root"
    exit 1
fi

# Mettre à jour les paquets
print_message "Mise à jour des paquets système..."
sudo apt update

# Installation de Docker
if ! command_exists docker; then
    print_message "Installation de Docker..."
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    print_success "Docker installé. Vous devrez vous déconnecter et vous reconnecter pour que les changements prennent effet."
else
    print_success "Docker est déjà installé"
fi

# Installation de Docker Compose
if ! command_exists docker-compose; then
    print_message "Installation de Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installé"
else
    print_success "Docker Compose est déjà installé"
fi

# Installation de Python et pip
if ! command_exists python3; then
    print_message "Installation de Python 3..."
    sudo apt install -y python3 python3-pip python3-tk
    sudo apt install -y pip
    print_success "Python 3 installé"
else
    print_success "Python 3 est déjà installé"
    print_message "Vérification/installation de python3-tk..."
    sudo apt install -y python3-tk
    sudo apt install -y pip
fi

# Installation de Node.js et npm
if ! command_exists node; then
    print_message "Installation de Node.js et npm..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
    print_success "Node.js et npm installés"
else
    print_success "Node.js est déjà installé"
fi

# Installation de Stockfish
if ! command_exists stockfish; then
    print_message "Installation de Stockfish..."
    sudo apt install -y stockfish
    print_success "Stockfish installé"
else
    print_success "Stockfish est déjà installé"
fi

# Vérification et création du fichier .env
if [ -f ChessBotSite/.env ]; then
    print_message "Le fichier .env existe déjà dans ChessBotSite/."
    read -p "Voulez-vous le remplacer ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "Remplacement du fichier .env..."
        cat > ChessBotSite/.env << EOL
DATABASE_URL="mysql://hess_user:hess_password@localhost:3307/hess_db"
PORT=5000
EOL
        print_success "Fichier .env remplacé dans ChessBotSite/"
    else
        print_message "Le fichier .env n'a pas été modifié"
    fi
else
    print_message "Création du fichier .env dans ChessBotSite/..."
    cat > ChessBotSite/.env << EOL
DATABASE_URL="mysql://hess_user:hess_password@localhost:3307/hess_db"
PORT=5000
EOL
    print_success "Fichier .env créé dans ChessBotSite/"
fi

# Installation des dépendances Node.js et configuration de Prisma
print_message "Installation des dépendances Node.js et configuration de Prisma..."
cd ChessBotSite
npm install
npx prisma db pull
npx prisma db push
npx prisma generate
print_success "Configuration de Prisma terminée"

# Retour à la racine du projet
cd ..

print_message "Installation terminée !"
print_message "N'oubliez pas de vous déconnecter et de vous reconnecter pour que les changements de groupe Docker prennent effet."
