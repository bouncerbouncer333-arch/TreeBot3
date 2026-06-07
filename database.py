import sqlite3

DB_NAME = "family_tree.db"

def init_db():
    """Инициализация базы данных и создание таблиц"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            spouse_id INTEGER,
            status TEXT DEFAULT 'single',
            FOREIGN KEY(spouse_id) REFERENCES users(id)
        )
    ''')
    
    # Таблица детей (связь родители -> дети)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            parent_id INTEGER,
            child_id INTEGER,
            PRIMARY KEY (parent_id, child_id),
            FOREIGN KEY(parent_id) REFERENCES users(id),
            FOREIGN KEY(child_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(user_id, username):
    """Регистрация или обновление имени пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, username) VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET username = excluded.username
    ''', (user_id, username))
    conn.commit()
    conn.close()

def get_user(user_id):
    """Получение данных пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, spouse_id, status FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def marry_users(user1_id, user2_id):
    """Заключение брака между двумя пользователями"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET spouse_id = ?, status = "married" WHERE id = ?', (user2_id, user1_id))
    cursor.execute('UPDATE users SET spouse_id = ?, status = "married" WHERE id = ?', (user1_id, user2_id))
    conn.commit()
    conn.close()

def divorce_users(user1_id, user2_id):
    """Расторжение брака"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET spouse_id = NULL, status = "divorced" WHERE id = ?', (user1_id,))
    cursor.execute('UPDATE users SET spouse_id = NULL, status = "divorced" WHERE id = ?', (user2_id,))
    conn.commit()
    conn.close()

def adopt_child(parent_id, child_id):
    """Добавление ребенка родителю"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO children (parent_id, child_id) VALUES (?, ?)', (parent_id, child_id))
    conn.commit()
    conn.close()

def remove_child(parent_id, child_id):
    """Удаление ребенка у родителя (отказ от прав)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM children WHERE parent_id = ? AND child_id = ?', (parent_id, child_id))
    conn.commit()
    conn.close()

def get_children(user_id):
    """Возвращает список детей пользователя (id и username)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.id, users.username FROM children
        JOIN users ON children.child_id = users.id
        WHERE children.parent_id = ?
    ''', (user_id,))
    children = cursor.fetchall()
    conn.close()
    return children

def get_parents(user_id):
    """Возвращает список родителей пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.id, users.username FROM children
        JOIN users ON children.parent_id = users.id
        WHERE children.child_id = ?
    ''', (user_id,))
    parents = cursor.fetchall()
    conn.close()
    return parents

def get_children_count(user_id):
    """Возвращает количество детей у пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor
