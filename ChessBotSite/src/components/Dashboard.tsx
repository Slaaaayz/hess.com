import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    UserIcon,
    KeyIcon
} from '@heroicons/react/24/outline';
import SettingsPanel from './dashboard/SettingsPanel';
import AdminDashboard from './AdminDashboard';
import './Dashboard.css';

interface User {
    id: number;
    username: string;
    email: string;
    subscriptionEndDate: string;
    role?: string;
    settings?: {
        skillLevel: number;
        searchDepth: number;
    };
}

const Dashboard = () => {
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        // Récupérer les informations utilisateur du localStorage
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                const userData = JSON.parse(storedUser);
                setUser(userData);
            } catch (error) {
                console.error('Erreur parsing user data:', error);
                localStorage.removeItem('user');
            }
        }
    }, []);

    // Si l'utilisateur est admin, afficher le dashboard admin
    if (user?.role === 'admin' || user?.email === 'admin') {
        return <AdminDashboard />;
    }

    // Dashboard utilisateur normal (settings seulement)
    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="header-content">
                    <div className="user-info">
                        <div className="user-avatar">
                            {user?.username?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div>
                            <h1>Dashboard ChessBot</h1>
                            <p>Bienvenue, {user?.username || 'Utilisateur'}</p>
                        </div>
                    </div>
                </div>
            </header>

            <main className="dashboard-main">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="dashboard-content"
                >
                    {user && <SettingsPanel user={user} setUser={setUser} />}
                </motion.div>
            </main>
        </div>
    );
};

export default Dashboard; 