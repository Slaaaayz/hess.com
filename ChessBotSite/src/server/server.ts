import express from 'express';
import cors from 'cors';
import authRouter from './auth.js';
import apiKeysRouter from './apikeys.js';
import adminRouter from './admin.js';

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware global
app.use(cors({
    origin: ['http://localhost:5173', 'http://localhost:3000'], // Frontend URLs
    credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', authRouter);
app.use('/api/apikeys', apiKeysRouter);
app.use('/api/admin', adminRouter);

// Route de test
app.get('/api/health', (req, res) => {
    res.json({
        status: 'OK',
        message: 'ChessBot Backend Server is running',
        timestamp: new Date().toISOString()
    });
});

// Route pour recevoir les données du dashboard
app.post('/api/dashboard/bot-status', (req, res) => {
    console.log('📊 Bot Status:', req.body);
    res.json({ status: 'success' });
});

app.post('/api/dashboard/logs', (req, res) => {
    console.log('📝 Log:', req.body);
    res.json({ status: 'success' });
});

app.post('/api/dashboard/move-executed', (req, res) => {
    console.log('♟️ Move Executed:', req.body);
    res.json({ status: 'success' });
});

// Gestion des erreurs 404
app.use('*', (req, res) => {
    res.status(404).json({
        message: 'Route non trouvée',
        path: req.originalUrl
    });
});

// Gestion des erreurs globales
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error('❌ Erreur serveur:', err);
    res.status(500).json({
        message: 'Erreur interne du serveur',
        error: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

// Démarrage du serveur
app.listen(PORT, () => {
    console.log(`🚀 Serveur backend démarré sur http://localhost:${PORT}`);
    console.log(`📋 Routes disponibles:`);
    console.log(`   - GET  /api/health`);
    console.log(`   - POST /api/auth/register`);
    console.log(`   - POST /api/auth/login`);
    console.log(`   - POST /api/dashboard/*`);
});

// Gestion de l'arrêt propre
process.on('SIGINT', () => {
    console.log('\n🛑 Arrêt du serveur...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Arrêt du serveur...');
    process.exit(0);
});

export default app; 