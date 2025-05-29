#!/usr/bin/env node

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Démarrage du backend ChessBot...\n');

// Vérification des prérequis
const checkRequirements = () => {
    console.log('🔍 Vérification des prérequis...');

    // Vérifier node_modules
    if (!fs.existsSync('node_modules')) {
        console.log('❌ node_modules manquant');
        console.log('💡 Lancez: npm install');
        return false;
    }

    // Vérifier si le client Prisma existe
    if (!fs.existsSync('node_modules/.prisma') && !fs.existsSync('prisma/dev.db')) {
        console.log('❌ Base de données non configurée');
        console.log('💡 Lancez: npm run setup');
        return false;
    }

    console.log('✅ Prérequis vérifiés');
    return true;
};

// Vérifier si le port est libre
const checkPort = (port) => {
    return new Promise((resolve) => {
        const net = require('net');
        const server = net.createServer();

        server.listen(port, () => {
            server.once('close', () => {
                resolve(true);
            });
            server.close();
        });

        server.on('error', () => {
            resolve(false);
        });
    });
};

// Fonction principale
const startBackend = async () => {
    try {
        // Vérifier les prérequis
        if (!checkRequirements()) {
            process.exit(1);
        }

        // Vérifier le port 5000
        console.log('🔍 Vérification du port 5000...');
        const portFree = await checkPort(5000);
        if (!portFree) {
            console.log('❌ Le port 5000 est déjà utilisé');
            console.log('💡 Fermez l\'application qui utilise ce port ou changez le port');

            // Tenter de trouver qui utilise le port
            exec('netstat -ano | findstr :5000', (error, stdout) => {
                if (stdout) {
                    console.log('📋 Processus utilisant le port 5000:');
                    console.log(stdout);
                }
            });

            process.exit(1);
        }
        console.log('✅ Port 5000 disponible');

        // Démarrer le serveur
        console.log('🚀 Démarrage du serveur backend...\n');

        const serverProcess = spawn('npx', ['tsx', 'src/server/server.ts'], {
            stdio: 'inherit',
            shell: true
        });

        // Gestion des signaux
        process.on('SIGINT', () => {
            console.log('\n🛑 Arrêt du serveur...');
            serverProcess.kill('SIGINT');
            process.exit(0);
        });

        serverProcess.on('error', (error) => {
            console.error('❌ Erreur démarrage serveur:', error.message);

            if (error.message.includes('tsx')) {
                console.log('💡 tsx non trouvé. Installation...');
                exec('npm install tsx --save-dev', (error) => {
                    if (!error) {
                        console.log('✅ tsx installé. Relancez le script.');
                    }
                });
            }
        });

        serverProcess.on('exit', (code) => {
            if (code !== 0) {
                console.log(`❌ Le serveur s'est arrêté avec le code ${code}`);
                console.log('\n🔧 Solutions possibles:');
                console.log('   - Vérifiez les logs ci-dessus pour les erreurs');
                console.log('   - Lancez: npm install');
                console.log('   - Lancez: npm run setup');
                console.log('   - Vérifiez que le port 5000 est libre');
            }
        });

    } catch (error) {
        console.error('❌ Erreur:', error.message);
        process.exit(1);
    }
};

startBackend(); 