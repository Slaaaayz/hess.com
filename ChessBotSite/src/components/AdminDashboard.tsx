import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    UsersIcon,
    KeyIcon,
    ChartBarIcon,
    TrashIcon,
    PencilIcon,
    EyeIcon
} from '@heroicons/react/24/outline';

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    subscriptionEndDate: string;
    createdAt: string;
    updatedAt: string;
    settings?: {
        skillLevel: number;
        searchDepth: number;
    };
    apiKeys?: Array<{
        id: number;
        keyValue: string;
        name: string;
        createdAt: string;
    }>;
}

interface ApiKey {
    id: number;
    userId: number;
    keyValue: string;
    name: string;
    isActive: boolean;
    createdAt: string;
    username: string;
    email: string;
}

interface Stats {
    totalUsers: number;
    totalApiKeys: number;
    adminUsers: number;
    regularUsers: number;
}

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('stats');
    const [users, setUsers] = useState<User[]>([]);
    const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    // ID de l'admin (4)
    const adminId = 4;

    const showMessage = (type: 'success' | 'error', text: string) => {
        setMessage({ type, text });
        setTimeout(() => setMessage(null), 3000);
    };

    const apiCall = async (url: string, options: RequestInit = {}) => {
        return fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'x-user-id': adminId.toString(),
                ...options.headers,
            },
        });
    };

    const loadStats = async () => {
        try {
            const response = await apiCall('http://localhost:5000/api/admin/stats');
            const data = await response.json();
            if (response.ok) {
                setStats(data.stats);
            } else {
                showMessage('error', data.error || 'Erreur lors du chargement des statistiques');
            }
        } catch (error) {
            showMessage('error', 'Erreur de connexion');
        }
    };

    const loadUsers = async () => {
        setLoading(true);
        try {
            const response = await apiCall('http://localhost:5000/api/admin/users');
            const data = await response.json();
            if (response.ok) {
                setUsers(data.users);
            } else {
                showMessage('error', data.error || 'Erreur lors du chargement des utilisateurs');
            }
        } catch (error) {
            showMessage('error', 'Erreur de connexion');
        } finally {
            setLoading(false);
        }
    };

    const loadApiKeys = async () => {
        setLoading(true);
        try {
            const response = await apiCall('http://localhost:5000/api/admin/apikeys');
            const data = await response.json();
            if (response.ok) {
                setApiKeys(data.apiKeys);
            } else {
                showMessage('error', data.error || 'Erreur lors du chargement des clés API');
            }
        } catch (error) {
            showMessage('error', 'Erreur de connexion');
        } finally {
            setLoading(false);
        }
    };

    const deleteUser = async (userId: number, username: string) => {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${username}" ?`)) {
            return;
        }

        try {
            const response = await apiCall(`http://localhost:5000/api/admin/users/${userId}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (response.ok) {
                showMessage('success', data.message);
                loadUsers();
                loadStats();
            } else {
                showMessage('error', data.error || 'Erreur lors de la suppression');
            }
        } catch (error) {
            showMessage('error', 'Erreur de connexion');
        }
    };

    const deleteApiKey = async (keyId: number, keyName: string) => {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer la clé "${keyName}" ?`)) {
            return;
        }

        try {
            const response = await apiCall(`http://localhost:5000/api/admin/apikeys/${keyId}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (response.ok) {
                showMessage('success', data.message);
                loadApiKeys();
                loadStats();
            } else {
                showMessage('error', data.error || 'Erreur lors de la suppression');
            }
        } catch (error) {
            showMessage('error', 'Erreur de connexion');
        }
    };

    useEffect(() => {
        loadStats();
    }, []);

    useEffect(() => {
        if (activeTab === 'users') {
            loadUsers();
        } else if (activeTab === 'apikeys') {
            loadApiKeys();
        }
    }, [activeTab]);

    const tabs = [
        { id: 'stats', label: 'Statistiques', icon: ChartBarIcon },
        { id: 'users', label: 'Utilisateurs', icon: UsersIcon },
        { id: 'apikeys', label: 'Clés API', icon: KeyIcon },
    ];

    return (
        <>
            {/* Header Admin */}
            <header className="dashboard-header">
                <div className="header-content">
                    <div className="user-info">
                        <UsersIcon className="user-icon" />
                        <div>
                            <h1>🛡️ Administration ChessBot</h1>
                            <p>Gestion des utilisateurs et des clés API</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Messages */}
            {message && (
                <motion.div
                    className={`message ${message.type}`}
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    style={{
                        position: 'fixed',
                        top: '100px',
                        right: '20px',
                        zIndex: 1000,
                        padding: '1rem 2rem',
                        borderRadius: '8px',
                        color: 'white',
                        background: message.type === 'success' ? '#22c55e' : '#ef4444'
                    }}
                >
                    {message.text}
                </motion.div>
            )}

            {/* Main Content */}
            <main className="dashboard-main">
                {/* Navigation Tabs */}
                <div className="admin-tabs">
                    {tabs.map((tab) => (
                        <motion.button
                            key={tab.id}
                            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <tab.icon className="tab-icon" />
                            {tab.label}
                        </motion.button>
                    ))}
                </div>

                {/* Tab Content */}
                <div className="admin-content">
                    {activeTab === 'stats' && (
                        <motion.div
                            key="stats"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="stats-section"
                        >
                            <h2>📊 Statistiques Générales</h2>
                            {stats && (
                                <div className="stats-grid">
                                    <div className="stat-card">
                                        <div className="stat-number">{stats.totalUsers}</div>
                                        <div className="stat-label">Utilisateurs Total</div>
                                    </div>
                                    <div className="stat-card">
                                        <div className="stat-number">{stats.regularUsers}</div>
                                        <div className="stat-label">Utilisateurs Standard</div>
                                    </div>
                                    <div className="stat-card">
                                        <div className="stat-number">{stats.adminUsers}</div>
                                        <div className="stat-label">Administrateurs</div>
                                    </div>
                                    <div className="stat-card">
                                        <div className="stat-number">{stats.totalApiKeys}</div>
                                        <div className="stat-label">Clés API Actives</div>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {activeTab === 'users' && (
                        <motion.div
                            key="users"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="users-section"
                        >
                            <h2>👥 Gestion des Utilisateurs</h2>
                            {loading ? (
                                <div>Chargement...</div>
                            ) : (
                                <div className="users-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>ID</th>
                                                <th>Nom d'utilisateur</th>
                                                <th>Email</th>
                                                <th>Rôle</th>
                                                <th>Clés API</th>
                                                <th>Créé le</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {users.map((user) => (
                                                <tr key={user.id}>
                                                    <td>{user.id}</td>
                                                    <td>{user.username}</td>
                                                    <td>{user.email}</td>
                                                    <td>
                                                        <span className={`role-badge ${user.role}`}>
                                                            {user.role === 'admin' ? '🛡️ Admin' : '👤 User'}
                                                        </span>
                                                    </td>
                                                    <td>{user.apiKeys?.length || 0}</td>
                                                    <td>{new Date(user.createdAt).toLocaleDateString()}</td>
                                                    <td>
                                                        <div className="action-buttons">
                                                            <button
                                                                className="action-btn delete"
                                                                onClick={() => deleteUser(user.id, user.username)}
                                                                disabled={user.id === adminId}
                                                                title={user.id === adminId ? "Impossible de supprimer votre propre compte" : "Supprimer"}
                                                            >
                                                                <TrashIcon />
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {activeTab === 'apikeys' && (
                        <motion.div
                            key="apikeys"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="apikeys-section"
                        >
                            <h2>🔑 Gestion des Clés API</h2>
                            {loading ? (
                                <div>Chargement...</div>
                            ) : (
                                <div className="apikeys-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>ID</th>
                                                <th>Utilisateur</th>
                                                <th>Nom de la clé</th>
                                                <th>Clé API</th>
                                                <th>Statut</th>
                                                <th>Créée le</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {apiKeys.map((key) => (
                                                <tr key={key.id}>
                                                    <td>{key.id}</td>
                                                    <td>
                                                        <div>
                                                            <div className="user-name">{key.username}</div>
                                                            <div className="user-email">{key.email}</div>
                                                        </div>
                                                    </td>
                                                    <td>{key.name}</td>
                                                    <td>
                                                        <code className="api-key-display">
                                                            {key.keyValue.substring(0, 20)}...
                                                        </code>
                                                    </td>
                                                    <td>
                                                        <span className={`status-badge ${key.isActive ? 'active' : 'inactive'}`}>
                                                            {key.isActive ? '✅ Active' : '❌ Inactive'}
                                                        </span>
                                                    </td>
                                                    <td>{new Date(key.createdAt).toLocaleDateString()}</td>
                                                    <td>
                                                        <div className="action-buttons">
                                                            <button
                                                                className="action-btn delete"
                                                                onClick={() => deleteApiKey(key.id, key.name)}
                                                                title="Supprimer"
                                                            >
                                                                <TrashIcon />
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </motion.div>
                    )}
                </div>
            </main>
        </>
    );
};

export default AdminDashboard; 