import mysql.connector

# Connexion à la base de données
conn = mysql.connector.connect(
    host='localhost',
    user='hess_user',
    password='hess_password',
    database='hess_db',
    port=3306
)

cursor = conn.cursor()

# Création de la table users si elle n'existe pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    )
''')

# Insertion d'un utilisateur exemple
cursor.execute('''
    INSERT INTO users (name, email) VALUES (%s, %s)
''', ("Alice", "alice@example.com"))

conn.commit()

# Affichage des utilisateurs
cursor.execute('SELECT * FROM users')
for user in cursor.fetchall():
    print(user)

cursor.close()
conn.close() 