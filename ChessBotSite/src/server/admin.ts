import { Router } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

// Middleware pour vérifier les droits admin
const requireAdmin = async (req: any, res: any, next: any) => {
    const userId = req.headers['x-user-id'];

    if (!userId) {
        return res.status(401).json({ error: 'ID utilisateur requis' });
    }

    try {
        const user = await prisma.user.findUnique({
            where: { id: parseInt(userId) }
        });

        if (!user || user.role !== 'admin') {
            return res.status(403).json({ error: 'Accès refusé - Droits administrateur requis' });
        }

        req.adminUser = user;
        next();
    } catch (error) {
        console.error('Erreur vérification admin:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
};

// ===== GESTION DES UTILISATEURS =====

// GET /api/admin/users - Lister tous les utilisateurs
router.get('/users', requireAdmin, async (req, res) => {
    try {
        const users = await prisma.user.findMany({
            include: {
                settings: true,
                apiKeys: {
                    where: { isActive: true },
                    select: {
                        id: true,
                        keyValue: true,
                        name: true,
                        createdAt: true
                    }
                }
            },
            orderBy: { createdAt: 'desc' }
        });

        res.json({ users });
    } catch (error) {
        console.error('Erreur récupération utilisateurs:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// GET /api/admin/users/:id - Récupérer un utilisateur spécifique
router.get('/users/:id', requireAdmin, async (req, res) => {
    try {
        const userId = parseInt(req.params.id);

        if (isNaN(userId)) {
            return res.status(400).json({ error: 'ID utilisateur invalide' });
        }

        const user = await prisma.user.findUnique({
            where: { id: userId },
            include: {
                settings: true,
                apiKeys: {
                    where: { isActive: true }
                }
            }
        });

        if (!user) {
            return res.status(404).json({ error: 'Utilisateur non trouvé' });
        }

        res.json({ user });
    } catch (error) {
        console.error('Erreur récupération utilisateur:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// PUT /api/admin/users/:id - Modifier un utilisateur
router.put('/users/:id', requireAdmin, async (req, res) => {
    try {
        const userId = parseInt(req.params.id);
        const { username, email, role, subscriptionEndDate, settings } = req.body;

        if (isNaN(userId)) {
            return res.status(400).json({ error: 'ID utilisateur invalide' });
        }

        const updatedUser = await prisma.user.update({
            where: { id: userId },
            data: {
                username,
                email,
                role,
                subscriptionEndDate: subscriptionEndDate ? new Date(subscriptionEndDate) : undefined,
                settings: settings ? {
                    upsert: {
                        create: settings,
                        update: settings
                    }
                } : undefined
            },
            include: {
                settings: true
            }
        });

        res.json({ success: true, user: updatedUser });
    } catch (error) {
        console.error('Erreur modification utilisateur:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// DELETE /api/admin/users/:id - Supprimer un utilisateur
router.delete('/users/:id', requireAdmin, async (req, res) => {
    try {
        const userId = parseInt(req.params.id);

        if (isNaN(userId)) {
            return res.status(400).json({ error: 'ID utilisateur invalide' });
        }

        // Empêcher la suppression de son propre compte admin
        if (userId === req.adminUser.id) {
            return res.status(400).json({ error: 'Impossible de supprimer votre propre compte' });
        }

        await prisma.user.delete({
            where: { id: userId }
        });

        res.json({ success: true, message: 'Utilisateur supprimé avec succès' });
    } catch (error) {
        console.error('Erreur suppression utilisateur:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// ===== GESTION DES CLÉS API =====

// GET /api/admin/apikeys - Lister toutes les clés API
router.get('/apikeys', requireAdmin, async (req, res) => {
    try {
        const apiKeys = await prisma.$queryRaw`
            SELECT ak.id, ak.userId, ak.keyValue, ak.name, ak.isActive, ak.createdAt, ak.updatedAt,
                   u.username, u.email
            FROM ApiKey ak
            JOIN User u ON ak.userId = u.id
            ORDER BY ak.createdAt DESC
        `;

        res.json({ apiKeys });
    } catch (error) {
        console.error('Erreur récupération clés API:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// DELETE /api/admin/apikeys/:id - Supprimer une clé API
router.delete('/apikeys/:id', requireAdmin, async (req, res) => {
    try {
        const keyId = parseInt(req.params.id);

        if (isNaN(keyId)) {
            return res.status(400).json({ error: 'ID de clé invalide' });
        }

        await prisma.$executeRaw`
            UPDATE ApiKey 
            SET isActive = 0 
            WHERE id = ${keyId}
        `;

        res.json({ success: true, message: 'Clé API supprimée avec succès' });
    } catch (error) {
        console.error('Erreur suppression clé API:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// ===== STATISTIQUES ADMIN =====

// GET /api/admin/stats - Statistiques générales
router.get('/stats', requireAdmin, async (req, res) => {
    try {
        const totalUsers = await prisma.user.count();
        const totalApiKeys = await prisma.apiKey.count({ where: { isActive: true } });
        const adminUsers = await prisma.user.count({ where: { role: 'admin' } });

        const recentUsers = await prisma.user.findMany({
            where: {
                createdAt: {
                    gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // 7 derniers jours
                }
            },
            orderBy: { createdAt: 'desc' },
            take: 5,
            select: {
                id: true,
                username: true,
                email: true,
                role: true,
                createdAt: true
            }
        });

        res.json({
            stats: {
                totalUsers,
                totalApiKeys,
                adminUsers,
                regularUsers: totalUsers - adminUsers
            },
            recentUsers
        });
    } catch (error) {
        console.error('Erreur récupération statistiques:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

export default router; 