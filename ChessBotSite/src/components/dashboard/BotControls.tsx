import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    PlayIcon,
    PauseIcon,
    BoltIcon,
    MicrophoneIcon,
    CogIcon,
    AdjustmentsHorizontalIcon
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

interface BotControlsProps {
    botStatus: BotStatus;
    setBotStatus: React.Dispatch<React.SetStateAction<BotStatus>>;
    user: User;
}

const BotControls: React.FC<BotControlsProps> = ({ botStatus, setBotStatus, user }) => {
    const [skillLevel, setSkillLevel] = useState(user.settings?.skillLevel || 1500);
    const [searchDepth, setSearchDepth] = useState(user.settings?.searchDepth || 3);

    const handleStartBot = () => {
        setBotStatus(prev => ({ ...prev, isRunning: true }));
        // Ici, vous ajouteriez l'appel API pour démarrer le bot
    };

    const handleStopBot = () => {
        setBotStatus(prev => ({ ...prev, isRunning: false }));
        // Ici, vous ajouteriez l'appel API pour arrêter le bot
    };

    const handleAutoPlayToggle = () => {
        setBotStatus(prev => ({ ...prev, autoPlay: !prev.autoPlay }));
    };

    const handleVoiceToggle = () => {
        setBotStatus(prev => ({ ...prev, voiceEnabled: !prev.voiceEnabled }));
    };

    const handleSkillLevelChange = (value: number) => {
        setSkillLevel(value);
        // Ici, vous ajouteriez l'appel API pour mettre à jour le niveau
    };

    const handleSearchDepthChange = (value: number) => {
        setSearchDepth(value);
        // Ici, vous ajouteriez l'appel API pour mettre à jour la profondeur
    };

    return (
        <div className="bot-controls">
            <motion.div
                className="controls-section"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h2>Contrôles du Bot</h2>

                {/* Main Controls */}
                <div className="main-controls">
                    <motion.button
                        className={`control-btn primary ${botStatus.isRunning ? 'stop' : 'start'}`}
                        onClick={botStatus.isRunning ? handleStopBot : handleStartBot}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        {botStatus.isRunning ? <PauseIcon /> : <PlayIcon />}
                        {botStatus.isRunning ? 'Arrêter le Bot' : 'Démarrer le Bot'}
                    </motion.button>
                </div>

                {/* Feature Toggles */}
                <div className="feature-toggles">
                    <div className="toggle-group">
                        <motion.button
                            className={`toggle-btn ${botStatus.autoPlay ? 'active' : ''}`}
                            onClick={handleAutoPlayToggle}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <BoltIcon />
                            <span>Auto-Play</span>
                            <div className={`toggle-switch ${botStatus.autoPlay ? 'on' : 'off'}`}>
                                <div className="toggle-handle"></div>
                            </div>
                        </motion.button>

                        <motion.button
                            className={`toggle-btn ${botStatus.voiceEnabled ? 'active' : ''}`}
                            onClick={handleVoiceToggle}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <MicrophoneIcon />
                            <span>Reconnaissance Vocale</span>
                            <div className={`toggle-switch ${botStatus.voiceEnabled ? 'on' : 'off'}`}>
                                <div className="toggle-handle"></div>
                            </div>
                        </motion.button>
                    </div>
                </div>

                {/* Advanced Settings */}
                <div className="advanced-settings">
                    <h3><AdjustmentsHorizontalIcon /> Paramètres Avancés</h3>

                    <div className="setting-group">
                        <label>Niveau de Compétence: <span className="value">{skillLevel}</span></label>
                        <input
                            type="range"
                            min="0"
                            max="3000"
                            value={skillLevel}
                            onChange={(e) => handleSkillLevelChange(Number(e.target.value))}
                            className="slider"
                        />
                        <div className="range-labels">
                            <span>Débutant (0)</span>
                            <span>Expert (3000)</span>
                        </div>
                    </div>

                    <div className="setting-group">
                        <label>Profondeur de Recherche: <span className="value">{searchDepth}</span></label>
                        <input
                            type="range"
                            min="1"
                            max="20"
                            value={searchDepth}
                            onChange={(e) => handleSearchDepthChange(Number(e.target.value))}
                            className="slider"
                        />
                        <div className="range-labels">
                            <span>Rapide (1)</span>
                            <span>Précis (20)</span>
                        </div>
                    </div>
                </div>

                {/* Status Information */}
                <div className="status-info">
                    <h3><CogIcon /> État Actuel</h3>
                    <div className="status-grid">
                        <div className="status-item">
                            <span className="label">État:</span>
                            <span className={`status ${botStatus.isRunning ? 'running' : 'stopped'}`}>
                                {botStatus.isRunning ? 'En marche' : 'Arrêté'}
                            </span>
                        </div>
                        <div className="status-item">
                            <span className="label">Auto-Play:</span>
                            <span className={`status ${botStatus.autoPlay ? 'enabled' : 'disabled'}`}>
                                {botStatus.autoPlay ? 'Activé' : 'Désactivé'}
                            </span>
                        </div>
                        <div className="status-item">
                            <span className="label">Voix:</span>
                            <span className={`status ${botStatus.voiceEnabled ? 'enabled' : 'disabled'}`}>
                                {botStatus.voiceEnabled ? 'Activée' : 'Désactivée'}
                            </span>
                        </div>
                        <div className="status-item">
                            <span className="label">Dernier coup:</span>
                            <span className="move">{botStatus.currentMove || 'Aucun'}</span>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default BotControls; 