import sqlite3

class FuncionariosController:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()


    def cadastrar_funcionario(self, funcionario_data):
        """
        Cadastra um novo funcionário no banco de dados
        
        Args:
            funcionario_data (dict): Dicionário contendo os dados do funcionário:
                {
                    'nome': str,
                    'cargo': str,
                    'telefone': str (opcional),
                    'email': str (opcional),
                    'data_admissao': str (formato YYYY-MM-DD),
                    'observacoes': str (opcional),
                }
        
        Returns:
            int: ID do funcionário cadastrado ou None em caso de erro
        """
        sql = """INSERT INTO funcionarios (
                    nome, 
                    cargo, 
                    telefone, 
                    email,
                    data_admissao,
                    observacoes
                ) VALUES (?, ?, ?, ?, ?, ?)"""
        
        try:
            self.cursor.execute(sql, (
                funcionario_data['nome'],
                funcionario_data['cargo'],
                funcionario_data.get('telefone'),
                funcionario_data.get('email'),
                funcionario_data['data_admissao'],
                funcionario_data.get('observacoes')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar funcionário: {e}")
            self.conn.rollback()
            return None
    
    def listar_funcionarios(self):
        """
        Lista todos os funcionários cadastrados no banco de dados
        
        Returns:
            list: Lista de dicionários com os dados dos funcionários
        """
        sql = "SELECT * FROM funcionarios"
        try:
            self.cursor.execute(sql)
            funcionarios = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in funcionarios]
        except sqlite3.Error as e:
            print(f"Erro ao listar funcionários: {e}")
            return []
        
    def atualizar_funcionario(self, funcionario_id, funcionario_data):
        """
        Atualiza os dados de um funcionário existente
        
        Args:
            funcionario_id (int): ID do funcionário a ser atualizado
            funcionario_data (dict): Dicionário com os novos dados do funcionário
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        sql = """UPDATE funcionarios SET 
                    nome = ?, 
                    cargo = ?, 
                    telefone = ?, 
                    email = ?,
                    data_admissao = ?,
                    observacoes = ?
                WHERE id = ?"""
        
        try:
            self.cursor.execute(sql, (
                funcionario_data['nome'],
                funcionario_data['cargo'],
                funcionario_data.get('telefone'),
                funcionario_data.get('email'),
                funcionario_data['data_admissao'],
                funcionario_data.get('observacoes'),
                funcionario_id
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar funcionário: {e}")
            self.conn.rollback()
            return False
        
    def excluir_funcionario(self, funcionario_id):
        """
        Exclui um funcionário do banco de dados
        
        Args:
            funcionario_id (int): ID do funcionário a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        sql = "DELETE FROM funcionarios WHERE id = ?"
        
        try:
            self.cursor.execute(sql, (funcionario_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir funcionário: {e}")
            self.conn.rollback()
            return False