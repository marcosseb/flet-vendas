import sqlite3

class ClientesController:
    def __init__(self, db_name:str):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def cadastrar_cliente(self, cliente_data):
        """
        Cadastra um novo cliente no banco de dados
        
        Args:
            cliente_data (dict): Dicionário contendo os dados do cliente:
                {
                    'nome': str,
                    'cpf_cnpj': str,
                    'telefone': str (opcional),
                    'email': str (opcional),
                    'cep': str (opcional),
                    'cidade': str (opcional),
                    'estado': str (opcional),
                    'bairro': str (opcional),
                    'endereco': str (opcional),
                    'numero': str (opcional),
                    'complemento': str (opcional)
                }
        
        Returns:
            int: ID do cliente cadastrado ou None em caso de erro
        """
        sql = """INSERT INTO clientes (
                    nome, 
                    cpf_cnpj, 
                    telefone, 
                    email, 
                    cep, 
                    cidade, 
                    estado, 
                    bairro, 
                    endereco, 
                    numero, 
                    complemento,
                    data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        try:
            self.cursor.execute(sql, (
                cliente_data['nome'],
                cliente_data['cpf_cnpj'],
                cliente_data.get('telefone'),
                cliente_data.get('email'),
                cliente_data.get('cep'),
                cliente_data.get('cidade'),
                cliente_data.get('estado'),
                cliente_data.get('bairro'),
                cliente_data.get('endereco'),
                cliente_data.get('numero'),
                cliente_data.get('complemento'),
                cliente_data.get('data_cadastro')
            ))
            self.conn.commit()
            print(f"Cliente {cliente_data['nome']} cadastrado com sucesso!")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"Erro: CPF/CNPJ {cliente_data['cpf_cnpj']} já cadastrado!")
            else:
                print(f"Erro de integridade ao cadastrar cliente: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"Erro inesperado ao cadastrar cliente: {e}")
            self.conn.rollback()
            return None
        
    def listar_clientes(self):
        """
        Lista todos os clientes cadastrados no banco de dados
        
        Returns:
            list: Lista de dicionários com os dados dos clientes
        """
        sql = "SELECT * FROM clientes"
        try:
            self.cursor.execute(sql)
            clientes = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in clientes]
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            self.conn.rollback()
            return []
        
    def atualizar_cliente(self, cliente_id, cliente_data):
        """
        Atualiza os dados de um cliente existente
        
        Args:
            cliente_id (int): ID do cliente a ser atualizado
            cliente_data (dict): Dicionário com os novos dados do cliente
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        sql = """UPDATE clientes SET 
                    nome = ?, 
                    cpf_cnpj = ?, 
                    telefone = ?, 
                    email = ?, 
                    cep = ?, 
                    cidade = ?, 
                    estado = ?, 
                    bairro = ?, 
                    endereco = ?, 
                    numero = ?, 
                    complemento = ?
                WHERE id = ?"""
        
        try:
            self.cursor.execute(sql, (
                cliente_data['nome'],
                cliente_data['cpf_cnpj'],
                cliente_data.get('telefone'),
                cliente_data.get('email'),
                cliente_data.get('cep'),
                cliente_data.get('cidade'),
                cliente_data.get('estado'),
                cliente_data.get('bairro'),
                cliente_data.get('endereco'),
                cliente_data.get('numero'),
                cliente_data.get('complemento'),
                cliente_id
            ))
            self.conn.commit()
            print(f"Cliente ID {cliente_id} atualizado com sucesso!")
            return True
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"Erro: CPF/CNPJ {cliente_data['cpf_cnpj']} já cadastrado!")
            else:
                print(f"Erro de integridade ao atualizar cliente: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Erro inesperado ao atualizar cliente: {e}")
            self.conn.rollback()
            return False
    
    def excluir_cliente(self, cliente_id):
        """
        Exclui um cliente do banco de dados
        
        Args:
            cliente_id (int): ID do cliente a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        sql = "DELETE FROM clientes WHERE id = ?"
        
        try:
            self.cursor.execute(sql, (cliente_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Cliente ID {cliente_id} excluído com sucesso!")
                return True
            else:
                print(f"Nenhum cliente encontrado com ID {cliente_id}.")
                return False
        except Exception as e:
            print(f"Erro ao excluir cliente: {e}")
            self.conn.rollback()
            return False
    

if __name__ == "__main__":
    """ db_controller = ClientesController()
    
    list1 = db_controller.listar_clientes()

    print("Lista de Clientes:")
    for cliente in list1:
        print(cliente) """