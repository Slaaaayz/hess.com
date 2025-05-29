const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Démarrage du serveur ChessBot Dashboard...');

// Chemin vers le serveur TypeScript
const serverPath = path.join(__dirname, 'src', 'server', 'server.ts');

// Commande pour exécuter le serveur avec ts-node
const command = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const args = ['ts-node', '--esm', serverPath];

const serverProcess = spawn(command, args, {
    stdio: 'inherit',
    shell: true,
    cwd: __dirname
});

serverProcess.on('error', (error) => {
    console.error('❌ Erreur lors du démarrage du serveur:', error);
});

serverProcess.on('close', (code) => {
    console.log(`📋 Serveur fermé avec le code: ${code}`);
});

// Gestion propre de l'arrêt
process.on('SIGINT', () => {
    console.log('\n⏹️ Arrêt du serveur...');
    serverProcess.kill('SIGINT');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n⏹️ Arrêt du serveur...');
    serverProcess.kill('SIGTERM');
    process.exit(0);
}); 