import flet as ft
import datetime
import globals
import asyncio
from database.vendas_controller import VendasController

venda_atual = []
venda_id = None

_clock_task = None

def View(page: ft.Page):
    db_vendas = VendasController(page.client_storage.get("user_db"))
    global _clock_task
    produtos = db_vendas.listar_produtos()
    clientes = db_vendas.listar_clientes()
    print(clientes)
    funcionarios = db_vendas.listar_funcionarios()

    nome_empresa = ft.Text(
        color=ft.Colors.WHITE,
        size=16,
        weight=ft.FontWeight.BOLD,
        value=page.client_storage.get("empresa_logada") or "Empresa não identificada"
    )

    def vaiPraVendas(e):
        # Ao sair da View, cancela a tarefa do relógio
        if _clock_task and not _clock_task.done():
            _clock_task.cancel()
            print("Tarefa atualiza_tempo cancelada.") # Para depuração
        page.go("/vendas")

    sugestoes_clientes = [c["nome"] for c in clientes]
    print(f"Sugestões de clientes: {sugestoes_clientes}")  # Para depuração

    def sugerir_cliente(e):
        texto = cliente_input.value.lower()
        cliente_input.autosuggest_options = [nome for nome in sugestoes_clientes if texto in nome.lower()]
        # Limpa o erro ao digitar
        if cliente_input.error_text:
            cliente_input.error_text = None
            cliente_input.border_color = None
        page.update()

    cliente_input = ft.TextField(
        label="Cliente",
        hint_text="Digite o nome do cliente",
        width=250,
        on_change=sugerir_cliente,
        filled=True,
        fill_color=ft.Colors.GREY_100,
        error_text=None, # Define inicialmente como None
        error_style=ft.TextStyle(color=ft.Colors.RED_400, size=12)
    )

    def get_cliente_id(nome):
        """
        Retorna o ID do cliente dado o nome.
        Se não encontrar, retorna None.
        """
        for cliente in clientes:
            if cliente["nome"].lower() == nome.strip().lower():
                return cliente["id"]
        return None
    
    def get_funcionario_id(nome):
        """
        Retorna o ID do funcionário dado o nome.
        Se não encontrar, retorna None.
        """
        for funcionario in funcionarios:
            if funcionario["nome"].lower() == nome.strip().lower():
                return funcionario["id"]
        return None

    def on_vendedor_change(e):
        # Limpa o erro ao selecionar um valor
        if vendedor_dropdown.error_text:
            vendedor_dropdown.error_text = None
            vendedor_dropdown.border_color = None
        page.update()

    vendedor_dropdown = ft.Dropdown(
        label="Vendedor Responsável",
        options=[ft.dropdown.Option(f["nome"]) for f in db_vendas.listar_funcionarios()],
        width=250,
        filled=True,
        fill_color=ft.Colors.GREY_100,
        on_change=on_vendedor_change,
        error_text=None, # Define inicialmente como None
        error_style=ft.TextStyle(color=ft.Colors.RED_400, size=12)
    )

    status_dropdown = ft.Dropdown(
        label="Status da Venda",
        options=[
            ft.dropdown.Option("Concluída"),
            ft.dropdown.Option("Pendente"),
            ft.dropdown.Option("Cancelada")
        ],
        width=250,
        filled=True,
        fill_color=ft.Colors.GREY_100,
        value="Pendente"
    )

    # Adiciona error_text e error_style para produto_input
    produto_input = ft.TextField(
        label="Produto (nome ou ID)",
        width=250,
        on_change=lambda e: (buscar_produto(e), setattr(e.control, 'error_text', None), setattr(e.control, 'border_color', None), page.update()),
        filled=True,
        fill_color=ft.Colors.GREY_100,
        error_text=None,
        error_style=ft.TextStyle(color=ft.Colors.RED_400, size=12)
    )
    quantidade_valor = ft.TextField(
        label="Quantidade",
        value="1",
        width=110,
        text_align=ft.TextAlign.CENTER,
        filled=True,
        fill_color=ft.Colors.GREY_100,
        error_text=None, # Pode ser útil para validação de quantidade mínima
        error_style=ft.TextStyle(color=ft.Colors.RED_400, size=16)
    )
    preco_unitario = ft.TextField(label="Preço Unitário", read_only=True, width=150, filled=True, fill_color=ft.Colors.GREY_100)

    desconto_global = ft.TextField(
        label="Desconto (R$)",
        value="0.00",
        width=150,
        filled=True,
        fill_color=ft.Colors.GREY_100,
        on_change=lambda e: (atualizar_valores(), setattr(e.control, 'error_text', None), setattr(e.control, 'border_color', None), page.update()),
        error_text=None,
        error_style=ft.TextStyle(color=ft.Colors.RED_400, size=12)
    )
    subtotal_text = ft.Text("Subtotal: R$ 0,00", size=16, color=ft.Colors.WHITE)
    total_text = ft.Text("TOTAL: R$ 0,00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    def atualizar_quantidade(delta):
        atual = int(quantidade_valor.value or 0)
        nova = max(atual + delta, 0)
        quantidade_valor.value = str(nova)
        # Limpa o erro ao ajustar a quantidade
        if quantidade_valor.error_text:
            quantidade_valor.error_text = None
            quantidade_valor.border_color = None
        page.update()

    quantidade_input = ft.Row([
        ft.IconButton(icon=ft.Icons.REMOVE, icon_color=ft.Colors.WHITE, on_click=lambda e: atualizar_quantidade(-1)),
        quantidade_valor,
        ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.WHITE, on_click=lambda e: atualizar_quantidade(1)),
    ], alignment=ft.MainAxisAlignment.START)

    def buscar_produto(e):
        nome_ou_id = produto_input.value.lower()
        p = next((p for p in produtos if nome_ou_id in p["nome"].lower() or nome_ou_id == str(p["id"])), None)
        preco_unitario.value = f"{p['preco']:.2f}" if p else ""
        if not p and nome_ou_id: # Se não encontrou o produto e o campo não está vazio
            produto_input.error_text = "Produto não encontrado."
            produto_input.border_color = ft.Colors.RED_400
        elif p and nome_ou_id and p['estoque_atual'] <= 0:
            produto_input.error_text = f"Produto fora de estoque ({p['estoque_atual']} unidades disponíveis)."
            produto_input.border_color = ft.Colors.RED_400
        else:
            produto_input.error_text = None
            produto_input.border_color = None
            #produto_input.value = p["nome"] if p else ""
        page.update()

    tabela_itens = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Qtde")),
            ft.DataColumn(ft.Text("Desconto")),
            ft.DataColumn(ft.Text("Valor Unit.")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Ações")),
        ],
        rows=[]
    )

    def atualizar_lista_itens():
        tabela_itens.rows.clear()
        for i, item in enumerate(venda_atual):
            tabela_itens.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item["produto_id"]))),
                        ft.DataCell(ft.Text(item["nome"])),
                        ft.DataCell(ft.Text(str(item["quantidade"]))),
                        ft.DataCell(ft.Text(f"R$ {item['desconto']:.2f}".replace(",", "X").replace(".", ",").replace("X", "."))), # Formato BR
                        ft.DataCell(ft.Text(f"R$ {item['preco_unitario']:.2f}".replace(",", "X").replace(".", ",").replace("X", "."))), # Formato BR
                        ft.DataCell(ft.Text(f"R$ {item['subtotal']:.2f}".replace(",", "X").replace(".", ",").replace("X", "."))), # Formato BR
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, index=i: remover_produto(index)
                            )
                        )
                    ]
                )
            )
        atualizar_valores()
        page.update()

    def remover_produto(index):
        venda_atual.pop(index)
        atualizar_lista_itens()

    def adicionar_produto(e):
        nome_ou_id = produto_input.value.lower()
        qtd_str = quantidade_valor.value
        
        # Validação de campo de produto e quantidade
        produto_encontrado = next((p for p in produtos if nome_ou_id in p["nome"].lower() or nome_ou_id == str(p["id"])), None)
        
        has_error = False

        # Limpa erros anteriores
        if not produto_encontrado:
            produto_input.error_text = "Produto não encontrado ou campo vazio."
            produto_input.border_color = ft.Colors.RED_400
            has_error = True
        else:
            produto_input.error_text = None
            produto_input.border_color = None

        # Validação de quantidade
        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                quantidade_valor.error_text = "Quantidade deve ser maior que zero."
                quantidade_valor.border_color = ft.Colors.RED_400
                has_error = True
            else:
                quantidade_valor.error_text = None
                quantidade_valor.border_color = None
        except ValueError:
            quantidade_valor.error_text = "Quantidade inválida."
            quantidade_valor.border_color = ft.Colors.RED_400
            has_error = True
        
        if produto_encontrado['estoque_atual'] < qtd:
            produto_input.error_text = f"Quantidade solicitada ({qtd}) maior que o estoque disponível ({produto_encontrado['estoque']})."
            produto_input.border_color = ft.Colors.RED_400
            has_error = True

        page.update() # Atualiza para mostrar os erros

        if has_error:
            return
    

        # Se tudo estiver ok, adiciona o produto
        subtotal = float(produto_encontrado["preco"]) * qtd
        venda_atual.append({
            "produto_id": produto_encontrado["id"],
            "nome": produto_encontrado["nome"],
            "quantidade": qtd,
            "preco_unitario": float(produto_encontrado["preco"]),
            "desconto": 0.0,
            "subtotal": subtotal
        })
        produto_input.value = ""
        quantidade_valor.value = "1"
        preco_unitario.value = ""
        atualizar_lista_itens()

    def atualizar_valores():
        try:
            subtotal = sum(item["subtotal"] for item in venda_atual)
            desconto = float(desconto_global.value.replace(",", ".")) # Converte para float corretamente
            desconto_global.error_text = None
            desconto_global.border_color = None
        except ValueError:
            desconto = 0.0
            desconto_global.error_text = "Desconto inválido."
            desconto_global.border_color = ft.Colors.RED_400
            page.update()
            return # Sai da função se houver erro no desconto

        total = max(subtotal - desconto, 0)
        subtotal_text.value = f"Subtotal: R$ {subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") # Formato BR
        total_text.value = f"TOTAL: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") # Formato BR
        page.update()

    hora_atual = ft.Text("", color=ft.Colors.WHITE)
    def atualizar_hora():
        hora_atual.value = f"Hoje: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        page.update()

    async def atualiza_tempo():
        while True:
            atualizar_hora()
            await asyncio.sleep(1)

    logo = ft.Image(src="seven.png", width=50, height=50, fit=ft.ImageFit.CONTAIN)

    appbar = ft.AppBar(
        title=ft.Container(
            height=100,
            content=ft.Row([
                ft.Container(logo, margin=ft.margin.only(left=14)),
                nome_empresa,
            ], alignment=ft.MainAxisAlignment.START),
        ),
        actions=[
            hora_atual,
            ft.Container( # Container para o botão de fechar com fundo vermelho
                content=ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.WHITE,
                    on_click=vaiPraVendas
                ),
                bgcolor=ft.Colors.RED,
                border_radius=5, # Borda arredondada
                padding=ft.padding.all(5) # Espaçamento interno
            )
        ],
        bgcolor=ft.Colors.BLUE_500,
        automatically_imply_leading=False
    )

    def resetar_campos():
        global venda_id, venda_atual
        venda_id = None
        venda_atual.clear()
        cliente_input.value = ""
        vendedor_dropdown.value = None
        desconto_global.value = "0.00"
        status_dropdown.value = "Pendente"
        produto_input.value = ""
        quantidade_valor.value = "1"
        preco_unitario.value = ""
        globals.venda_em_edicao = None
        atualizar_lista_itens()
        

    def salvar_venda(e):
        global venda_id
        
        # Limpa erros anteriores
        cliente_input.error_text = None
        cliente_input.border_color = None
        vendedor_dropdown.error_text = None
        vendedor_dropdown.border_color = None
        desconto_global.error_text = None
        desconto_global.border_color = None

        has_error = False

        # Verifica se o cliente foi preenchido e existe
        if not cliente_input.value:
            cliente_input.error_text = "Campo 'Cliente' é obrigatório."
            cliente_input.border_color = ft.Colors.RED_400
            has_error = True
        else:
            # Verifica se o cliente existe
            cliente_id = get_cliente_id(cliente_input.value)
            if cliente_id is None:
                cliente_input.error_text = "Cliente não encontrado. Selecione um cliente válido."
                cliente_input.border_color = ft.Colors.RED_400
                has_error = True

        # Verifica se o vendedor foi selecionado e existe
        if not vendedor_dropdown.value:
            vendedor_dropdown.error_text = "Campo 'Vendedor Responsável' é obrigatório."
            vendedor_dropdown.border_color = ft.Colors.RED_400
            has_error = True
        else:
            # Verifica se o funcionário existe
            funcionario_id = get_funcionario_id(vendedor_dropdown.value)
            if funcionario_id is None:
                vendedor_dropdown.error_text = "Funcionário não encontrado. Selecione um vendedor válido."
                vendedor_dropdown.border_color = ft.Colors.RED_400
                has_error = True

        # Verifica se há produtos na venda
        if not venda_atual:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Adicione pelo menos um produto à venda!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700
            )
            page.snack_bar.open = True
            has_error = True
        
        # Validação do desconto
        try:
            desconto = float(desconto_global.value.replace(",", "."))
            if desconto < 0:
                desconto_global.error_text = "Desconto não pode ser negativo."
                desconto_global.border_color = ft.Colors.RED_400
                has_error = True
        except ValueError:
            desconto_global.error_text = "Valor de desconto inválido."
            desconto_global.border_color = ft.Colors.RED_400
            has_error = True
            desconto = 0.0  # Define um valor padrão

        page.update()  # Atualiza para mostrar os erros nos campos

        if has_error:
            return

        # Cálculo dos valores
        status = status_dropdown.value
        subtotal = sum(item["subtotal"] for item in venda_atual)
        total = max(subtotal - desconto, 0)

        # Ajusta o total baseado no status
        if status == "Cancelada":
            total = 0.0            
        elif status == "Pendente":
            pass

        # Prepara os dados da venda
        venda_data = {
            "cliente_id": int(get_cliente_id(cliente_input.value)),
            "funcionario_id": int(get_funcionario_id(vendedor_dropdown.value)),
            "desconto": desconto,
            "status": status,
            "total": total,
            "data_venda": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "itens": [{
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
                "desconto": item["desconto"],
                "subtotal": item["subtotal"]
            } for item in venda_atual]
        }

        try:
            if globals.venda_em_edicao is not None:  # Modo edição
            # Primeiro remove os itens antigos
                if db_vendas.remover_itens_venda(globals.venda_em_edicao):
                    # Depois atualiza a venda e adiciona os novos itens
                    if db_vendas.atualizar_venda(globals.venda_em_edicao, venda_data) and \
                    db_vendas.atualizar_itens_venda(globals.venda_em_edicao, venda_data["itens"]):
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Venda {globals.venda_em_edicao} atualizada com sucesso!", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.GREEN_700
                        )
                        venda_id = globals.venda_em_edicao  # Mantém o ID da venda editada
                        vaiPraVendas(e)
                    else:
                        raise Exception("Erro ao atualizar venda no banco de dados")
                else:
                    raise Exception("Erro ao remover itens antigos da venda")
            else:  # Nova venda
                # Cadastra nova venda
                novo_venda_id = db_vendas.cadastrar_venda(venda_data)
                if novo_venda_id:
                    venda_id = novo_venda_id
                    page.open = ft.SnackBar(
                        content=ft.Text(f"Venda {venda_id} salva com sucesso!", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN_700
                    )
                    globals.venda_em_edicao = None  # Reseta a variável global
                    vaiPraVendas(e)  # Redireciona para a tela de vendas
                else:
                    raise Exception("Erro ao cadastrar venda no banco de dados")
            
            page.snack_bar.open = True
            page.update()
            
            # Comportamento pós-salvamento
            if globals.venda_em_edicao is None:
                resetar_campos()
            else:
                pass

        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro ao salvar venda: {str(ex)}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700
            )
            page.snack_bar.open = True
            page.update()


    # Inicia a tarefa do relógio apenas uma vez por View
    if not _clock_task or _clock_task.done():
        _clock_task = page.run_task(atualiza_tempo)
        print("Tarefa atualiza_tempo iniciada (cadastro_vendas).")

    if globals.venda_em_edicao is not None:
        # Busca a venda do banco de dados
        venda_edit = db_vendas.buscar_venda_por_id(globals.venda_em_edicao)
        if venda_edit:
            # Preenche os campos com os dados da venda
            cliente_input.value = venda_edit['cliente_nome']
            vendedor_dropdown.value = venda_edit['funcionario_nome']
            status_dropdown.value = venda_edit['status']
            desconto_global.value = str(venda_edit['desconto'])
            
            # Preenche os itens da venda
            venda_atual.clear()
            for item in venda_edit['itens']:
                venda_atual.append({
                    "produto_id": item['produto_id'],
                    "nome": item['produto_nome'],
                    "quantidade": item['quantidade'],
                    "preco_unitario": item['preco_unitario'],
                    "desconto": item['desconto'],
                    "subtotal": item['subtotal']
                })
            atualizar_lista_itens()
            
            # Define o venda_id global para edição
            venda_id = globals.venda_em_edicao

    return ft.View(
        route="/cadastro_vendas",
        appbar=appbar,
        bgcolor='#1565c0',
        controls=[
            ft.Column([ # Coluna principal para conter os dois Rows
                ft.Row([
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Container(
                            padding=20,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=10,
                            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12, spread_radius=1),
                            content=ft.Column([
                                ft.Text("Itens da Venda", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                tabela_itens
                            ], spacing=10, expand=True) # Adiciona expand=True para a coluna da tabela
                        )
                    ),
                    ft.Container(
                        width=300,
                        bgcolor=ft.Colors.BLUE_500,
                        padding=15,
                        content=ft.Column([
                            ft.Text("CAIXA LIVRE - VENDA", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            vendedor_dropdown,
                            cliente_input,
                            produto_input,
                            quantidade_input,
                            preco_unitario,
                            ft.ElevatedButton("Adicionar Produto", icon=ft.Icons.ADD, on_click=adicionar_produto),
                            status_dropdown,
                            ft.Container(expand=True) # Para empurrar os elementos para cima
                        ], scroll=ft.ScrollMode.AUTO) # Adiciona scroll ao painel lateral
                    )
                ], expand=True), # O Row principal deve expandir

                # Bloco de Totais
                ft.Container(
                    bgcolor=ft.Colors.BLUE_400,
                    padding=30,
                    content=ft.Row([
                        ft.Column([subtotal_text, desconto_global, total_text]),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "SALVAR VENDA",
                            icon=ft.Icons.SAVE,
                            color=ft.Colors.WHITE,
                            icon_color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREEN_500,
                                padding=20
                            ),
                            scale=1.2,
                            on_click=salvar_venda
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    # Para alinhar na parte inferior da tela
                    alignment=ft.alignment.bottom_center,
                    width=page.width, # Garante que o Container de totais ocupe a largura total
                )
            ], expand=True) # Coluna principal deve expandir
        ],
        scroll=ft.ScrollMode.AUTO, # Mude para AUTO para permitir rolagem se o conteúdo exceder
        vertical_alignment=ft.MainAxisAlignment.START
    )