import sqlite3

DB_NAME = "family.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            spouse_id INTEGER DEFAULT NULL,
            marriage_status TEXT DEFAULT 'single'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            parent_id INTEGER,
            child_id INTEGER,
            PRIMARY KEY (parent_id, child_id)
        )
    ''')
    conn.commit()
    conn.close()

def register_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username) 
        VALUES (?, ?)
    ''', (user_id, username))
    conn.commit()
    conn.close()

def marry_users(user1_id, user2_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET spouse_id = ?, marriage_status = 'married' WHERE user_id = ?
    ''', (user2_id, user1_id))
    cursor.execute('''
        UPDATE users SET spouse_id = ?, marriage_status = 'married' WHERE user_id = ?
    ''', (user1_id, user2_id))
    conn.commit()
    conn.close()

def divorce_users(user1_id, user2_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET marriage_status = 'divorced' WHERE user_id = ?", (user1_id,))
    cursor.execute("UPDATE users SET marriage_status = 'divorced' WHERE user_id = ?", (user2_id,))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, spouse_id, marriage_status FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def adopt_child(parent_id, child_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO children (parent_id, child_id) VALUES (?, ?)', (parent_id, child_id))
    conn.commit()
    conn.close()

def remove_child(parent_id, child_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM children WHERE parent_id = ? AND child_id = ?', (parent_id, child_id))
    conn.commit()
    conn.close()

def get_children_count(parent_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM children WHERE parent_id = ?", (parent_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_children(parent_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.user_id, u.username FROM children c 
        JOIN users u ON c.child_id = u.user_id 
        WHERE c.parent_id = ?
    ''', (parent_id,))
    children = cursor.fetchall()
    conn.close()
    return children

def get_parents(child_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.user_id, u.username FROM children c 
        JOIN users u ON c.parent_id = u.user_id 
        WHERE c.child_id = ?
    ''', (child_id,))
    parents = cursor.fetchall()
    conn.close()
    return parents
