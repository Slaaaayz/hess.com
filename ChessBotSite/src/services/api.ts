const API_URL = 'http://localhost:5000/api';

interface RegisterData {
    username: string;
    email: string;
    password: string;
}

interface LoginData {
    email: string;
    password: string;
}

interface UserSettings {
    skillLevel: number;
    searchDepth: number;
}

interface User {
    id: number;
    username: string;
    email: string;
    subscriptionEndDate: string;
    settings?: UserSettings;
}

interface ApiResponse {
    message: string;
    user?: User;
}

export const authApi = {
    async register(data: RegisterData): Promise<ApiResponse> {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'Erreur lors de l\'inscription');
        }

        return result;
    },

    async login(data: LoginData): Promise<ApiResponse> {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'Erreur lors de la connexion');
        }

        return result;
    },
}; 