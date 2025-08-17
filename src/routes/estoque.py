import flet as ft
from datetime import datetime
from database.estoque_controller import EstoqueController


def View(page: ft.Page):
    db_estoque = EstoqueController(page.client_storage.get("user_db"))
    movimentacoes = []
    movimentacao_para_excluir = {"index": None}
    movimentacao_em_edicao = {"index": None}

    #produtos_dados = db_estoque.listar_id_e_produtos()
    #produtos = [f['nome'] for f in produtos_dados]
    funcionarios_dados = db_estoque.listar_id_e_funcionarios()
    funcionarios = [f['nome'] for f in funcionarios_dados]
    

    id_field = ft.TextField(label="ID", read_only=True, width=120)

    def voltar_home(e):
        page.go("/home")

    def criar_linha_tabela(i, p):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(p["id"]))),
                ft.DataCell(ft.Text(p.get("produto_nome", p['produto_id']))),  # Mostrar nome em vez de ID
                ft.DataCell(ft.Text(p["tipo_movimentacao"], color={
                    "ENTRADA": ft.Colors.GREEN,
                    "SAIDA": ft.Colors.RED,
                    "AJUSTE": ft.Colors.ORANGE,
                    "PERDA": ft.Colors.PURPLE,
                    "DEVOLUCAO": ft.Colors.BLUE
                }.get(p["tipo_movimentacao"], ft.Colors.BLACK))),
                ft.DataCell(ft.Text(str(p["quantidade"]))),
                ft.DataCell(ft.Text(str(p["estoque_anterior"]))),
                ft.DataCell(ft.Text(str(p["estoque_atual"]))),
                ft.DataCell(ft.Text(p["motivo"] or "")),
                ft.DataCell(ft.Text(str(p["referencia_id"]) if p["referencia_id"] else "")),
                ft.DataCell(ft.Text(p["referencia_tipo"] or "")),
                ft.DataCell(ft.Text(p.get("funcionario_nome", "") or "Sistema")),  # Mostrar nome do funcionário
                ft.DataCell(ft.Text(p["data_movimentacao"])),
                ft.DataCell(ft.Text(p["observacoes"] or "")),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Editar movimentacao",
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, idx=i: editar_movimentacao(idx)(e)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Excluir movimentacao",
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, idx=i: excluir_movimentacao(idx)(e)
                        ),
                    ], spacing=5)
                ),
            ]
        )

    def atualizar_lista():
        tabela.rows.clear()
        movimentacoes.clear()
        movimentacoes.extend(db_estoque.listar_movimentacoes())
        for i, p in enumerate(movimentacoes):
            tabela.rows.append(criar_linha_tabela(i, p))
        page.update()

    def editar_movimentacao(index):
        def handler(e):
            movimentacao_em_edicao["index"] = index
            movimentacao = movimentacoes[index]
            id_field.value = movimentacao["id"]
            tipo_movimentacao_field.value = movimentacao["tipo_movimentacao"]
            quantidade_field.value = str(movimentacao["quantidade"])
            estoque_anterior_field.value = str(movimentacao["estoque_anterior"])
            estoque_atual_field.value = str(movimentacao["estoque_atual"])
            motivo_field.value = movimentacao["motivo"] or ""
            referencia_id_field.value = str(movimentacao["referencia_id"]) if movimentacao["referencia_id"] else ""
            observacoes_field.value = movimentacao["observacoes"] or ""

            #produto_nome = None
            #if 'produto_nome' in movimentacao and movimentacao['produto_nome']:
            #    produto_nome = movimentacao['produto_nome']
            #elif 'produto_id' in movimentacao and movimentacao['produto_id']:
            #    produtos_dados = db_estoque.listar_id_e_produtos()
            #    for produto in produtos_dados:
            #        if produto['id'] == movimentacao['produto_id']:
            #            produto_nome = produto['nome']
            #            break
            
            #produto_field.value = produto_nome if produto_nome else f'Id: {movimentacao["produto_id"]}'
            produto_field.value = movimentacao["produto_id"]

            funcionario_nome = None
            if 'funcionario_nome' in movimentacao and movimentacao['funcionario_nome']:
                funcionario_nome = movimentacao['funcionario_nome']
            elif 'funcionario_id' in movimentacao and movimentacao['funcionario_id']:
                funcionarios_dados = db_estoque.listar_id_e_funcionarios()
                for funcionario in funcionarios_dados:
                    if funcionario['id'] == movimentacao['funcionario_id']:
                        funcionario_nome = funcionario['nome']
                        break
            
            funcionario_field.value = funcionario_nome if funcionario_nome else f'Id: {movimentacao["funcionario_id"]}'

            dialog.open = True
            page.update()
        return handler

    def excluir_movimentacao(index):
        def handler(e):
            movimentacao_para_excluir["index"] = index
            confirm_dialog.open = True
            page.update()
        return handler

    def confirmar_exclusao(e):
        index = movimentacao_para_excluir["index"]
        if index is not None:
            movimentacao_id = movimentacoes[index]["id"]
            if db_estoque.excluir_movimentacao(movimentacao_id):
                movimentacoes.pop(index)
                atualizar_lista()
        confirm_dialog.open = False
        page.update()

    def cancelar_exclusao(e):
        confirm_dialog.open = False
        page.update()

    #def limpar_campos():
    #    id_field.value = ""
    #    produto_field.value = ""
    #    tipo_movimentacao_field.value = ""
    #    quantidade_field.value = ""
    #    estoque_anterior_field.value = ""
    #    estoque_atual_field.value = ""
    #    motivo_field.value = ""
    #    referencia_id_field.value = ""
    #    referencia_tipo_field.value = ""
    #    funcionario_field.value = ""
    #    observacoes_field.value = ""
    #    movimentacao_em_edicao["index"] = None
    #    # Limpar erros de validação
    #    for field in [produto_field, tipo_movimentacao_field, quantidade_field, 
    #                 estoque_anterior_field, estoque_atual_field]:
    #        field.error_text = None
    #        field.border_color = None

    def nome_para_id_funcionario(nome):
        for f in funcionarios_dados:
            if f["nome"] == nome:
                return f['id']
        return None

    def salvar_movimentacao_click(e):
        # Validação dos campos obrigatórios
        campos_obrigatorios = {
            produto_field: "ID do Produto",
            tipo_movimentacao_field: "Tipo de Movimentação",
            quantidade_field: "Quantidade",
            estoque_anterior_field: "Estoque Anterior",
            estoque_atual_field: "Estoque Atual"
        }
        
        campos_invalidos = False
        for field, nome in campos_obrigatorios.items():
            if not field.value:
                field.error_text = f"* {nome} obrigatório"
                field.border_color = ft.Colors.RED_400
                campos_invalidos = True
        
        if campos_invalidos:
            page.update()
            return

        try:
            nova_movimentacao = {
                "produto_id": int(produto_field.value),
                "tipo_movimentacao": tipo_movimentacao_field.value,
                "quantidade": int(quantidade_field.value),
                "estoque_anterior": int(estoque_anterior_field.value),
                "estoque_atual": int(estoque_atual_field.value),
                "motivo": motivo_field.value or None,
                "referencia_id": int(referencia_id_field.value) if referencia_id_field.value else None,
                "referencia_tipo": referencia_tipo_field.value or None,
                "funcionario_id": int(nome_para_id_funcionario(funcionario_field.value)) if funcionario_field.value else None,
                "observacoes": observacoes_field.value or None
            }
        except ValueError:
            # Tratar erros de conversão numérica
            ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text("Valores numéricos inválidos")).open = True
            page.update()
            return

        if movimentacao_em_edicao["index"] is None:
            movimentacao_id = db_estoque.cadastrar_movimentacao(nova_movimentacao)
            if movimentacao_id:
                nova_movimentacao["id"] = movimentacao_id
                nova_movimentacao["data_movimentacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                movimentacoes.append(nova_movimentacao)
        else:
            index = movimentacao_em_edicao["index"]
            movimentacao_id = movimentacoes[index]["id"]
            if db_estoque.atualizar_movimentacao(movimentacao_id, nova_movimentacao):
                nova_movimentacao["id"] = movimentacao_id
                nova_movimentacao["data_movimentacao"] = movimentacoes[index]["data_movimentacao"]
                movimentacoes[movimentacao_em_edicao["index"]] = nova_movimentacao

        movimentacao_em_edicao["index"] = None
        atualizar_lista()
        dialog.open = False
        page.update()

    # Campos do formulário
    produto_field = ft.TextField(label="* ID do Produto", width=120)
    tipo_movimentacao_field = ft.Dropdown(
        label="* Tipo de Movimentação",
        options=[
            ft.dropdown.Option("ENTRADA"),
            ft.dropdown.Option("SAIDA"),
            ft.dropdown.Option("AJUSTE"),
            ft.dropdown.Option("PERDA"),
            ft.dropdown.Option("DEVOLUCAO")
        ],
        width=150
    )
    quantidade_field = ft.TextField(label="* Quantidade", width=120, input_filter=ft.NumbersOnlyInputFilter())
    estoque_anterior_field = ft.TextField(label="* Estoque Anterior", width=120, input_filter=ft.NumbersOnlyInputFilter())
    estoque_atual_field = ft.TextField(label="* Estoque Atual", width=120, input_filter=ft.NumbersOnlyInputFilter())
    motivo_field = ft.TextField(label="Motivo", width=200)
    referencia_id_field = ft.TextField(label="Referência ID", width=120, input_filter=ft.NumbersOnlyInputFilter())
    referencia_tipo_field = ft.TextField(label="Tipo de Referência", width=150)

    #funcionario_field = ft.TextField(label="ID do Funcionário", width=120, input_filter=ft.NumbersOnlyInputFilter())
    funcionario_field = ft.Dropdown(
        label = "Funcionário",
        options = [ft.dropdown.Option(f) for f in funcionarios],
        width=120
    )

    observacoes_field = ft.TextField(label="Observações", width=300, multiline=True, min_lines=2, max_lines=4)

    salvar_movimentacao = ft.ElevatedButton(
        "Salvar",
        on_click=salvar_movimentacao_click,
        tooltip="Salvar movimentação",
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
        )
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cadastrar/Editar movimentação de estoque"),
        content=ft.Container(
            content=ft.Column([
                ft.Row([id_field, produto_field, tipo_movimentacao_field], spacing=10),
                ft.Row([quantidade_field, estoque_anterior_field, estoque_atual_field], spacing=10),
                ft.Row([motivo_field, referencia_id_field, referencia_tipo_field], spacing=10),
                ft.Row([funcionario_field], spacing=10),
                observacoes_field
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=800,
            height=400,
            padding=10
        ),
        actions=[
            salvar_movimentacao,
            ft.ElevatedButton(
                "Cancelar",
                tooltip="Cancelar operação",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                ),
                on_click=lambda e: (
                    setattr(dialog, 'open', False),
                    page.update()
                )
            ),
        ]
    )
    page.overlay.append(dialog)

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Exclusão"),
        content=ft.Text("Você realmente deseja excluir esta movimentação?"),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_exclusao),
            ft.TextButton("Excluir", on_click=confirmar_exclusao),
        ]
    )
    page.overlay.append(confirm_dialog)

    campo_pesquisa = ft.TextField(
        label="Pesquisar movimentação (por ID, produto ou tipo)",
        visible=True,
        on_change=lambda e: filtrar_movimentacoes(e.control.value),
        prefix_icon=ft.Icons.SEARCH,
        width=500
    )

    def filtrar_movimentacoes(query):
        if not query:
            atualizar_lista()
            return
            
        tabela.rows.clear()
        for i, p in enumerate(movimentacoes):
            if (query.lower() in str(p["id"]).lower() or
                query.lower() in str(p["produto_id"]).lower() or
                query.lower() in p["tipo_movimentacao"].lower()):
                tabela.rows.append(criar_linha_tabela(i, p))
        page.update()

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Produto")),
            ft.DataColumn(ft.Text("Tipo")),
            ft.DataColumn(ft.Text("Quantidade")),
            ft.DataColumn(ft.Text("Est. Anterior")),
            ft.DataColumn(ft.Text("Est. Atual")),
            ft.DataColumn(ft.Text("Motivo")),
            ft.DataColumn(ft.Text("Ref. ID")),
            ft.DataColumn(ft.Text("Ref. Tipo")),
            ft.DataColumn(ft.Text("Funcionário")),
            ft.DataColumn(ft.Text("Data Mov.")),
            ft.DataColumn(ft.Text("Observações")),
            ft.DataColumn(ft.Text("Ações")),
        ],
        rows=[]
    )

    atualizar_lista()

    '''def abrir_dialogo_cadastro(e):
        movimentacao_em_edicao["index"] = None
        limpar_campos()
        dialog.open = True
        page.update()'''

    return ft.View(
        route="/movimentacoes",
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(name=ft.Icons.INVENTORY, color=ft.Colors.WHITE),
                ft.Text("Movimentações de Estoque", color=ft.Colors.WHITE),
            ], spacing=10),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Voltar", icon_color=ft.Colors.WHITE, on_click=voltar_home),
            bgcolor=ft.Colors.TEAL
        ),
        controls=[
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            campo_pesquisa, ft.Divider(),
                            tabela
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True
                    )
                    #ft.Container(
                    #    content=ft.FloatingActionButton(
                    #        text="Cadastrar",
                    #        icon=ft.Icons.ADD,
                    #        on_click=abrir_dialogo_cadastro,
                    #        bgcolor=ft.Colors.TEAL,
                    #        foreground_color=ft.Colors.WHITE
                    #    ),
                    #    left=20,
                    #    bottom=20,
                    #    alignment=ft.alignment.bottom_left
                    #)
                ],
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START
    )