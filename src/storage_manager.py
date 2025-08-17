import sqlite3
import hashlib
from contextlib import contextmanager
import os
from typing import Optional

MAIN_DATABASE = "users.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(MAIN_DATABASE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Inicializa o banco de dados principal de usuários"""
    if not os.path.exists(MAIN_DATABASE):
        with open(MAIN_DATABASE, 'w'):
            pass

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            empresa TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            db_name TEXT UNIQUE NOT NULL
        )
        """)
        conn.commit()
        conn.close()

def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """Gera um hash seguro da senha usando PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    return password_hash, salt

def create_user(nome, email, empresa, usuario, senha):
    """Cria um novo usuário no banco de dados"""
    with get_db_connection() as conn:
        try:
            senha_hash, salt = hash_password(senha)
            db_name = f"user_{usuario.lower()}.db"
            
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO usuarios (nome, email, empresa, usuario, senha_hash, salt, db_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nome, email, empresa, usuario, senha_hash.hex(), salt.hex(), db_name)
            )
            
            conn.commit()
            conn.close()
            
            # Cria o banco de dados específico do usuário
            init_user_db(db_name)
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False

def init_user_db(db_name: str):
    """Inicializa o banco de dados específico do usuário"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    tabelas = [
            """CREATE TABLE IF NOT EXISTS funcionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cargo TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                data_admissao DATE NOT NULL,
                observacoes TEXT
            );""",
            
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funcionario_id INTEGER NOT NULL,
                username TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                nivel_acesso TEXT CHECK(nivel_acesso IN ('admin', 'gerente', 'vendedor')) NOT NULL,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE
            );""",
            
            """CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_fantasia TEXT NOT NULL UNIQUE,
                razao_social TEXT NOT NULL,
                cnpj TEXT NOT NULL UNIQUE,
                telefone TEXT NOT NULL,
                email TEXT,
                observacoes TEXT
            );""",
            
            """CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL CHECK(preco >= 0),
                preco_promocional REAL CHECK(preco_promocional >= 0 AND preco_promocional <= preco),
                custo_unitario REAL NOT NULL CHECK(custo_unitario >= 0),
                estoque_atual INTEGER NOT NULL DEFAULT 0 CHECK(estoque_atual >= 0),
                estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK(estoque_minimo >= 0),
                estoque_maximo INTEGER DEFAULT NULL CHECK(estoque_maximo IS NULL OR estoque_maximo >= estoque_minimo),
                fornecedor_id INTEGER NOT NULL,
                categoria TEXT,
                data_cadastro TEXT,
                data_atualizacao TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE
            );""",
            
            """CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf_cnpj TEXT NOT NULL UNIQUE,
                telefone TEXT,
                email TEXT,
                cep TEXT,
                cidade TEXT,
                estado TEXT,
                bairro TEXT,
                endereco TEXT,
                numero TEXT,
                complemento TEXT,
                data_cadastro TEXT
            );""",
            
            """CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                funcionario_id INTEGER NOT NULL,
                desconto REAL CHECK(desconto >= 0) DEFAULT 0,
                status TEXT CHECK(status IN ('Concluída', 'Pendente', 'Cancelada')) DEFAULT 'Pendente',
                total REAL NOT NULL CHECK(total >= 0),
                data_venda TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE
            );""",
            
            """CREATE TABLE IF NOT EXISTS itens_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venda_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade REAL NOT NULL CHECK(quantidade > 0),
                desconto REAL CHECK(desconto >= 0) DEFAULT 0,
                preco_unitario REAL NOT NULL CHECK(preco_unitario >= 0),
                subtotal REAL NOT NULL CHECK(subtotal >= 0),
                FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
            );""",

            """CREATE TABLE IF NOT EXISTS movimentacao_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo_movimentacao TEXT NOT NULL CHECK(tipo_movimentacao IN ('ENTRADA', 'SAIDA', 'AJUSTE', 'PERDA', 'DEVOLUCAO')),
                quantidade INTEGER NOT NULL,
                estoque_anterior INTEGER NOT NULL,
                estoque_atual INTEGER NOT NULL,
                motivo TEXT,
                referencia_id INTEGER,
                referencia_tipo TEXT,
                funcionario_id INTEGER,
                data_movimentacao TEXT DEFAULT (datetime('now')),
                observacoes TEXT,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE SET NULL
            );""",

            """CREATE TRIGGER IF NOT EXISTS trigger_baixa_estoque_venda
            AFTER INSERT ON itens_venda
            WHEN (SELECT status FROM vendas WHERE id = NEW.venda_id) = 'Concluída'
            BEGIN
                UPDATE produtos 
                SET estoque_atual = estoque_atual - NEW.quantidade,
                    data_atualizacao = datetime('now')
                WHERE id = NEW.produto_id 
                AND estoque_atual >= NEW.quantidade;
                INSERT INTO movimentacao_estoque (
                    produto_id, tipo_movimentacao, quantidade, 
                    estoque_anterior, estoque_atual, motivo,
                    referencia_id, referencia_tipo, funcionario_id
                )
                SELECT 
                    NEW.produto_id, 'SAIDA', NEW.quantidade,
                    p.estoque_atual + NEW.quantidade, p.estoque_atual,
                    'Venda de produto', NEW.venda_id, 'VENDA',
                    (SELECT funcionario_id FROM vendas WHERE id = NEW.venda_id)
                FROM produtos p WHERE p.id = NEW.produto_id;
            END;""",

            """CREATE TRIGGER IF NOT EXISTS trigger_venda_pendente
            AFTER INSERT ON vendas
            WHEN NEW.status = 'Pendente'
            BEGIN
                UPDATE produtos 
                SET estoque_atual = estoque_atual - (
                    SELECT quantidade FROM itens_venda
                    WHERE venda_id = NEW.id AND produto_id = produtos.id
                ),
                data_atualizacao = datetime('now')
                WHERE id IN (SELECT produto_id FROM itens_venda WHERE venda_id = NEW.id)
                AND estoque_atual >= (
                    SELECT quantidade FROM itens_venda 
                    WHERE venda_id = NEW.id AND produto_id = produtos.id
                );
                INSERT INTO movimentacao_estoque (
                    produto_id, tipo_movimentacao, quantidade,
                    estoque_anterior, estoque_atual, motivo,
                    referencia_id, referencia_tipo, funcionario_id
                )
                SELECT 
                    iv.produto_id, 'SAIDA', iv.quantidade,
                    p.estoque_atual + iv.quantidade, p.estoque_atual,
                    'Venda pendente', NEW.id, 'VENDA', NEW.funcionario_id
                FROM itens_venda iv
                JOIN produtos p ON p.id = iv.produto_id
                WHERE iv.venda_id = NEW.id;
            END;
            """,

        """CREATE TRIGGER IF NOT EXISTS trg_movimentacao_estoque_status
        AFTER UPDATE OF status ON vendas
        WHEN OLD.status != NEW.status
        BEGIN
            INSERT INTO movimentacao_estoque (
                produto_id, tipo_movimentacao, quantidade, 
                estoque_anterior, estoque_atual, motivo,
                referencia_id, referencia_tipo, funcionario_id,
                observacoes
            )
            SELECT 
                iv.produto_id,
                'SAIDA',
                iv.quantidade,
                p.estoque_atual,
                p.estoque_atual - iv.quantidade,
                'Venda concluída',
                NEW.id,
                'VENDA',
                NEW.funcionario_id,
                'Status alterado de ' || OLD.status || ' para ' || NEW.status
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = NEW.id 
            AND NEW.status = 'Concluída'
            AND OLD.status = 'Pendente';
            
            INSERT INTO movimentacao_estoque (
                produto_id, tipo_movimentacao, quantidade, 
                estoque_anterior, estoque_atual, motivo,
                referencia_id, referencia_tipo, funcionario_id,
                observacoes
            )
            SELECT 
                iv.produto_id,
                'DEVOLUCAO',
                iv.quantidade,
                p.estoque_atual,
                p.estoque_atual + iv.quantidade,
                'Venda cancelada',
                NEW.id,
                'VENDA',
                NEW.funcionario_id,
                'Status alterado de ' || OLD.status || ' para ' || NEW.status
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = NEW.id 
            AND NEW.status = 'Cancelada'
            AND OLD.status = 'Concluída';
            
            INSERT INTO movimentacao_estoque (
                produto_id, tipo_movimentacao, quantidade, 
                estoque_anterior, estoque_atual, motivo,
                referencia_id, referencia_tipo, funcionario_id,
                observacoes
            )
            SELECT 
                iv.produto_id,
                'SAIDA',
                iv.quantidade,
                p.estoque_atual,
                p.estoque_atual - iv.quantidade,
                'Reativação de venda',
                NEW.id,
                'VENDA',
                NEW.funcionario_id,
                'Status alterado de ' || OLD.status || ' para ' || NEW.status
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = NEW.id 
            AND NEW.status = 'Pendente'
            AND OLD.status = 'Cancelada';
            
            UPDATE produtos 
            SET estoque_atual = estoque_atual - (
                SELECT iv.quantidade 
                FROM itens_venda iv 
                WHERE iv.produto_id = produtos.id 
                AND iv.venda_id = NEW.id
            ),
            data_atualizacao = datetime('now')
            WHERE id IN (
                SELECT iv.produto_id 
                FROM itens_venda iv 
                WHERE iv.venda_id = NEW.id
            )
            AND ((NEW.status = 'Concluída' AND OLD.status = 'Pendente') 
                OR (NEW.status = 'Pendente' AND OLD.status = 'Cancelada'));
            
            UPDATE produtos 
            SET estoque_atual = estoque_atual + (
                SELECT iv.quantidade 
                FROM itens_venda iv 
                WHERE iv.produto_id = produtos.id 
                AND iv.venda_id = NEW.id
            ),
            data_atualizacao = datetime('now')
            WHERE id IN (
                SELECT iv.produto_id 
                FROM itens_venda iv 
                WHERE iv.venda_id = NEW.id
            )
            AND NEW.status = 'Cancelada' 
            AND OLD.status = 'Concluída';
            
        END;""",

        """CREATE TRIGGER IF NOT EXISTS trg_produto_adicionado
        AFTER INSERT ON produtos
        BEGIN
            INSERT INTO movimentacao_estoque (
                produto_id,
                tipo_movimentacao,
                quantidade,
                estoque_anterior,
                estoque_atual,
                motivo,
                referencia_id,
                referencia_tipo,
                funcionario_id,
                data_movimentacao,
                observacoes
            ) VALUES (
                NEW.id,
                'ENTRADA',
                NEW.estoque_atual,
                0,
                NEW.estoque_atual,
                'Estoque inicial do produto',
                NEW.id,
                'PRODUTO_NOVO',
                NULL, -- funcionario_id pode ser NULL para cadastros automáticos
                datetime('now'),
                'Produto cadastrado: ' || NEW.nome || ' - Estoque inicial: ' || NEW.estoque_atual
            );
        END;"""
        ]
    
    try:
        for tabela in tabelas:
            cursor.execute(tabela)
        conn.commit()
        print("Todas as tabelas foram criadas com sucesso!")
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
        conn.rollback()

def verify_user(usuario, senha):
    """Verifica o usuário e retorna seus dados se válido"""
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT senha_hash, salt, db_name FROM usuarios WHERE usuario = ?",
                (usuario,)
            )
            
            result = cursor.fetchone()
            
            if not result:
                return None
                
            stored_hash_hex, salt_hex, db_name = result
            stored_hash = bytes.fromhex(stored_hash_hex)
            salt = bytes.fromhex(salt_hex)
            
            new_hash, _ = hash_password(senha, salt)
            return db_name if new_hash == stored_hash else None
        except Exception as e:
            print(f"Erro ao verificar usuário: {e}")
            return None
        finally:
            conn.close()

def get_user_data(usuario):
    """Obtém os dados do usuário a partir do nome de usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome, email, empresa FROM usuarios WHERE usuario = ?",
            (usuario,)
        )
        return cursor.fetchone()