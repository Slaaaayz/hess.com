const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');
const prisma = new PrismaClient();

async function createOrUpdateAdmin() {
    try {
        // Supprimer l'utilisateur admin existant s'il existe
        await prisma.user.deleteMany({
            where: {
                OR: [
                    { email: 'admin' },
                    { id: 4 }
                ]
            }
        });

        // Créer un hash du mot de passe
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash('admin', salt);

        // Créer un nouvel utilisateur admin avec l'ID 4
        const newUser = await prisma.user.create({
            data: {
                id: 4, // Forcer l'ID à 4
                username: 'Administrateur',
                email: 'admin',
                password: hashedPassword,
                role: 'admin',
                subscriptionEndDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // +1 an
                settings: {
                    create: {
                        skillLevel: 15,
                        searchDepth: 3
                    }
                }
            }
        });
        console.log('Nouvel utilisateur admin créé avec succès:', newUser);
    } catch (error) {
        console.error('Erreur:', error);
    } finally {
        await prisma.$disconnect();
    }
}

createOrUpdateAdmin(); 