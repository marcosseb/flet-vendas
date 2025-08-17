import sqlite3

class EstoqueController:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def listar_movimentacoes(self):
        """
        Lista todas as movimentações cadastradas no banco de dados com informações relacionadas.

        Returns:
            list: Lista de dicionários com os dados das movimentações e informações relacionadas.
        """
        sql = """SELECT
                    me.*,
                    p.nome as produto_nome,
                    f.nome as funcionario_nome,
                    CASE 
                        WHEN me.referencia_tipo = 'VENDA' THEN 'Venda #' || me.referencia_id
                        WHEN me.referencia_tipo = 'COMPRA' THEN 'Compra #' || me.referencia_id
                        ELSE me.referencia_tipo || ' #' || COALESCE(me.referencia_id, '')
                    END as referencia_descricao
                FROM movimentacao_estoque me
                LEFT JOIN produtos p ON me.produto_id = p.id
                LEFT JOIN funcionarios f ON me.funcionario_id = f.id
                ORDER BY me.data_movimentacao DESC"""
        
        try:
            self.cursor.execute(sql)
            movimentacoes = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in movimentacoes]
        except sqlite3.Error as e:
            print(f"Erro ao listar movimentações: {e}")
            return []

    def atualizar_movimentacao(self, movimentacao_id: int, dados: dict) -> bool:
        """
        Atualiza uma movimentação de estoque existente.

        Args:
            movimentacao_id: ID da movimentação a ser atualizada
            dados: Dicionário com os campos a serem atualizados:
                - produto_id (int)
                - tipo_movimentacao (str)
                - quantidade (int)
                - estoque_anterior (int)
                - estoque_atual (int)
                - motivo (str, opcional)
                - referencia_id (int, opcional)
                - referencia_tipo (str, opcional)
                - funcionario_id (int, opcional)
                - observacoes (str, opcional)

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        sql = """UPDATE movimentacao_estoque
                 SET produto_id = :produto_id,
                     tipo_movimentacao = :tipo_movimentacao,
                     quantidade = :quantidade,
                     estoque_anterior = :estoque_anterior,
                     estoque_atual = :estoque_atual,
                     motivo = :motivo,
                     referencia_id = :referencia_id,
                     referencia_tipo = :referencia_tipo,
                     funcionario_id = :funcionario_id,
                     observacoes = :observacoes
                 WHERE id = :id"""
        try:
            self.cursor.execute(sql, {
                'id': movimentacao_id,
                'produto_id': dados['produto_id'],
                'tipo_movimentacao': dados['tipo_movimentacao'],
                'quantidade': dados['quantidade'],
                'estoque_anterior': dados['estoque_anterior'],
                'estoque_atual': dados['estoque_atual'],
                'motivo': dados.get('motivo'),
                'referencia_id': dados.get('referencia_id'),
                'referencia_tipo': dados.get('referencia_tipo'),
                'funcionario_id': dados.get('funcionario_id'),
                'observacoes': dados.get('observacoes')
            })
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar movimentação: {e}")
            return False

    def listar_id_e_produtos(self):
        """
        Lista os IDs e nomes dos produtos cadastrados no banco de dados.

        Returns:
            list: Lista de dicionários com os IDs e nomes dos produtos.
        """
        sql = "SELECT id, nome FROM produtos ORDER BY nome"
        try:
            self.cursor.execute(sql)
            produtos = self.cursor.fetchall()
            return [{'id': row[0], 'nome': row[1]} for row in produtos]
        except sqlite3.Error as e:
            print(f"Erro ao listar produtos: {e}")
            return []
        
    def listar_id_e_funcionarios(self):
        """
        Lista os IDs e nomes dos funcionários cadastrados no banco de dados.

        Returns:
            list: Lista de dicionários com os IDs e nomes dos funcionários.
        """
        sql = "SELECT id, nome FROM funcionarios ORDER BY nome"
        try:
            self.cursor.execute(sql)
            funcionarios = self.cursor.fetchall()
            return [{'id': row[0], 'nome': row[1]} for row in funcionarios]
        except sqlite3.Error as e:
            print(f"Erro ao listar funcionários: {e}")
            return []
