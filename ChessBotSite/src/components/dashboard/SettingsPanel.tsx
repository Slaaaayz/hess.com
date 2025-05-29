import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    KeyIcon,
    UserIcon,
    ShieldCheckIcon,
    BellIcon,
    ClipboardDocumentIcon,
    ArrowPathIcon,
    ExclamationTriangleIcon,
    TrashIcon
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

interface ApiKey {
    id: number;
    keyValue: string;
    name: string;
    createdAt: string;
    updatedAt: string;
}

interface SettingsPanelProps {
    user: User;
    setUser: React.Dispatch<React.SetStateAction<User | null>>;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ user, setUser }) => {
    const [activeSection, setActiveSection] = useState('api');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [apiKey, setApiKey] = useState<ApiKey | null>(null);

    // États locaux pour les paramètres
    const [profileData, setProfileData] = useState({
        username: user.username,
        email: user.email
    });

    const [notifications, setNotifications] = useState({
        gameStart: true,
        gameEnd: true,
        errors: true,
        updates: false
    });

    // Charger la clé API au démarrage
    useEffect(() => {
        loadApiKey();
    }, [user.id]);

    const loadApiKey = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/apikeys/${user.id}`);
            const data = await response.json();

            if (data.apiKeys && data.apiKeys.length > 0) {
                setApiKey(data.apiKeys[0]); // Prendre la première clé active
            }
        } catch (error) {
            console.error('Erreur lors du chargement de la clé API:', error);
            showMessage('error', 'Erreur lors du chargement de la clé API');
        }
    };

    const showMessage = (type: 'success' | 'error', text: string) => {
        setMessage({ type, text });
        setTimeout(() => setMessage(null), 3000);
    };

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            showMessage('success', 'Clé API copiée dans le presse-papier !');
        } catch (error) {
            // Fallback pour les navigateurs plus anciens
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showMessage('success', 'Clé API copiée !');
        }
    };

    const regenerateApiKey = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`http://localhost:5000/api/apikeys/${user.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            const data = await response.json();

            if (data.success) {
                setApiKey(data.apiKey);
                showMessage('success', 'Nouvelle clé API générée avec succès !');
            } else {
                showMessage('error', data.error || 'Erreur lors de la génération de la clé');
            }
        } catch (error) {
            console.error('Erreur lors de la génération de la clé API:', error);
            showMessage('error', 'Erreur lors de la génération de la clé API');
        } finally {
            setIsLoading(false);
        }
    };

    const handleProfileUpdate = async () => {
        setIsLoading(true);
        try {
            // Simuler un appel API
            await new Promise(resolve => setTimeout(resolve, 1000));

            setUser(prev => prev ? { ...prev, ...profileData } : null);
            showMessage('success', 'Profil mis à jour avec succès');
        } catch (error) {
            showMessage('error', 'Erreur lors de la mise à jour du profil');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteAccount = async () => {
        // Double confirmation pour la suppression de compte
        const firstConfirm = confirm(
            `⚠️ ATTENTION ⚠️\n\nÊtes-vous absolument sûr de vouloir supprimer votre compte ?\n\nCette action est IRRÉVERSIBLE et supprimera :\n- Votre profil utilisateur\n- Toutes vos clés API\n- Tous vos paramètres\n\nTapez "SUPPRIMER" pour confirmer`
        );

        if (!firstConfirm) return;

        const secondConfirm = prompt(
            'Pour confirmer la suppression, tapez exactement "SUPPRIMER" :'
        );

        if (secondConfirm !== 'SUPPRIMER') {
            showMessage('error', 'Suppression annulée - Texte de confirmation incorrect');
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(`http://localhost:5000/api/auth/delete-account/${user.id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.success) {
                showMessage('success', 'Votre compte a été supprimé. Redirection...');

                // Nettoyer le localStorage et rediriger vers la page d'accueil après 2 secondes
                setTimeout(() => {
                    localStorage.removeItem('user');
                    window.location.href = '/';
                }, 2000);
            } else {
                showMessage('error', data.error || 'Erreur lors de la suppression du compte');
            }
        } catch (error) {
            console.error('Erreur lors de la suppression du compte:', error);
            showMessage('error', 'Erreur lors de la suppression du compte');
        } finally {
            setIsLoading(false);
        }
    };

    const sections = [
        { id: 'api', label: 'Clé API', icon: KeyIcon },
        { id: 'profile', label: 'Profil', icon: UserIcon },
        { id: 'security', label: 'Sécurité', icon: ShieldCheckIcon },
        { id: 'notifications', label: 'Notifications', icon: BellIcon },
        { id: 'danger', label: 'Zone de Danger', icon: ExclamationTriangleIcon },
    ];

    return (
        <div className="settings-panel">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="settings-container"
            >
                {message && (
                    <motion.div
                        className={`message ${message.type}`}
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                    >
                        {message.text}
                    </motion.div>
                )}

                <div className="settings-layout">
                    {/* Navigation */}
                    <nav className="settings-nav">
                        {sections.map((section) => (
                            <motion.button
                                key={section.id}
                                className={`nav-item ${activeSection === section.id ? 'active' : ''} ${section.id === 'danger' ? 'danger-tab' : ''}`}
                                onClick={() => setActiveSection(section.id)}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                <section.icon className="nav-icon" />
                                {section.label}
                            </motion.button>
                        ))}
                    </nav>

                    {/* Contenu */}
                    <div className="settings-content">
                        {activeSection === 'api' && (
                            <motion.div
                                key="api"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="section"
                            >
                                <h2><KeyIcon /> Clé API ChessBot</h2>

                                <div className="api-key-section">
                                    <div className="api-info">
                                        <h3>🔑 Votre Clé API</h3>
                                        <p>Utilisez cette clé pour intégrer ChessBot dans vos applications ou pour connecter des outils externes.</p>
                                    </div>

                                    {apiKey ? (
                                        <>
                                            <div className="api-key-display">
                                                <div className="api-key-container">
                                                    <code className="api-key-text">{apiKey.keyValue}</code>
                                                    <motion.button
                                                        className="copy-btn"
                                                        onClick={() => copyToClipboard(apiKey.keyValue)}
                                                        whileHover={{ scale: 1.05 }}
                                                        whileTap={{ scale: 0.95 }}
                                                    >
                                                        <ClipboardDocumentIcon />
                                                        Copier
                                                    </motion.button>
                                                </div>
                                            </div>

                                            <div className="api-actions">
                                                <motion.button
                                                    className="regenerate-btn"
                                                    onClick={regenerateApiKey}
                                                    disabled={isLoading}
                                                    whileHover={{ scale: 1.05 }}
                                                    whileTap={{ scale: 0.95 }}
                                                >
                                                    {isLoading ? <ArrowPathIcon className="spinning" /> : <ArrowPathIcon />}
                                                    {isLoading ? 'Génération...' : 'Régénérer la clé'}
                                                </motion.button>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="no-api-key">
                                            <p>Aucune clé API trouvée. Générez votre première clé :</p>
                                            <motion.button
                                                className="save-btn"
                                                onClick={regenerateApiKey}
                                                disabled={isLoading}
                                                whileHover={{ scale: 1.05 }}
                                                whileTap={{ scale: 0.95 }}
                                            >
                                                {isLoading ? <ArrowPathIcon className="spinning" /> : <KeyIcon />}
                                                {isLoading ? 'Génération...' : 'Générer ma clé API'}
                                            </motion.button>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        )}

                        {activeSection === 'profile' && (
                            <motion.div
                                key="profile"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="section"
                            >
                                <h2><UserIcon /> Profil Utilisateur</h2>

                                <div className="form-group">
                                    <label>Nom d'utilisateur</label>
                                    <input
                                        type="text"
                                        value={profileData.username}
                                        onChange={(e) => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                                        disabled={isLoading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Email</label>
                                    <input
                                        type="email"
                                        value={profileData.email}
                                        onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                                        disabled={isLoading}
                                    />
                                </div>

                                <div className="subscription-info">
                                    <h3>Abonnement</h3>
                                    <p>Actif jusqu'au {new Date(user.subscriptionEndDate).toLocaleDateString()}</p>
                                    <div className="subscription-status active">Premium</div>
                                </div>

                                <button
                                    className="save-btn"
                                    onClick={handleProfileUpdate}
                                    disabled={isLoading}
                                >
                                    {isLoading ? <ArrowPathIcon className="spinning" /> : null}
                                    Sauvegarder
                                </button>
                            </motion.div>
                        )}

                        {activeSection === 'security' && (
                            <motion.div
                                key="security"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="section"
                            >
                                <h2><ShieldCheckIcon /> Sécurité</h2>

                                <div className="form-group">
                                    <label>Mot de passe actuel</label>
                                    <input type="password" placeholder="••••••••" />
                                </div>

                                <div className="form-group">
                                    <label>Nouveau mot de passe</label>
                                    <input type="password" placeholder="••••••••" />
                                </div>

                                <div className="form-group">
                                    <label>Confirmer le nouveau mot de passe</label>
                                    <input type="password" placeholder="••••••••" />
                                </div>

                                <button className="save-btn">
                                    Changer le mot de passe
                                </button>
                            </motion.div>
                        )}

                        {activeSection === 'notifications' && (
                            <motion.div
                                key="notifications"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="section"
                            >
                                <h2><BellIcon /> Notifications</h2>

                                <div className="toggle-list">
                                    {Object.entries(notifications).map(([key, value]) => (
                                        <div key={key} className="toggle-item">
                                            <label>
                                                <input
                                                    type="checkbox"
                                                    checked={value}
                                                    onChange={(e) => setNotifications(prev => ({
                                                        ...prev,
                                                        [key]: e.target.checked
                                                    }))}
                                                />
                                                <span className="toggle-label">
                                                    {key === 'gameStart' ? 'Début de partie' :
                                                        key === 'gameEnd' ? 'Fin de partie' :
                                                            key === 'errors' ? 'Erreurs' : 'Mises à jour'}
                                                </span>
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {activeSection === 'danger' && (
                            <motion.div
                                key="danger"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="section"
                            >
                                <h2><ExclamationTriangleIcon /> Zone de Danger</h2>

                                <div className="danger-zone">
                                    <div className="danger-warning">
                                        <h3>⚠️ Suppression de Compte</h3>
                                        <p>La suppression de votre compte est une action <strong>irréversible</strong> qui entraînera :</p>
                                        <ul>
                                            <li>🗑️ Suppression définitive de votre profil utilisateur</li>
                                            <li>🔑 Suppression de toutes vos clés API</li>
                                            <li>⚙️ Suppression de tous vos paramètres et préférences</li>
                                            <li>📊 Perte de tout l'historique de vos parties</li>
                                        </ul>
                                        <p className="danger-note">
                                            <strong>Important :</strong> Aucune récupération ne sera possible après confirmation.
                                        </p>
                                    </div>

                                    <motion.button
                                        className="delete-account-btn"
                                        onClick={handleDeleteAccount}
                                        disabled={isLoading}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        {isLoading ? (
                                            <>
                                                <ArrowPathIcon className="spinning" />
                                                Suppression en cours...
                                            </>
                                        ) : (
                                            <>
                                                <TrashIcon />
                                                Supprimer définitivement mon compte
                                            </>
                                        )}
                                    </motion.button>
                                </div>
                            </motion.div>
                        )}
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default SettingsPanel; 