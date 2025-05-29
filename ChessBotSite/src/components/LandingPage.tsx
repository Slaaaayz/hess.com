import { motion } from 'framer-motion'
import { PlayIcon, UserIcon, LockClosedIcon } from '@heroicons/react/24/outline'
import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'

function LandingPage() {
    const navigate = useNavigate()

    useEffect(() => {
        // Empêcher le scroll horizontal et corriger les marges
        document.body.style.overflowX = 'hidden'
        document.body.style.margin = '0'
        document.body.style.padding = '0'
        document.documentElement.style.overflowX = 'hidden'
        document.documentElement.style.margin = '0'
        document.documentElement.style.padding = '0'

        // Forcer le root à prendre toute la largeur
        const root = document.getElementById('root')
        if (root) {
            root.style.margin = '0'
            root.style.padding = '0'
            root.style.width = '100vw'
            root.style.maxWidth = 'none'
            root.style.left = '0'
            root.style.right = '0'
            root.style.position = 'relative'
            root.style.boxSizing = 'border-box'
        }

        return () => {
            // Nettoyer en cas de démontage du composant
            document.body.style.overflowX = ''
            document.body.style.margin = ''
            document.body.style.padding = ''
            document.documentElement.style.overflowX = ''
            document.documentElement.style.margin = ''
            document.documentElement.style.padding = ''

            if (root) {
                root.style.margin = ''
                root.style.padding = ''
                root.style.width = ''
                root.style.maxWidth = ''
                root.style.left = ''
                root.style.right = ''
                root.style.position = ''
                root.style.boxSizing = ''
            }
        }
    }, [])

    const handleMouseEnter = (e: React.MouseEvent<HTMLElement>, color: string) => {
        (e.target as HTMLElement).style.color = color
    }

    const handleMouseLeave = (e: React.MouseEvent<HTMLElement>, color: string) => {
        (e.target as HTMLElement).style.color = color
    }

    const handleButtonMouseEnter = (e: React.MouseEvent<HTMLElement>, bg: string, border?: string) => {
        const target = e.target as HTMLElement
        target.style.background = bg
        if (border) target.style.borderColor = border
    }

    const handleButtonMouseLeave = (e: React.MouseEvent<HTMLElement>, bg: string, border?: string) => {
        const target = e.target as HTMLElement
        target.style.background = bg
        if (border) target.style.borderColor = border
    }

    const handlePlayButtonMouseEnter = (e: React.MouseEvent<HTMLElement>) => {
        const target = e.target as HTMLElement
        target.style.background = '#16a34a'
        target.style.transform = 'scale(1.02)'
    }

    const handlePlayButtonMouseLeave = (e: React.MouseEvent<HTMLElement>) => {
        const target = e.target as HTMLElement
        target.style.background = '#22c55e'
        target.style.transform = 'scale(1)'
    }

    const handleChessSquareMouseEnter = (e: React.MouseEvent<HTMLElement>) => {
        (e.target as HTMLElement).style.backgroundColor = 'rgba(34, 197, 94, 0.5)'
    }

    const handleChessSquareMouseLeave = (e: React.MouseEvent<HTMLElement>, i: number) => {
        const target = e.target as HTMLElement
        target.style.backgroundColor = (Math.floor(i / 8) + i % 8) % 2 === 0
            ? 'rgba(34, 197, 94, 0.3)'
            : 'rgba(34, 197, 94, 0.1)'
    }

    return (
        <div style={{
            backgroundColor: '#000000',
            minHeight: '100vh',
            width: '100vw',
            color: 'white',
            margin: 0,
            padding: 0,
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            overflowX: 'hidden',
            overflowY: 'auto',
            boxSizing: 'border-box'
        }}>
            {/* Grille LED en arrière-plan */}
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundImage: `
                    linear-gradient(rgba(34, 197, 94, 0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(34, 197, 94, 0.05) 1px, transparent 1px)
                `,
                backgroundSize: '50px 50px',
                opacity: 0.3,
                zIndex: 1
            }}></div>

            {/* Navigation */}
            <nav style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                zIndex: 50,
                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                backdropFilter: 'blur(10px)',
                borderBottom: '1px solid rgba(34, 197, 94, 0.2)',
                padding: '1rem 0',
                width: '100vw',
                boxSizing: 'border-box'
            }}>
                <div style={{
                    width: '100%',
                    margin: '0',
                    padding: '0 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    boxSizing: 'border-box'
                }}>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        style={{ display: 'flex', alignItems: 'center' }}
                    >
                        <span style={{
                            fontSize: 'clamp(1.5rem, 4vw, 2rem)',
                            fontWeight: 'bold',
                            color: '#22c55e',
                            textShadow: '0 0 8px rgba(34, 197, 94, 0.5)'
                        }}>
                            PAWNED
                        </span>
                    </motion.div>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'clamp(0.5rem, 2vw, 1.5rem)',
                        flexWrap: 'nowrap'
                    }}>
                        <button
                            onClick={() => navigate('/login')}
                            style={{
                                color: '#9ca3af',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                transition: 'color 0.3s',
                                fontSize: 'clamp(0.8rem, 2vw, 1rem)',
                                padding: '0.5rem',
                                whiteSpace: 'nowrap'
                            }}
                            onMouseEnter={(e) => handleMouseEnter(e, '#22c55e')}
                            onMouseLeave={(e) => handleMouseLeave(e, '#9ca3af')}
                        >
                            <UserIcon style={{ width: '1.25rem', height: '1.25rem' }} />
                            <span style={{ display: window.innerWidth < 480 ? 'none' : 'inline' }}>Connexion</span>
                        </button>
                        <button
                            onClick={() => navigate('/register')}
                            style={{
                                background: 'rgba(34, 197, 94, 0.2)',
                                border: '1px solid rgba(34, 197, 94, 0.5)',
                                color: '#22c55e',
                                padding: 'clamp(0.5rem, 2vw, 0.75rem) clamp(1rem, 3vw, 1.5rem)',
                                borderRadius: '0.25rem',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                transition: 'all 0.3s',
                                fontSize: 'clamp(0.8rem, 2vw, 1rem)',
                                whiteSpace: 'nowrap'
                            }}
                            onMouseEnter={(e) => handleButtonMouseEnter(e, 'rgba(34, 197, 94, 0.3)', 'rgba(34, 197, 94, 0.7)')}
                            onMouseLeave={(e) => handleButtonMouseLeave(e, 'rgba(34, 197, 94, 0.2)', 'rgba(34, 197, 94, 0.5)')}
                        >
                            <LockClosedIcon style={{ width: '1.25rem', height: '1.25rem' }} />
                            <span style={{ display: window.innerWidth < 480 ? 'none' : 'inline' }}>S'inscrire</span>
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main style={{
                minHeight: '100vh',
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                position: 'relative',
                background: 'linear-gradient(to bottom, rgba(34, 197, 94, 0.05), transparent)',
                zIndex: 2,
                padding: '0 1rem',
                boxSizing: 'border-box',
                margin: 0
            }}>
                <div style={{
                    width: '100%',
                    margin: '0',
                    paddingTop: '6rem'
                }}>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: window.innerWidth < 768 ? '1fr' : '1fr 1fr',
                        gap: 'clamp(2rem, 5vw, 4rem)',
                        alignItems: 'center',
                        minHeight: 'calc(100vh - 8rem)'
                    }}>
                        {/* Texte */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8 }}
                            style={{
                                textAlign: window.innerWidth < 768 ? 'center' : 'left',
                                order: window.innerWidth < 768 ? 2 : 1,
                                paddingLeft: window.innerWidth < 768 ? '0' : 'clamp(2rem, 8vw, 6rem)'
                            }}
                        >
                            <h1 style={{
                                fontSize: 'clamp(2.5rem, 8vw, 5rem)',
                                fontWeight: 'bold',
                                marginBottom: '1.5rem',
                                lineHeight: '1.1'
                            }}>
                                <span style={{
                                    color: '#22c55e',
                                    textShadow: '0 0 8px rgba(34, 197, 94, 0.5)'
                                }}>
                                    PAWNED
                                </span>
                                <br />
                                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>L'ÉCHEC</span>
                                <br />
                                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>RÉINVENTÉ</span>
                            </h1>
                            <p style={{
                                fontSize: 'clamp(1rem, 3vw, 1.25rem)',
                                color: '#9ca3af',
                                marginBottom: '2rem',
                                lineHeight: '1.6',
                                margin: window.innerWidth < 768 ? '0 auto 2rem auto' : '0 0 2rem 0'
                            }}>
                                Une expérience de jeu d'échecs révolutionnaire où l'intelligence artificielle rencontre le design futuriste.
                            </p>
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                style={{
                                    background: '#22c55e',
                                    color: '#000000',
                                    padding: 'clamp(0.75rem, 3vw, 1rem) clamp(1.5rem, 4vw, 2rem)',
                                    borderRadius: '0.5rem',
                                    border: 'none',
                                    fontWeight: 'bold',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)',
                                    transition: 'all 0.3s',
                                    fontSize: 'clamp(0.9rem, 3vw, 1.1rem)',
                                    margin: window.innerWidth < 768 ? '0 auto' : '0'
                                }}
                                onMouseEnter={handlePlayButtonMouseEnter}
                                onMouseLeave={handlePlayButtonMouseLeave}
                            >
                                <PlayIcon style={{ width: '1.25rem', height: '1.25rem' }} />
                                JOUER MAINTENANT
                            </motion.button>
                        </motion.div>

                        {/* Échiquier */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.8, delay: 0.2 }}
                            style={{
                                position: 'relative',
                                order: window.innerWidth < 768 ? 1 : 2,
                                maxWidth: '450px',
                                margin: '0 auto',
                                width: '100%'
                            }}
                        >
                            <div style={{
                                background: 'rgba(0, 0, 0, 0.5)',
                                border: '1px solid rgba(34, 197, 94, 0.2)',
                                borderRadius: '0.5rem',
                                padding: 'clamp(0.5rem, 3vw, 1rem)',
                                aspectRatio: '1',
                                position: 'relative',
                                overflow: 'hidden',
                                width: '100%'
                            }}>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(8, 1fr)',
                                    gap: 'clamp(1px, 0.5vw, 2px)',
                                    height: '100%'
                                }}>
                                    {Array(64).fill(0).map((_, i) => (
                                        <div
                                            key={i}
                                            style={{
                                                aspectRatio: '1',
                                                borderRadius: '2px',
                                                backgroundColor: (Math.floor(i / 8) + i % 8) % 2 === 0
                                                    ? 'rgba(34, 197, 94, 0.3)'
                                                    : 'rgba(34, 197, 94, 0.1)',
                                                transition: 'background-color 0.3s',
                                                cursor: 'pointer'
                                            }}
                                            onMouseEnter={handleChessSquareMouseEnter}
                                            onMouseLeave={(e) => handleChessSquareMouseLeave(e, i)}
                                        ></div>
                                    ))}
                                </div>
                                <div style={{
                                    position: 'absolute',
                                    inset: 0,
                                    background: 'linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent)',
                                    pointerEvents: 'none'
                                }}></div>
                            </div>
                        </motion.div>
                    </div>
                </div>

                {/* Ligne de séparation LED */}
                <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '1px',
                    background: 'linear-gradient(to right, transparent, #22c55e, transparent)'
                }}></div>
            </main>

            {/* Section Prix */}
            <section style={{
                padding: 'clamp(3rem, 6vw, 6rem) 1rem',
                position: 'relative',
                zIndex: 2,
                width: '100%',
                boxSizing: 'border-box',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                background: 'linear-gradient(to bottom, transparent, rgba(34, 197, 94, 0.05))'
            }}>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    style={{
                        background: 'rgba(0, 0, 0, 0.7)',
                        borderRadius: '1rem',
                        border: '1px solid rgba(34, 197, 94, 0.3)',
                        padding: 'clamp(2rem, 4vw, 3rem)',
                        maxWidth: '400px',
                        width: '100%',
                        boxShadow: '0 0 30px rgba(34, 197, 94, 0.1)',
                        position: 'relative',
                        overflow: 'hidden'
                    }}
                >
                    {/* Effet de brillance */}
                    <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '1px',
                        background: 'linear-gradient(to right, transparent, #22c55e, transparent)',
                        opacity: 0.5
                    }}></div>

                    <h2 style={{
                        fontSize: 'clamp(1.5rem, 4vw, 2rem)',
                        color: '#22c55e',
                        textAlign: 'center',
                        marginBottom: '1.5rem',
                        textShadow: '0 0 8px rgba(34, 197, 94, 0.5)'
                    }}>
                        Abonnement Premium
                    </h2>

                    <div style={{
                        fontSize: 'clamp(2.5rem, 6vw, 3.5rem)',
                        fontWeight: 'bold',
                        color: 'white',
                        textAlign: 'center',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem'
                    }}>
                        <span>8€</span>
                        <span style={{
                            fontSize: 'clamp(1rem, 2vw, 1.25rem)',
                            color: '#9ca3af',
                            fontWeight: 'normal'
                        }}>/mois</span>
                    </div>

                    <p style={{
                        color: '#9ca3af',
                        textAlign: 'center',
                        marginBottom: '2rem',
                        fontSize: 'clamp(0.9rem, 2vw, 1rem)',
                        lineHeight: '1.6'
                    }}>
                        Accédez à toutes les fonctionnalités premium et devenez un maître des échecs
                    </p>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        style={{
                            width: '100%',
                            background: '#22c55e',
                            color: '#000000',
                            padding: 'clamp(0.75rem, 3vw, 1rem)',
                            borderRadius: '0.5rem',
                            border: 'none',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            fontSize: 'clamp(0.9rem, 2vw, 1rem)',
                            boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)',
                            transition: 'all 0.3s'
                        }}
                        onMouseEnter={handlePlayButtonMouseEnter}
                        onMouseLeave={handlePlayButtonMouseLeave}
                    >
                        COMMENCER MAINTENANT
                    </motion.button>
                </motion.div>
            </section>

            {/* Footer */}
            <footer style={{
                padding: 'clamp(1rem, 3vw, 2rem) 0',
                position: 'relative',
                zIndex: 2,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                width: '100%',
                boxSizing: 'border-box'
            }}>
                <div style={{
                    width: '100%',
                    margin: '0',
                    padding: '0 1rem',
                    boxSizing: 'border-box'
                }}>
                    <div style={{
                        display: 'flex',
                        flexDirection: window.innerWidth < 768 ? 'column' : 'row',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: '1rem',
                        textAlign: window.innerWidth < 768 ? 'center' : 'left'
                    }}>
                        <div style={{
                            fontSize: 'clamp(1.2rem, 4vw, 1.5rem)',
                            fontWeight: 'bold',
                            color: '#22c55e',
                            textShadow: '0 0 8px rgba(34, 197, 94, 0.5)'
                        }}>
                            PAWNED
                        </div>
                        <div style={{
                            display: 'flex',
                            gap: 'clamp(1rem, 4vw, 2rem)',
                            flexWrap: 'wrap',
                            justifyContent: 'center'
                        }}>
                            <a href="#" style={{
                                color: '#9ca3af',
                                textDecoration: 'none',
                                transition: 'color 0.3s',
                                fontSize: 'clamp(0.8rem, 2vw, 1rem)'
                            }}
                                onMouseEnter={(e) => handleMouseEnter(e, '#22c55e')}
                                onMouseLeave={(e) => handleMouseLeave(e, '#9ca3af')}
                            >
                                Mentions légales
                            </a>
                            <a href="#" style={{
                                color: '#9ca3af',
                                textDecoration: 'none',
                                transition: 'color 0.3s',
                                fontSize: 'clamp(0.8rem, 2vw, 1rem)'
                            }}
                                onMouseEnter={(e) => handleMouseEnter(e, '#22c55e')}
                                onMouseLeave={(e) => handleMouseLeave(e, '#9ca3af')}
                            >
                                Contact
                            </a>
                            <a href="#" style={{
                                color: '#9ca3af',
                                textDecoration: 'none',
                                transition: 'color 0.3s',
                                fontSize: 'clamp(0.8rem, 2vw, 1rem)'
                            }}
                                onMouseEnter={(e) => handleMouseEnter(e, '#22c55e')}
                                onMouseLeave={(e) => handleMouseLeave(e, '#9ca3af')}
                            >
                                À propos
                            </a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default LandingPage 