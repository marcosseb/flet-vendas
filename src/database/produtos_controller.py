import sqlite3

class ProdutosController:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def cadastrar_produto(self, produto_data):
        """
        Cadastra um novo produto no banco de dados
        
        Args:
            produto_data (dict): Dicionário contendo os dados do produto:
                {
                    'nome': str,
                    'descricao': str,
                    'preco': float,
                    'preco_promocional': float,
                    'custo_unitario': float,
                    'estoque': int,
                    'fornecedor_id': int,
                    'categoria': str,
                    'data_cadastro': str
                }
        
        Returns:
            int: ID do produto cadastrado ou None em caso de erro
        """
        sql = """INSERT INTO produtos (
                nome,
                descricao,
                preco,
                preco_promocional,
                custo_unitario,
                estoque_atual,
                estoque_minimo,
                estoque_maximo,
                fornecedor_id,
                categoria,
                data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            self.cursor.execute(sql, (
                produto_data['nome'],
                produto_data.get('descricao'),
                produto_data['preco'],
                produto_data.get('preco_promocional'),
                produto_data['custo_unitario'],
                produto_data['estoque_atual'],  # Alterado de 'estoque' para 'estoque_atual'
                produto_data.get('estoque_minimo', 0),  # Novo campo com valor padrão 0
                produto_data.get('estoque_maximo'),  # Novo campo (opcional)
                produto_data['fornecedor_id'],
                produto_data.get('categoria'),
                produto_data.get('data_cadastro')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar produto: {e}")
            return None


    def listar_produtos(self):
        """
        Lista todos os produtos cadastrados no banco de dados com nome do fornecedor
        
        Returns:
            list: Lista de dicionários com os dados dos produtos
        """
        sql = """SELECT 
                    p.*,
                    f.nome_fantasia as fornecedor
                FROM produtos p
                LEFT JOIN fornecedores f ON p.fornecedor_id = f.id"""
        try:
            self.cursor.execute(sql)
            produtos = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in produtos]
        except sqlite3.Error as e:
            print(f"Erro ao listar produtos: {e}")
            return []
        
    def atualizar_produto(self, produto_id, produto_data):
        """
        Atualiza os dados de um produto existente
        
        Args:
            produto_id (int): ID do produto a ser atualizado
            produto_data (dict): Dicionário com os novos dados do produto:
                {
                    'nome': str,
                    'descricao': str,
                    'preco': float,
                    'preco_promocional': float,
                    'custo_unitario': float,
                    'estoque': int,
                    'fornecedor_id': int,
                    'categoria': str,
                    'data_cadastro': str (formato 'YYYY-MM-DD')
                }
        
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        sql = """UPDATE produtos SET
                nome = ?,
                descricao = ?,
                preco = ?,
                preco_promocional = ?,
                custo_unitario = ?,
                estoque_atual = ?,
                estoque_minimo = ?,
                estoque_maximo = ?,
                fornecedor_id = ?,
                categoria = ?,
                data_cadastro = ?,
                data_atualizacao = datetime('now')
            WHERE id = ?"""
        try:
            self.cursor.execute(sql, (
                produto_data['nome'],
                produto_data.get('descricao'),
                produto_data['preco'],
                produto_data.get('preco_promocional'),
                produto_data['custo_unitario'],
                produto_data['estoque_atual'],  # Alterado de 'estoque' para 'estoque_atual'
                produto_data.get('estoque_minimo', 0),  # Novo campo com valor padrão 0
                produto_data.get('estoque_maximo'),  # Novo campo (opcional)
                produto_data['fornecedor_id'],
                produto_data.get('categoria'),
                produto_data.get('data_cadastro'),
                produto_id
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")
            return False
        
    def excluir_produto(self, produto_id):
        """
        Exclui um produto do banco de dados
        
        Args:
            produto_id (int): ID do produto a ser excluído
        
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        sql = "DELETE FROM produtos WHERE id = ?"
        try:
            self.cursor.execute(sql, (produto_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir produto: {e}")
            return False
        
    def listar_id_e_fornecedores(self):
        """
        Lista apenas os nomes dos fornecedores cadastrados
        
        Returns:
            list: Lista de strings com os nomes dos fornecedores
        """
        sql = "SELECT id, nome_fantasia FROM fornecedores"
        try:
            self.cursor.execute(sql)
            nomes = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in nomes]
        except sqlite3.Error as e:
            print(f"Erro ao listar nomes de fornecedores: {e}")
            return []
    
if __name__ == "__main__":
    db = ProdutosController()

    print(db.listar_id_e_fornecedores())