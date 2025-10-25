# database.py
import sqlite3
import logging

from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DatabaseHandler:
    def __init__(self, db_path='estoque.db'):
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()
        self.insert_sample_data()

    def connect(self):
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        logger.info("Conectado ao SQLite")

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                categoria TEXT NOT NULL,
                descricao TEXT,
                quantidade INTEGER DEFAULT 0,
                estoque_minimo INTEGER DEFAULT 10,
                estoque_critico INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                tipo_movimentacao TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                quantidade_anterior INTEGER,
                quantidade_atual INTEGER,
                usuario TEXT,
                fornecedor TEXT,
                destino TEXT,
                observacoes TEXT,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        self.connection.commit()

    def insert_sample_data(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM items")
        if cursor.fetchone()['count'] == 0:
            sample_items = [
                ('Luvas Cirúrgicas', 'EPI', 'Luvas de procedimento', 50, 20, 10),
                ('Máscara N95', 'EPI', 'Máscara de proteção N95', 8, 15, 5),
                ('Seringa 5ml', 'Insumos', 'Seringa descartável 5ml', 100, 30, 10),
                ('Agulha 25x7', 'Insumos', 'Agulha descartável', 4, 25, 8),
                ('Algodão', 'Insumos', 'Algodão hidrófilo', 40, 15, 5),
                ('Álcool 70%', 'Limpeza', 'Álcool em gel 70%', 20, 10, 3),

            ]
            cursor.executemany('''
                INSERT OR IGNORE INTO items (nome, categoria, descricao, quantidade, estoque_minimo, estoque_critico)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_items)
            self.connection.commit()

    def get_all_items(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM items ORDER BY nome')
        return [dict(r) for r in cursor.fetchall()]

    def get_stock_summary(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM items'); total_items = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as total FROM items WHERE quantidade > 0'); in_stock = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as total FROM items WHERE quantidade <= estoque_minimo'); low = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as total FROM items WHERE quantidade <= estoque_critico'); critical = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as total FROM movements WHERE DATE(data) = DATE("now")'); today_mov = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(DISTINCT categoria) as total FROM items'); total_cat = cursor.fetchone()['total']
        return {
            'total_items': total_items,
            'in_stock_items': in_stock,
            'low_stock_items': low,
            'critical_items': critical,
            'today_movements': today_mov,
            'total_categories': total_cat
        }

    def get_critical_items(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM items WHERE quantidade <= estoque_critico ORDER BY quantidade ASC')
        return [dict(r) for r in cursor.fetchall()]

    def get_recent_movements(self, days=30, limit=None):
        cursor = self.connection.cursor()
        query = '''
            SELECT m.*, i.nome as item_nome
            FROM movements m
            JOIN items i ON m.item_id = i.id
            WHERE m.data >= DATE('now', ?)
            ORDER BY m.data DESC
        '''
        params = [f'-{days} days']
        if limit:
            query += ' LIMIT ?'; params.append(limit)
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

    def update_stock(self, item_name, quantity, movement_type='saida', usuario='system', **kwargs):
        """
        quantity: POSITIVO (always positive)
        movement_type: 'entrada' or 'saida'
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM items WHERE nome = ?', (item_name,))
        item = cursor.fetchone()
        if not item:
            return {'success': False, 'error': 'Item não encontrado'}

        item = dict(item)
        prev = item['quantidade']
        if movement_type == 'entrada':
            new_q = prev + int(quantity)
        else:
            new_q = prev - int(quantity)

        if new_q < 0:
            return {'success': False, 'error': 'Estoque insuficiente'}

        cursor.execute('UPDATE items SET quantidade = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_q, item['id']))
        cursor.execute('''
            INSERT INTO movements (item_id, tipo_movimentacao, quantidade, quantidade_anterior, quantidade_atual, usuario, fornecedor, destino, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item['id'], movement_type, int(quantity), prev, new_q, usuario, kwargs.get('supplier'), kwargs.get('destination'), kwargs.get('notes')))
        self.connection.commit()
        return {'success': True, 'item': item_name, 'previous_quantity': prev, 'current_quantity': new_q, 'movement_type': movement_type, 'critical_threshold': item['estoque_critico']}

    def batch_update_stock(self, items, movement_type='saida', usuario='system'):
        results = []
        critical_items = []
        for it in items:
            name = it['name'] if 'name' in it else it.get('item')  # tolerate both keys
            qty = int(it['quantity'])
            res = self.update_stock(name, qty, movement_type=movement_type, usuario=usuario)
            results.append(res)
            if res.get('success') and res['current_quantity'] <= res.get('critical_threshold', 0):
                critical_items.append({'item': res['item'], 'current_quantity': res['current_quantity']})
        return {'success': True, 'results': results, 'critical_items': critical_items}

DB_NAME = "estoque.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Criar tabela de estoque
    cur.execute("""
            CREATE TABLE IF NOT EXISTS estoque (
                item TEXT PRIMARY KEY,
                quantidade INTEGER DEFAULT 0
            )
        """)

    # Criar tabela de histórico
    cur.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                acao TEXT,
                quantidade INTEGER,
                data TEXT
            )
        """)

    conn.commit()
    conn.close()


def update_stock(item, qtd):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Se o item já existe, atualiza
    cur.execute("SELECT quantidade FROM estoque WHERE item = ?", (item,))
    row = cur.fetchone()

    if row:
        nova_qtd = row[0] + qtd
        if nova_qtd < 0:
            nova_qtd = 0  # evita estoque negativo
        cur.execute("UPDATE estoque SET quantidade = ? WHERE item = ?", (nova_qtd, item))
    else:
        cur.execute("INSERT INTO estoque (item, quantidade) VALUES (?, ?)", (item, max(qtd, 0)))

    conn.commit()
    conn.close()


# ================= Buscar estoque =================
def get_stock():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT item, quantidade FROM estoque")
    data = cur.fetchall()
    conn.close()
    return data

# ================= Histórico =================
def add_history(item, acao, qtd):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO historico (item, acao, quantidade, data) VALUES (?, ?, ?, ?)",
        (item, acao, qtd, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM historico ORDER BY data DESC")
    data = cur.fetchall()
    conn.close()
    return data

def listar_itens_existentes():
    """Retorna uma lista com os nomes dos itens cadastrados no estoque."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT item FROM estoque ORDER BY item")
    data = [row[0] for row in cur.fetchall()]
    conn.close()
    return data