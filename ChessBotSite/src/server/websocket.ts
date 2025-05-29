import { WebSocketServer, WebSocket } from 'ws';
import { createServer } from 'http';

interface BotStatus {
    isRunning: boolean;
    autoPlay: boolean;
    voiceEnabled: boolean;
    currentMove: string;
    currentFen: string;
    currentScore: number;
    gamesPlayed: number;
    winRate: number;
    lastActivity: string;
}

interface LogEntry {
    id: string;
    timestamp: string;
    type: 'info' | 'warning' | 'error' | 'success';
    message: string;
    details?: string;
}

class DashboardWebSocketServer {
    private wss: WebSocketServer;
    private clients: Set<WebSocket> = new Set();
    private botStatus: BotStatus = {
        isRunning: false,
        autoPlay: false,
        voiceEnabled: false,
        currentMove: '',
        currentFen: '',
        currentScore: 0,
        gamesPlayed: 0,
        winRate: 0,
        lastActivity: new Date().toISOString()
    };

    constructor(port: number = 5001) {
        const server = createServer();
        this.wss = new WebSocketServer({ server });

        this.wss.on('connection', (ws: WebSocket) => {
            console.log('Nouvelle connexion WebSocket');
            this.clients.add(ws);

            // Envoyer le statut actuel au nouveau client
            this.sendToClient(ws, {
                type: 'bot_status',
                status: this.botStatus
            });

            ws.on('message', (data: any) => {
                try {
                    const message = JSON.parse(data.toString());
                    this.handleMessage(ws, message);
                } catch (error) {
                    console.error('Erreur parsing message WebSocket:', error);
                }
            });

            ws.on('close', () => {
                console.log('Connexion WebSocket fermée');
                this.clients.delete(ws);
            });

            ws.on('error', (error: Error) => {
                console.error('Erreur WebSocket:', error);
                this.clients.delete(ws);
            });
        });

        server.listen(port, () => {
            console.log(`Serveur WebSocket écoute sur le port ${port}`);
        });

        // Simuler des mises à jour périodiques
        this.startSimulation();
    }

    private handleMessage(ws: WebSocket, message: any) {
        switch (message.type) {
            case 'bot_command':
                this.handleBotCommand(message.command, message.data);
                break;
            case 'get_status':
                this.sendToClient(ws, {
                    type: 'bot_status',
                    status: this.botStatus
                });
                break;
            default:
                console.log('Message non reconnu:', message);
        }
    }

    private handleBotCommand(command: string, data: any) {
        switch (command) {
            case 'start':
                this.botStatus.isRunning = true;
                this.broadcastLog('success', 'Bot démarré');
                break;
            case 'stop':
                this.botStatus.isRunning = false;
                this.broadcastLog('info', 'Bot arrêté');
                break;
            case 'toggle_autoplay':
                this.botStatus.autoPlay = !this.botStatus.autoPlay;
                this.broadcastLog('info', `Auto-play ${this.botStatus.autoPlay ? 'activé' : 'désactivé'}`);
                break;
            case 'toggle_voice':
                this.botStatus.voiceEnabled = !this.botStatus.voiceEnabled;
                this.broadcastLog('info', `Reconnaissance vocale ${this.botStatus.voiceEnabled ? 'activée' : 'désactivée'}`);
                break;
            case 'update_settings':
                if (data.skillLevel !== undefined) {
                    this.broadcastLog('info', `Niveau de compétence mis à jour: ${data.skillLevel}`);
                }
                if (data.searchDepth !== undefined) {
                    this.broadcastLog('info', `Profondeur de recherche mise à jour: ${data.searchDepth}`);
                }
                break;
        }

        this.botStatus.lastActivity = new Date().toISOString();
        this.broadcastBotStatus();
    }

    private sendToClient(ws: WebSocket, data: any) {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data));
        }
    }

    private broadcast(data: any) {
        this.clients.forEach(client => {
            this.sendToClient(client, data);
        });
    }

    private broadcastBotStatus() {
        this.broadcast({
            type: 'bot_status',
            status: this.botStatus
        });
    }

    private broadcastLog(type: LogEntry['type'], message: string, details?: string) {
        const log: LogEntry = {
            id: Date.now().toString() + Math.random(),
            timestamp: new Date().toISOString(),
            type,
            message,
            details
        };

        this.broadcast({
            type: 'log',
            log
        });
    }

    // Simuler l'activité du bot pour la démonstration
    private startSimulation() {
        setInterval(() => {
            if (this.botStatus.isRunning) {
                // Simuler des coups aléatoires
                const moves = ['e2e4', 'Nf3', 'd2d4', 'Bb5', 'O-O', 'Qd5'];
                const randomMove = moves[Math.floor(Math.random() * moves.length)];

                this.botStatus.currentMove = randomMove;
                this.botStatus.currentScore = Math.floor(Math.random() * 400) - 200; // Score entre -200 et +200
                this.botStatus.currentFen = `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 ${Math.floor(Math.random() * 50)}`;

                if (Math.random() < 0.3) { // 30% de chance de générer un log
                    const logTypes: LogEntry['type'][] = ['info', 'success', 'warning'];
                    const messages = [
                        'Analyse en cours...',
                        `Coup ${randomMove} calculé`,
                        'Position évaluée',
                        'Recherche dans la base de données',
                        'Calcul des variantes'
                    ];

                    const randomType = logTypes[Math.floor(Math.random() * logTypes.length)];
                    const randomMessage = messages[Math.floor(Math.random() * messages.length)];

                    this.broadcastLog(randomType, randomMessage);
                }

                if (Math.random() < 0.1) { // 10% de chance d'incrémenter les parties jouées
                    this.botStatus.gamesPlayed++;
                    this.botStatus.winRate = Math.random() * 100;
                }

                this.botStatus.lastActivity = new Date().toISOString();
                this.broadcastBotStatus();
            }
        }, 2000); // Toutes les 2 secondes

        // Simuler des logs périodiques
        setInterval(() => {
            if (Math.random() < 0.2) { // 20% de chance
                const logTypes: LogEntry['type'][] = ['info', 'warning', 'error'];
                const messages = [
                    'Connexion à Chess.com vérifiée',
                    'Mémoire du système vérifiée',
                    'Sauvegarde des paramètres',
                    'Vérification des mises à jour',
                    'Optimisation des performances'
                ];

                const randomType = logTypes[Math.floor(Math.random() * logTypes.length)];
                const randomMessage = messages[Math.floor(Math.random() * messages.length)];

                this.broadcastLog(randomType, randomMessage);
            }
        }, 5000); // Toutes les 5 secondes
    }

    // Méthodes publiques pour intégrer avec l'application Python
    public updateBotStatus(status: Partial<BotStatus>) {
        Object.assign(this.botStatus, status);
        this.botStatus.lastActivity = new Date().toISOString();
        this.broadcastBotStatus();
    }

    public sendLog(type: LogEntry['type'], message: string, details?: string) {
        this.broadcastLog(type, message, details);
    }

    public executeMove(move: string, fen: string, score: number) {
        this.botStatus.currentMove = move;
        this.botStatus.currentFen = fen;
        this.botStatus.currentScore = score;
        this.botStatus.lastActivity = new Date().toISOString();

        this.broadcastBotStatus();
        this.broadcastLog('success', `Coup exécuté: ${move}`, `Score: ${score}`);
    }
}

// Démarrer le serveur WebSocket
const wsServer = new DashboardWebSocketServer(5001);

export default wsServer; 