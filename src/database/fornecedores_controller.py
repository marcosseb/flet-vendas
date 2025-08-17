import sqlite3

class FornecedoresController:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def cadastrar_fornecedor(self, fornecedor_data):
        """
        Cadastra um novo fornecedor no banco de dados
        
        Args:
            fornecedor_data (dict): Dicionário contendo os dados do fornecedor:
                {
                    'nome_fantasia': str,
                    'razao_social': str,
                    'cnpj': str,
                    'telefone': str,
                    'email': str,
                    'observacoes': str,
                }
        
        Returns:
            int: ID do fornecedor cadastrado ou None em caso de erro
        """
        sql = """INSERT INTO fornecedores (
                nome_fantasia,
                razao_social,
                cnpj,
                telefone,
                'email',
                'observacoes'
            ) VALUES (?, ?, ?, ?, ?, ?)"""
        
        try:
            self.cursor.execute(sql, (
                fornecedor_data['nome_fantasia'],
                fornecedor_data['razao_social'],
                fornecedor_data['cnpj'],
                fornecedor_data.get('telefone'),
                fornecedor_data.get('email'),
                fornecedor_data.get('observacoes')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar fornecedor: {e}")
            return None
        
    def listar_fornecedores(self):
        """
        Lista todos os fornecedores cadastrados no banco de dados
        
        Returns:
            list: Lista de dicionários com os dados dos fornecedores
        """
        sql = "SELECT * FROM fornecedores"
        try:
            self.cursor.execute(sql)
            fornedores = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in fornedores]
        except sqlite3.Error as e:
            print(f"Erro ao listar fornecedores: {e}")
            self.conn.rollback()
            return []
        
    def atualizar_fornecedor(self, fornecedor_id, fornecedor_data):
        """
        Atualiza os dados de um fornecedor existente
        
        Args:
            fornecedor_id (int): ID do fornecedor a ser atualizado
            fornecedor_data (dict): Dicionário com os novos dados do fornecedor
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        sql = """UPDATE fornecedores SET 
                nome_fantasia = ?, 
                razao_social = ?, 
                cnpj = ?, 
                telefone = ?, 
                email = ?, 
                observacoes = ? 
            WHERE id = ?"""
        
        try:
            self.cursor.execute(sql, (
                fornecedor_data['nome_fantasia'],
                fornecedor_data['razao_social'],
                fornecedor_data['cnpj'],
                fornecedor_data.get('telefone'),
                fornecedor_data.get('email'),
                fornecedor_data.get('observacoes'),
                fornecedor_id
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar fornecedor: {e}")
            self.conn.rollback()
            return False
        
    def excluir_fornecedor(self, fornecedor_id):
        """
        Exclui um fornecedor do banco de dados
        
        Args:
            fornecedor_id (int): ID do fornecedor a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        sql = "DELETE FROM fornecedores WHERE id = ?"
        
        try:
            self.cursor.execute(sql, (fornecedor_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Fornecedor ID {fornecedor_id} excluído com sucesso!")
                return True
            else:
                print(f"Nenhum fornecedor encontrado com ID {fornecedor_id}.")
                return False
        except sqlite3.Error as e:
            print(f"Erro ao excluir fornecedor: {e}")
            self.conn.rollback()
            return False
        
    
        
if __name__ == "__main__":
    db = FornecedoresController()

    list1 = db.listar_fornecedores()

    print('Listando Fornecedores:')
    for fornecedor in list1:
        print(fornecedor)