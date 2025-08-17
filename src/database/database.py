import sqlite3

class Database:
    def __init__(self, db_name='sistema_vendas.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()
        print(f"Banco de dados '{db_name}' conectado com sucesso!")

    def criar_tabelas(self):
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
                estoque INTEGER NOT NULL DEFAULT 0 CHECK(estoque >= 0),
                fornecedor_id INTEGER NOT NULL,
                categoria TEXT,
                data_cadastro TEXT,
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
            );"""
        ]

        try:
            for tabela in tabelas:
                self.cursor.execute(tabela)
            self.conn.commit()
            print("Todas as tabelas foram criadas com sucesso!")
            
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
            self.conn.rollback()

    def fechar_conexao(self):
        self.conn.close()
        print("Conexão com o banco de dados fechada.")

# Exemplo de uso
if __name__ == "__main__":
    db = Database()
    
    # Para manter o banco aberto durante testes (opcional)
    # input("Pressione Enter para fechar a conexão...")
    db.fechar_conexao()