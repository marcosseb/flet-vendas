import sqlite3


class VendasController:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def cadastrar_itens_venda(self, venda_id, itens_data):
        """
        Cadastra os itens de uma venda no banco de dados
        Args:
            venda_id (int): ID da venda à qual os itens pertencem
            itens_data (list): Lista de dicionários contendo os dados dos itens:
                [
                    {
                        'produto_id': int,
                        'quantidade': float,
                        'preco_unitario': float,
                        'desconto': float,
                        'subtotal': float
                    },
                    ...
                ]
        Returns:
            list: Lista de IDs dos itens cadastrados ou None em caso de erro
        """
        sql = """INSERT INTO itens_venda (
                venda_id,
                produto_id,
                quantidade,
                preco_unitario,
                desconto,
                subtotal
            ) VALUES (?, ?, ?, ?, ?, ?)"""
        itens_ids = []
        try:
            print(f"Venda cadastrada com sucesso! ID: {venda_id}")
            for item in itens_data:
                self.cursor.execute(sql, (
                    venda_id,
                    item['produto_id'],
                    item['quantidade'],
                    item['preco_unitario'],
                    item.get('desconto', 0.0),
                    item['subtotal']
                ))
                itens_ids.append(self.cursor.lastrowid)
            self.conn.commit()
            return itens_ids
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar itens de venda: {e}")
            return None

    def cadastrar_venda(self, venda_data):
        """
        Cadastra uma nova venda no banco de dados
        
        Args:
            venda_data (dict): Dicionário contendo os dados da venda:
                {
                    'cliente_id': int,
                    'funcionario_id': int,
                    'desconto': float,
                    'status': str,
                    'total': float,
                    'data_venda': str,
                    'itens': list
                }
        
        Returns:
            int: ID da venda cadastrada ou None em caso de erro
        """
        sql = """INSERT INTO vendas (
                cliente_id,
                funcionario_id,
                desconto,
                status,
                total,
                data_venda
            ) VALUES (?, ?, ?, ?, ?, ?)"""
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            self.cursor.execute(sql, (
                venda_data['cliente_id'],
                venda_data['funcionario_id'],
                venda_data.get('desconto', 0.0),
                venda_data.get('status', 'Pendente'),
                venda_data['total'],
                venda_data.get('data_venda', 'CURRENT_TIMESTAMP')
            ))
            venda_id = self.cursor.lastrowid
            
            # Cadastra os itens da venda
            if venda_data.get('itens'):
                result = self.cadastrar_itens_venda(venda_id, venda_data['itens'])
                if result is None:
                    raise Exception("Erro ao cadastrar itens da venda")
            
            self.conn.commit()
            return venda_id
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erro ao cadastrar venda: {e}")
            return None
        
    def listar_vendas(self):
        """
        Lista todas as vendas cadastradas no banco de dados
        
        Returns:
            list: Lista de dicionários com os dados das vendas
        """
        sql = """SELECT v.*, c.nome AS cliente_nome, f.nome AS funcionario_nome
                 FROM vendas v
                 JOIN clientes c ON v.cliente_id = c.id
                 JOIN funcionarios f ON v.funcionario_id = f.id"""
        try:
            self.cursor.execute(sql)
            vendas = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in vendas]
        except sqlite3.Error as e:
            print(f"Erro ao listar vendas: {e}")
            return []
        
    def listar_produtos(self):
        """
        Lista todos os produtos cadastrados no banco de dados
        
        Returns:
            list: Lista de dicionários com os dados dos produtos
        """
        sql = "SELECT * FROM produtos"
        try:
            self.cursor.execute(sql)
            produtos = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in produtos]
        except sqlite3.Error as e:
            print(f"Erro ao listar produtos: {e}")
            return []

    def buscar_venda_por_id(self, venda_id):
        """
        Busca uma venda específica pelo ID, incluindo seus itens
        
        Args:
            venda_id (int): ID da venda a ser buscada
        
        Returns:
            dict: Dados da venda com seus itens ou None se não encontrada
        """
        # Busca os dados principais da venda
        sql_venda = """SELECT v.*, c.nome AS cliente_nome, f.nome AS funcionario_nome
                      FROM vendas v
                      JOIN clientes c ON v.cliente_id = c.id
                      JOIN funcionarios f ON v.funcionario_id = f.id
                      WHERE v.id = ?"""
        
        # Busca os itens da venda
        sql_itens = """SELECT iv.*, p.nome AS produto_nome
                      FROM itens_venda iv
                      JOIN produtos p ON iv.produto_id = p.id
                      WHERE iv.venda_id = ?"""
        
        try:
            # Busca a venda
            self.cursor.execute(sql_venda, (venda_id,))
            venda_row = self.cursor.fetchone()
            
            if not venda_row:
                return None
            
            # Converte para dicionário
            venda = dict(zip([column[0] for column in self.cursor.description], venda_row))
            
            # Busca os itens
            self.cursor.execute(sql_itens, (venda_id,))
            itens_rows = self.cursor.fetchall()
            
            # Converte itens para lista de dicionários
            itens = []
            if itens_rows:
                for item_row in itens_rows:
                    item = dict(zip([column[0] for column in self.cursor.description], item_row))
                    itens.append(item)
            
            venda['itens'] = itens
            return venda
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar venda: {e}")
            return None

    def excluir_venda(self, venda_id):
        """
        Exclui uma venda e seus itens associados do banco de dados.

        Args:
            venda_id (int): ID da venda a ser excluída.

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário.
        """
        try:
            # Exclui os itens da venda primeiro devido à chave estrangeira
            self.cursor.execute("DELETE FROM itens_venda WHERE venda_id = ?", (venda_id,))
            # Exclui a venda principal
            self.cursor.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir venda: {e}")
            self.conn.rollback()
            return False

    def atualizar_venda(self, venda_id, venda_data):
        """
        Atualiza uma venda existente no banco de dados.

        Args:
            venda_id (int): ID da venda a ser atualizada.
            venda_data (dict): Dados atualizados da venda.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.
        """
        sql = """UPDATE vendas SET
                cliente_id = ?,
                funcionario_id = ?,
                desconto = ?,
                status = ?,
                total = ?,
                data_venda = ?
            WHERE id = ?"""
        try:
            self.cursor.execute(sql, (
                venda_data['cliente_id'],
                venda_data['funcionario_id'],
                venda_data.get('desconto', 0.0),
                venda_data.get('status', 'Pendente'),
                venda_data['total'],
                venda_data.get('data_venda', 'CURRENT_TIMESTAMP'),
                venda_id
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar venda: {e}")
            self.conn.rollback()
            return False

    def atualizar_itens_venda(self, venda_id, itens_data):
        """
        Atualiza os itens de uma venda existente.

        Args:
            venda_id (int): ID da venda.
            itens_data (list): Lista de itens atualizados.

        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário.
        """
        try:
            # Remove itens antigos
            self.cursor.execute("DELETE FROM itens_venda WHERE venda_id = ?", (venda_id,))
            # Adiciona novos itens
            if itens_data:
                self.cadastrar_itens_venda(venda_id, itens_data)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar itens da venda: {e}")
            self.conn.rollback()
            return False

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
        except sqlite3.Error as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def remover_itens_venda(self, venda_id):
        """
        Remove todos os itens de uma venda específica.

        Args:
            venda_id (int): ID da venda cujos itens serão removidos.

        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário.
        """
        try:
            self.cursor.execute("DELETE FROM itens_venda WHERE venda_id = ?", (venda_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao remover itens da venda: {e}")
            self.conn.rollback()
            return False

    def listar_itens_venda(self):
        """
        Lista todos os itens de venda cadastrados no banco de dados.
        Returns:
            list: Lista de dicionários com os dados dos itens de venda
        """
        sql = """SELECT iv.*, v.data_venda, p.nome AS produto_nome
                 FROM itens_venda iv
                 JOIN vendas v ON iv.venda_id = v.id
                 JOIN produtos p ON iv.produto_id = p.id"""
        try:
            self.cursor.execute(sql)
            itens_venda = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in itens_venda]
        except sqlite3.Error as e:
            print(f"Erro ao listar itens de venda: {e}")
            return []
        

    def __del__(self):
        """
        Fecha a conexão com o banco de dados ao deletar a instância
        """
        self.conn.close()
        print("Conexão com o banco de dados fechada.")