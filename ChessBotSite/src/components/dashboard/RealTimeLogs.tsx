import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    EyeIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XMarkIcon,
    ArrowPathIcon
} from '@heroicons/react/24/outline';

interface LogEntry {
    id: string;
    timestamp: string;
    type: 'info' | 'warning' | 'error' | 'success';
    message: string;
    details?: string;
}

const RealTimeLogs: React.FC = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [autoScroll, setAutoScroll] = useState(true);
    const [filter, setFilter] = useState<'all' | 'info' | 'warning' | 'error' | 'success'>('all');
    const [isConnected, setIsConnected] = useState(false);

    const addLog = (type: LogEntry['type'], message: string, details?: string) => {
        const newLog: LogEntry = {
            id: Date.now().toString() + Math.random(),
            timestamp: new Date().toISOString(),
            type,
            message,
            details
        };

        setLogs(prev => [newLog, ...prev].slice(0, 100)); // Garder seulement les 100 derniers logs
    };

    useEffect(() => {
        // Simuler une connexion
        setIsConnected(true);
        addLog('info', 'Connexion aux logs en temps réel établie');

        // Simuler quelques logs pour la démonstration
        const simulateLogs = () => {
            const mockLogs = [
                { type: 'info', message: 'Bot démarré avec succès' },
                { type: 'success', message: 'Coup e2e4 exécuté' },
                { type: 'info', message: 'Analyse en cours...' },
                { type: 'warning', message: 'Connexion internet lente détectée' },
                { type: 'success', message: 'Meilleur coup trouvé: Nf3' },
                { type: 'error', message: 'Échec de l\'exécution du coup' },
            ];

            mockLogs.forEach((log, index) => {
                setTimeout(() => {
                    addLog(log.type as LogEntry['type'], log.message);
                }, index * 2000);
            });
        };

        simulateLogs();

        // Simuler des logs périodiques
        const interval = setInterval(() => {
            if (Math.random() < 0.3) { // 30% de chance
                const logTypes: LogEntry['type'][] = ['info', 'warning', 'success'];
                const messages = [
                    'Connexion à Chess.com vérifiée',
                    'Mémoire du système vérifiée',
                    'Sauvegarde des paramètres',
                    'Vérification des mises à jour',
                    'Optimisation des performances',
                    'Analyse de position terminée',
                    'Cache mis à jour',
                    'Synchronisation des données'
                ];

                const randomType = logTypes[Math.floor(Math.random() * logTypes.length)];
                const randomMessage = messages[Math.floor(Math.random() * messages.length)];

                addLog(randomType, randomMessage);
            }
        }, 4000);

        return () => {
            clearInterval(interval);
            setIsConnected(false);
        };
    }, []);

    const clearLogs = () => {
        setLogs([]);
    };

    const getIcon = (type: LogEntry['type']) => {
        switch (type) {
            case 'error':
                return <ExclamationTriangleIcon className="log-icon error" />;
            case 'warning':
                return <ExclamationTriangleIcon className="log-icon warning" />;
            case 'success':
                return <InformationCircleIcon className="log-icon success" />;
            default:
                return <InformationCircleIcon className="log-icon info" />;
        }
    };

    const filteredLogs = filter === 'all' ? logs : logs.filter(log => log.type === filter);

    return (
        <div className="real-time-logs">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="logs-container"
            >
                <div className="logs-header">
                    <div className="header-left">
                        <h2><EyeIcon /> Logs en Temps Réel</h2>
                        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                            <div className="status-indicator"></div>
                            {isConnected ? 'Connecté' : 'Déconnecté'}
                        </div>
                    </div>

                    <div className="header-controls">
                        <div className="filter-group">
                            {['all', 'info', 'success', 'warning', 'error'].map((filterType) => (
                                <button
                                    key={filterType}
                                    className={`filter-btn ${filter === filterType ? 'active' : ''} ${filterType}`}
                                    onClick={() => setFilter(filterType as any)}
                                >
                                    {filterType === 'all' ? 'Tous' : filterType.charAt(0).toUpperCase() + filterType.slice(1)}
                                </button>
                            ))}
                        </div>

                        <div className="action-buttons">
                            <button
                                className={`toggle-btn ${autoScroll ? 'active' : ''}`}
                                onClick={() => setAutoScroll(!autoScroll)}
                                title="Auto-scroll"
                            >
                                <ArrowPathIcon />
                            </button>
                            <button
                                className="clear-btn"
                                onClick={clearLogs}
                                title="Effacer les logs"
                            >
                                <XMarkIcon />
                            </button>
                        </div>
                    </div>
                </div>

                <div className="logs-content">
                    <div className="logs-list" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                        <AnimatePresence>
                            {filteredLogs.map((log) => (
                                <motion.div
                                    key={log.id}
                                    className={`log-entry ${log.type}`}
                                    initial={{ opacity: 0, x: -20, height: 0 }}
                                    animate={{ opacity: 1, x: 0, height: 'auto' }}
                                    exit={{ opacity: 0, x: 20, height: 0 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <div className="log-content">
                                        <div className="log-main">
                                            {getIcon(log.type)}
                                            <div className="log-text">
                                                <div className="log-message">{log.message}</div>
                                                {log.details && (
                                                    <div className="log-details">{log.details}</div>
                                                )}
                                            </div>
                                        </div>
                                        <div className="log-timestamp">
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>

                    {filteredLogs.length === 0 && (
                        <div className="no-logs">
                            <EyeIcon />
                            <p>Aucun log à afficher</p>
                            <small>Les logs apparaîtront ici en temps réel</small>
                        </div>
                    )}
                </div>

                <div className="logs-footer">
                    <div className="logs-count">
                        {filteredLogs.length} log{filteredLogs.length > 1 ? 's' : ''} affiché{filteredLogs.length > 1 ? 's' : ''}
                    </div>
                    <div className="auto-scroll-toggle">
                        <label>
                            <input
                                type="checkbox"
                                checked={autoScroll}
                                onChange={(e) => setAutoScroll(e.target.checked)}
                            />
                            Défilement automatique
                        </label>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default RealTimeLogs; 