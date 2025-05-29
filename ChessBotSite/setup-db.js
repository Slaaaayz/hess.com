const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Configuration de la base de données ChessBot...');

// Vérifier si Prisma est installé
const checkPrisma = () => {
    return new Promise((resolve, reject) => {
        exec('npx prisma --version', (error, stdout, stderr) => {
            if (error) {
                console.log('📦 Installation de Prisma...');
                exec('npm install prisma @prisma/client', (error) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve();
                    }
                });
            } else {
                console.log('✅ Prisma détecté');
                resolve();
            }
        });
    });
};

// Générer le client Prisma
const generateClient = () => {
    return new Promise((resolve, reject) => {
        console.log('🔄 Génération du client Prisma...');
        exec('npx prisma generate', (error, stdout, stderr) => {
            if (error) {
                console.error('❌ Erreur génération client:', stderr);
                reject(error);
            } else {
                console.log('✅ Client Prisma généré');
                resolve();
            }
        });
    });
};

// Créer et migrer la base de données
const setupDatabase = () => {
    return new Promise((resolve, reject) => {
        console.log('🗄️ Configuration de la base de données...');
        exec('npx prisma db push', (error, stdout, stderr) => {
            if (error) {
                console.error('❌ Erreur base de données:', stderr);
                reject(error);
            } else {
                console.log('✅ Base de données configurée');
                resolve();
            }
        });
    });
};

// Fonction principale
const setup = async () => {
    try {
        await checkPrisma();
        await generateClient();
        await setupDatabase();

        console.log('\n🎉 Configuration terminée !');
        console.log('📋 Étapes suivantes :');
        console.log('   1. npm run dev:server    (dans un terminal)');
        console.log('   2. npm run dev           (dans un autre terminal)');
        console.log('   3. Ouvrir http://localhost:5173');

    } catch (error) {
        console.error('\n❌ Erreur lors de la configuration:', error.message);
        console.log('\n🔧 Solutions possibles :');
        console.log('   - Vérifiez que Node.js est installé');
        console.log('   - Lancez "npm install" pour installer les dépendances');
        console.log('   - Vérifiez les permissions du dossier');
    }
};

setup(); 