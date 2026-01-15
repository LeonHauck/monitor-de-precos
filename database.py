import sqlite3
from datetime import datetime

# --- O QUE É ESSE ARQUIVO? ---
# Este arquivo é responsável por guardar as informações. 
# Imagine que o Scraper é o "olho" que vê o preço, e o Banco de Dados é o "caderno" que anota.

DB_NAME = "monitor.db"

def init_db():
    """Cria as tabelas no banco de dados se elas não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Criamos uma tabela para os produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            target_price REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Adicionamos a coluna created_at caso ela não exista (Migração simples)
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass # A coluna já existe

    
    # Criamos uma tabela para o histórico de preços
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

def add_product(name, url, target_price):
    """Adiciona um novo produto ao monitoramento."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, url, target_price) VALUES (?, ?, ?)', 
                       (name, url, target_price))
        conn.commit()
        conn.close()
        print(f"Produto '{name}' adicionado!")
    except sqlite3.IntegrityError:
        print("Este produto já está sendo monitorado.")

def save_price(product_url, price):
    """Salva um novo preço encontrado no histórico."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Primeiro, pegamos o ID do produto pela URL
    cursor.execute('SELECT id FROM products WHERE url = ?', (product_url,))
    result = cursor.fetchone()
    
    if result:
        product_id = result[0]
        cursor.execute('INSERT INTO price_history (product_id, price) VALUES (?, ?)', 
                       (product_id, price))
        conn.commit()
        print(f"Preço de R$ {price:.2f} salvo no histórico.")
    else:
        print("Produto não encontrado no banco de dados para salvar o preço.")
        
    conn.close()

def get_products():
    """Retorna a lista de todos os produtos monitorados."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def get_history(product_id):
    """Retorna o histórico de preços de um produto específico."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT price, timestamp 
        FROM price_history 
        WHERE product_id = ? 
        ORDER BY timestamp DESC
    ''', (product_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def delete_product(product_id):
    """Remove um produto e seu histórico."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def update_product_price(product_id, new_price):
    """Atualiza o preço alvo de um produto."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET target_price = ? WHERE id = ?', (new_price, product_id))
    conn.commit()
    conn.close()



if __name__ == "__main__":

    # Quando rodamos este arquivo direto, ele apenas cria o banco
    init_db()
