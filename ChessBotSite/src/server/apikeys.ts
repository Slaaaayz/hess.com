import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import crypto from 'crypto';

const router = Router();
const prisma = new PrismaClient();

// Fonction pour générer une clé API
const generateApiKey = (): string => {
    const prefix = 'sk-chessbot-';
    const randomPart = crypto.randomBytes(16).toString('hex');
    return prefix + randomPart;
};

// GET /api/apikeys/:userId - Récupérer les clés API d'un utilisateur
router.get('/:userId', async (req, res) => {
    try {
        const userId = parseInt(req.params.userId);

        if (isNaN(userId)) {
            return res.status(400).json({ error: 'ID utilisateur invalide' });
        }

        // Utiliser du SQL brut pour éviter les problèmes de types
        const apiKeys = await prisma.$queryRaw`
            SELECT id, keyValue, name, createdAt, updatedAt 
            FROM ApiKey 
            WHERE userId = ${userId} AND isActive = 1 
            ORDER BY createdAt DESC
        `;

        res.json({ apiKeys });
    } catch (error) {
        console.error('Erreur lors de la récupération des clés API:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// POST /api/apikeys/:userId - Créer une nouvelle clé API (et supprimer l'ancienne)
router.post('/:userId', async (req, res) => {
    try {
        const userId = parseInt(req.params.userId);

        if (isNaN(userId)) {
            return res.status(400).json({ error: 'ID utilisateur invalide' });
        }

        // Vérifier que l'utilisateur existe
        const user = await prisma.user.findUnique({
            where: { id: userId }
        });

        if (!user) {
            return res.status(404).json({ error: 'Utilisateur non trouvé' });
        }

        const newKeyValue = generateApiKey();
        const keyName = 'Default API Key';

        // Utiliser du SQL brut dans une transaction
        const result = await prisma.$transaction(async (tx) => {
            // Désactiver toutes les anciennes clés
            await tx.$executeRaw`
                UPDATE ApiKey 
                SET isActive = 0 
                WHERE userId = ${userId} AND isActive = 1
            `;

            // Créer la nouvelle clé
            await tx.$executeRaw`
                INSERT INTO ApiKey (userId, keyValue, name, isActive, createdAt, updatedAt)
                VALUES (${userId}, ${newKeyValue}, ${keyName}, 1, NOW(), NOW())
            `;

            // Récupérer la nouvelle clé créée
            const newKey = await tx.$queryRaw`
                SELECT id, keyValue, name, createdAt, updatedAt 
                FROM ApiKey 
                WHERE userId = ${userId} AND keyValue = ${newKeyValue}
            `;

            return Array.isArray(newKey) ? newKey[0] : newKey;
        });

        res.json({
            success: true,
            apiKey: result,
            message: 'Nouvelle clé API créée avec succès'
        });
    } catch (error) {
        console.error('Erreur lors de la création de la clé API:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// DELETE /api/apikeys/:keyId - Supprimer une clé API spécifique
router.delete('/:keyId', async (req, res) => {
    try {
        const keyId = parseInt(req.params.keyId);

        if (isNaN(keyId)) {
            return res.status(400).json({ error: 'ID de clé invalide' });
        }

        // Récupérer le nom de la clé avant de la supprimer
        const apiKey = await prisma.$queryRaw`
            SELECT name FROM ApiKey WHERE id = ${keyId}
        `;

        if (!apiKey || (Array.isArray(apiKey) && apiKey.length === 0)) {
            return res.status(404).json({ error: 'Clé API non trouvée' });
        }

        // Désactiver la clé
        await prisma.$executeRaw`
            UPDATE ApiKey 
            SET isActive = 0 
            WHERE id = ${keyId}
        `;

        const keyName = Array.isArray(apiKey) ? (apiKey[0] as any).name : (apiKey as any).name;

        res.json({
            success: true,
            message: `Clé API "${keyName}" supprimée avec succès`
        });
    } catch (error) {
        console.error('Erreur lors de la suppression de la clé API:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

export default router; 