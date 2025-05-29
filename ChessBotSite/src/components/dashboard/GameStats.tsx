import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    ChartBarIcon,
    TrophyIcon,
    ClockIcon,
    FireIcon
} from '@heroicons/react/24/outline';

interface User {
    id: number;
    username: string;
    email: string;
    subscriptionEndDate: string;
    settings?: {
        skillLevel: number;
        searchDepth: number;
    };
}

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

interface GameStatsProps {
    user: User;
    botStatus: BotStatus;
}

interface GameData {
    date: string;
    result: 'win' | 'loss' | 'draw';
    duration: number;
    avgScore: number;
}

const GameStats: React.FC<GameStatsProps> = ({ botStatus }) => {
    const [gameHistory, setGameHistory] = useState<GameData[]>([]);
    const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');

    useEffect(() => {
        // Simuler des données de parties (à remplacer par de vraies données API)
        const mockData: GameData[] = [
            { date: '2024-05-29', result: 'win', duration: 25, avgScore: 150 },
            { date: '2024-05-28', result: 'win', duration: 32, avgScore: 200 },
            { date: '2024-05-27', result: 'loss', duration: 18, avgScore: -100 },
            { date: '2024-05-26', result: 'draw', duration: 45, avgScore: 50 },
            { date: '2024-05-25', result: 'win', duration: 28, avgScore: 175 },
        ];
        setGameHistory(mockData);
    }, [timeRange]);

    const calculateStats = () => {
        const wins = gameHistory.filter(game => game.result === 'win').length;
        const losses = gameHistory.filter(game => game.result === 'loss').length;
        const draws = gameHistory.filter(game => game.result === 'draw').length;
        const total = gameHistory.length;

        const winRate = total > 0 ? (wins / total) * 100 : 0;
        const avgDuration = total > 0 ? gameHistory.reduce((sum, game) => sum + game.duration, 0) / total : 0;
        const avgScore = total > 0 ? gameHistory.reduce((sum, game) => sum + game.avgScore, 0) / total : 0;

        return { wins, losses, draws, total, winRate, avgDuration, avgScore };
    };

    const stats = calculateStats();

    // Utiliser botStatus pour afficher des statistiques en temps réel
    const currentGamesPlayed = botStatus.gamesPlayed || stats.total;
    const currentWinRate = botStatus.winRate || stats.winRate;

    return (
        <div className="game-stats">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="stats-container"
            >
                <div className="stats-header">
                    <h2><ChartBarIcon /> Statistiques de Jeu</h2>
                    <div className="time-selector">
                        {['7d', '30d', '90d'].map((range) => (
                            <button
                                key={range}
                                className={`time-btn ${timeRange === range ? 'active' : ''}`}
                                onClick={() => setTimeRange(range as any)}
                            >
                                {range === '7d' ? '7 jours' : range === '30d' ? '30 jours' : '90 jours'}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="stats-grid">
                    <motion.div
                        className="stat-card wins"
                        whileHover={{ scale: 1.02 }}
                    >
                        <div className="stat-icon">
                            <TrophyIcon />
                        </div>
                        <div className="stat-content">
                            <h3>Victoires</h3>
                            <div className="stat-value">{stats.wins}</div>
                            <div className="stat-subtitle">Taux: {currentWinRate.toFixed(1)}%</div>
                        </div>
                    </motion.div>

                    <motion.div
                        className="stat-card games"
                        whileHover={{ scale: 1.02 }}
                    >
                        <div className="stat-icon">
                            <ChartBarIcon />
                        </div>
                        <div className="stat-content">
                            <h3>Parties Totales</h3>
                            <div className="stat-value">{currentGamesPlayed}</div>
                            <div className="stat-subtitle">{stats.draws} nulles</div>
                        </div>
                    </motion.div>

                    <motion.div
                        className="stat-card duration"
                        whileHover={{ scale: 1.02 }}
                    >
                        <div className="stat-icon">
                            <ClockIcon />
                        </div>
                        <div className="stat-content">
                            <h3>Durée Moyenne</h3>
                            <div className="stat-value">{stats.avgDuration.toFixed(0)}min</div>
                            <div className="stat-subtitle">Par partie</div>
                        </div>
                    </motion.div>

                    <motion.div
                        className="stat-card score"
                        whileHover={{ scale: 1.02 }}
                    >
                        <div className="stat-icon">
                            <FireIcon />
                        </div>
                        <div className="stat-content">
                            <h3>Score Moyen</h3>
                            <div className="stat-value">{stats.avgScore > 0 ? '+' : ''}{stats.avgScore.toFixed(0)}</div>
                            <div className="stat-subtitle">Centipions</div>
                        </div>
                    </motion.div>
                </div>

                {/* Performance Chart */}
                <div className="performance-chart">
                    <h3>Performance Récente</h3>
                    <div className="chart-container">
                        <div className="chart-bars">
                            {gameHistory.slice(0, 10).reverse().map((game, index) => (
                                <motion.div
                                    key={index}
                                    className={`chart-bar ${game.result}`}
                                    initial={{ height: 0 }}
                                    animate={{ height: `${Math.abs(game.avgScore) / 5}px` }}
                                    transition={{ delay: index * 0.1 }}
                                    title={`${game.date}: ${game.result} (${game.avgScore})`}
                                >
                                    <div className="bar-tooltip">
                                        <span className="date">{new Date(game.date).toLocaleDateString()}</span>
                                        <span className={`result ${game.result}`}>
                                            {game.result === 'win' ? 'Victoire' :
                                                game.result === 'loss' ? 'Défaite' : 'Nulle'}
                                        </span>
                                        <span className="score">{game.avgScore > 0 ? '+' : ''}{game.avgScore}</span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Recent Games */}
                <div className="recent-games">
                    <h3>Parties Récentes</h3>
                    <div className="games-list">
                        {gameHistory.slice(0, 5).map((game, index) => (
                            <motion.div
                                key={index}
                                className="game-item"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <div className="game-date">
                                    {new Date(game.date).toLocaleDateString()}
                                </div>
                                <div className={`game-result ${game.result}`}>
                                    {game.result === 'win' ? 'Victoire' :
                                        game.result === 'loss' ? 'Défaite' : 'Nulle'}
                                </div>
                                <div className="game-duration">
                                    {game.duration} min
                                </div>
                                <div className="game-score">
                                    {game.avgScore > 0 ? '+' : ''}{game.avgScore}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default GameStats; 