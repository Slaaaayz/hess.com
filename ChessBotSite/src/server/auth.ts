import express from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import cors from 'cors';

const prisma = new PrismaClient();
const router = express.Router();

router.use(cors());
router.use(express.json());

// Validation des paramètres utilisateur
const validateUserSettings = (skillLevel: number, searchDepth: number) => {
    if (skillLevel < 0 || skillLevel > 3000) {
        throw new Error('Le niveau de compétence doit être entre 0 et 3000');
    }
    if (searchDepth < 1 || searchDepth > 20) {
        throw new Error('La profondeur de recherche doit être entre 1 et 20');
    }
};

// Route d'inscription
router.post('/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;

        // Vérification si l'utilisateur existe déjà
        const existingUser = await prisma.user.findFirst({
            where: {
                OR: [
                    { username },
                    { email }
                ]
            }
        });

        if (existingUser) {
            return res.status(400).json({
                message: existingUser.email === email
                    ? 'Cet email est déjà utilisé'
                    : 'Ce nom d\'utilisateur est déjà pris'
            });
        }

        // Hashage du mot de passe
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Validation des paramètres par défaut
        validateUserSettings(15, 3);

        // Création de l'utilisateur avec une date d'abonnement de 30 jours
        const user = await prisma.user.create({
            data: {
                username,
                email,
                password: hashedPassword,
                subscriptionEndDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // +30 jours
                settings: {
                    create: {
                        skillLevel: 1500,
                        searchDepth: 3
                    }
                }
            },
            include: {
                settings: true
            }
        });

        res.status(201).json({
            message: 'Inscription réussie',
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                subscriptionEndDate: user.subscriptionEndDate,
                settings: user.settings
            }
        });

    } catch (error) {
        console.error('Erreur lors de l\'inscription:', error);
        res.status(500).json({
            message: error instanceof Error ? error.message : 'Erreur lors de l\'inscription'
        });
    }
});

// Route de connexion
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // Recherche de l'utilisateur avec SQL raw pour avoir le champ role
        const users = await prisma.$queryRaw`
            SELECT u.id, u.username, u.email, u.password, u.role, u.subscriptionEndDate,
                   us.skillLevel, us.searchDepth
            FROM User u
            LEFT JOIN UserSettings us ON u.id = us.userId
            WHERE u.email = ${email}
        `;

        if (!users || (Array.isArray(users) && users.length === 0)) {
            return res.status(400).json({ message: 'Email ou mot de passe incorrect' });
        }

        const user = Array.isArray(users) ? users[0] : users;

        // Vérification du mot de passe
        const validPassword = await bcrypt.compare(password, (user as any).password);
        if (!validPassword) {
            return res.status(400).json({ message: 'Email ou mot de passe incorrect' });
        }

        res.json({
            message: 'Connexion réussie',
            user: {
                id: (user as any).id,
                username: (user as any).username,
                email: (user as any).email,
                role: (user as any).role,
                subscriptionEndDate: (user as any).subscriptionEndDate,
                settings: {
                    skillLevel: (user as any).skillLevel || 1500,
                    searchDepth: (user as any).searchDepth || 3
                }
            }
        });

    } catch (error) {
        console.error('Erreur lors de la connexion:', error);
        res.status(500).json({
            message: error instanceof Error ? error.message : 'Erreur lors de la connexion'
        });
    }
});

// DELETE /api/auth/delete-account/:userId - Supprimer son propre compte
router.delete('/delete-account/:userId', async (req, res) => {
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

        // Supprimer l'utilisateur (cela supprimera aussi ses paramètres et clés API grâce aux contraintes CASCADE)
        await prisma.user.delete({
            where: { id: userId }
        });

        res.json({
            success: true,
            message: 'Votre compte a été supprimé avec succès'
        });
    } catch (error) {
        console.error('Erreur suppression compte:', error);
        res.status(500).json({ error: 'Erreur lors de la suppression du compte' });
    }
});

export default router; 