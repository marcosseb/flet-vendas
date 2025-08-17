import flet as ft
import datetime
from database.produtos_controller import ProdutosController

def View(page: ft.Page):
    produtos = []
    db_produtos = ProdutosController(page.client_storage.get("user_db"))
    produto_para_excluir = {"index": None}
    produto_para_edicao = {"index": None}
    
    fornecedores_dados = db_produtos.listar_id_e_fornecedores()
    fornecedores = [f['nome_fantasia'] for f in fornecedores_dados]

    id_field = ft.TextField(label="ID", read_only=True, width=120)

    def voltar_home(e):
        page.go("/home")

    def criar_linha_tabela(i, p):
        preco_display = f"R$ {p['preco']}"
        if p.get('preco_promocional'):
            preco_display = f"R$ {p['preco_promocional']} (Promo)"

        descricao_text = ft.Text(
            p["descricao"],
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
            size=12,
            text_align=ft.TextAlign.JUSTIFY
        )

        return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(p["id"]))),
                    ft.DataCell(ft.Text(p["nome"])),
                    ft.DataCell(ft.Text(preco_display)),
                    ft.DataCell(ft.Text(str(p["estoque_atual"]))),  # Alterado de 'estoque' para 'estoque_atual'
                    ft.DataCell(ft.Text(str(p.get("estoque_minimo", 0)))),  # Novo campo
                    ft.DataCell(ft.Text(str(p.get("estoque_maximo", "-")) if p.get("estoque_maximo") is not None else "-")),  # Novo campo
                    ft.DataCell(ft.Text(p["categoria"])),
                    ft.DataCell(ft.Text(p.get("fornecedor", "N/A"))),  # Fornecedor pode ser None
                    ft.DataCell(ft.Text(f"R$ {p['custo_unitario']}")),
                    ft.DataCell(ft.Text(p["data_cadastro"])),
                    ft.DataCell(descricao_text),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Clique aqui para editar produto",
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, idx=i: editar_produto(idx)(e)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Clique aqui para excluir produto",
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, idx=i: excluir_produto(idx)(e)
                            ),
                        ], spacing=5)
                    ),
                ]
            )

    def atualizar_lista():
        tabela.rows.clear()
        produtos.clear()
        produtos.extend(db_produtos.listar_produtos())

        tabela.rows.clear()
        for i, p in enumerate(produtos):
            tabela.rows.append(criar_linha_tabela(i, p))
        page.update()

    def editar_produto(index):
        def handler(e):
            produto_para_edicao["index"] = index
            p = produtos[index]

            print(f"Produto para edição: {p}")
            print(f"Chaves disponíveis: {list(p.keys())}")
            
            # Campos simples
            id_field.value = str(p["id"])
            nome_field.value = p["nome"]
            descricao_field.value = p["descricao"]
            preco_field.value = str(p["preco"])
            preco_promocional_field.value = str(p.get("preco_promocional") or "")
            custo_field.value = str(p["custo_unitario"])
            estoque_field.value = str(p["estoque_atual"])  # Alterado para estoque_atual
            estoque_minimo_field.value = str(p.get("estoque_minimo", 0))  # Novo campo
            estoque_maximo_field.value = str(p.get("estoque_maximo", "")) if p.get("estoque_maximo") is not None else ""  # Novo campo
            categoria_dropdown.value = p["categoria"]
            data_field.value = p["data_cadastro"]
            
            # Fornecedor - lógica robusta que funciona com qualquer implementação
            fornecedor_nome = None
            if "fornecedor" in p and p["fornecedor"]:
                # Se já temos o nome do fornecedor (JOIN implementado)
                fornecedor_nome = p["fornecedor"]
            elif "fornecedor_id" in p and p["fornecedor_id"]:
                # Se temos apenas o ID, converter para nome
                fornecedores_dados = db_produtos.listar_id_e_fornecedores()
                for f in fornecedores_dados:
                    if f["id"] == p["fornecedor_id"]:
                        fornecedor_nome = f["nome_fantasia"]
                        break
            
            fornecedor_dropdown.value = fornecedor_nome
            
            dialog.open = True
            page.update()
        return handler

    def excluir_produto(index):
        def handler(e):
            produto_para_excluir["index"] = index
            confirm_dialog.open = True
            page.update()
        return handler

    def confirmar_exclusao(e):
        index = produto_para_excluir["index"]
        if index is not None:
            try:
                produto_id = produtos[index]["id"]
                if db_produtos.excluir_produto(produto_id):
                    produtos.pop(index)
                    atualizar_lista()
                    page.open(
                        ft.SnackBar(
                            content=ft.Text("Produto excluído com sucesso!"),
                            bgcolor=ft.Colors.GREEN
                        )
                    )
                else:
                    raise Exception("Erro ao excluir produto")
            except Exception as e:
                print(f"Erro ao excluir produto: {e}")
                page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Erro ao excluir produto. {str(e)}"),
                        bgcolor=ft.Colors.RED
                    )
                )
        confirm_dialog.open = False
        page.update()

    def cancelar_exclusao(e):
        confirm_dialog.open = False
        page.update()

    def abrir_calendario(e):
        calendario.open = True
        page.update()

    def limpar_campos():
        id_field.value = str(max([p["id"] for p in produtos], default=0) + 1)
        nome_field.value = ""
        descricao_field.value = ""
        preco_field.value = ""
        preco_promocional_field.value = ""
        custo_field.value = ""
        estoque_field.value = ""
        fornecedor_dropdown.value = None
        categoria_dropdown.value = None
        data_field.value = datetime.date.today().strftime("%d/%m/%Y")
        produto_para_edicao["index"] = None
        for f in [nome_field, preco_field, custo_field, estoque_field, categoria_dropdown]:
            f.error_text = None

    def nome_para_id_fornecedor(nome):
        """
        Converte o nome do fornecedor para o ID correspondente.
        Se o nome não for encontrado, retorna None.
        """
        for f in fornecedores_dados:
            if f["nome_fantasia"] == nome:
                return f["id"]
        return None

    def salvar_produto_click(e):
            campos_obrigatorios = [
                (nome_field, "Nome"),
                (preco_field, "Preço", float), # Adiciona o tipo esperado para validação
                (custo_field, "Custo Unitário", float),
                (estoque_field, "Estoque", int),
                (categoria_dropdown, "Categoria"),
                (estoque_minimo_field, "Estoque Mínimo", int),
            ]

            faltando = False
            valores_convertidos = {}

            for campo, nome, *tipo_esperado in campos_obrigatorios:
                if not campo.value:
                    campo.error_text = f"* {nome} obrigatório"
                    campo.border_color = ft.Colors.RED_400
                    faltando = True
                else:
                    campo.error_text = None
                    campo.border_color = None
                    if tipo_esperado: # Se houver tipo esperado (float, int)
                        try:
                            valores_convertidos[nome] = tipo_esperado[0](campo.value)
                        except ValueError:
                            campo.error_text = "* Valor inválido"
                            campo.border_color = ft.Colors.RED_400
                            faltando = True
                    else:
                        valores_convertidos[nome] = campo.value
            
            # Validação do preço promocional (campo opcional)
            preco_promocional_float = None
            if preco_promocional_field.value:
                try:
                    preco_promocional_float = float(preco_promocional_field.value)
                    preco_promocional_field.error_text = None
                    preco_promocional_field.border_color = None
                except ValueError:
                    preco_promocional_field.error_text = "* Valor inválido"
                    preco_promocional_field.border_color = ft.Colors.RED_400
                    faltando = True
            else:
                preco_promocional_field.error_text = None
                preco_promocional_field.border_color = None

            page.update()

            if faltando:
                return

            estoque_maximo_int = None
            if estoque_maximo_field.value:
                try:
                    estoque_maximo_int = int(estoque_maximo_field.value)
                    if estoque_maximo_int < int(estoque_minimo_field.value):
                        raise ValueError("Estoque máximo não pode ser menor que o mínimo")
                    estoque_maximo_field.error_text = None
                    estoque_maximo_field.border_color = None
                except ValueError as e:
                    estoque_maximo_field.error_text = f"* {str(e)}"
                    estoque_maximo_field.border_color = ft.Colors.RED_400
                    faltando = True

            novo_produto = {
                "nome": valores_convertidos["Nome"],
                "descricao": descricao_field.value,
                "preco": valores_convertidos["Preço"],
                "preco_promocional": preco_promocional_float,
                "custo_unitario": valores_convertidos["Custo Unitário"],
                "estoque_atual": valores_convertidos["Estoque"],
                "estoque_minimo": valores_convertidos["Estoque Mínimo"],
                "estoque_maximo": estoque_maximo_int,
                "fornecedor_id": int(nome_para_id_fornecedor(fornecedor_dropdown.value)),
                "categoria": categoria_dropdown.value,
                "data_cadastro": data_field.value
            }

            print(novo_produto)

            try:
                if produto_para_edicao["index"] is None:
                    # CADASTRO NOVO
                    produto_id = db_produtos.cadastrar_produto(novo_produto)
                    if produto_id is not None:
                        novo_produto["id"] = produto_id
                        produtos.append(novo_produto)
                        page.open(
                            ft.SnackBar(
                                content=ft.Text("Produto cadastrado com sucesso!"),
                                bgcolor=ft.Colors.GREEN
                            )
                        )
                    else:
                        raise Exception("Erro ao cadastrar produto")
                else:
                    # EDIÇÃO
                    index = produto_para_edicao["index"]
                    produto_id = produtos[index]["id"]

                    if db_produtos.atualizar_produto(produto_id, novo_produto):
                        novo_produto["id"] = produto_id
                        produtos[index] = novo_produto
                        page.open(
                            ft.SnackBar(
                                content=ft.Text("Produto atualizado com sucesso!"),
                                bgcolor=ft.Colors.GREEN
                            )
                        )
                    else:
                        raise Exception("Erro ao atualizar produto")


                atualizar_lista()
                dialog.open = False
                page.update()
            except Exception as e:
                print(f"Erro ao salvar produto: {e}")
                page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Erro ao salvar produto. {str(e)}"),
                        bgcolor=ft.Colors.RED
                    )
                )
                page.update()

    salvar_produto = ft.ElevatedButton(
        "Salvar",
        on_click=salvar_produto_click,
        tooltip="Clique aqui para salvar este produto",
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
        )
    )

    nome_field = ft.TextField(label="* Nome", width=180)
    descricao_field = ft.TextField(label="Descrição", width=300)
    preco_field = ft.TextField(label="* Preço", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    preco_promocional_field = ft.TextField(label="Preço Promocional", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    custo_field = ft.TextField(label="* Custo Unitário", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    estoque_field = ft.TextField(label="* Estoque", keyboard_type=ft.KeyboardType.NUMBER, width=300)

    estoque_minimo_field = ft.TextField(
        label="Estoque Mínimo", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        width=300,
        value="0"
    )

    estoque_maximo_field = ft.TextField(
        label="Estoque Máximo (opcional)", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        width=300
    )

    fornecedor_dropdown = ft.Dropdown(
        label="Fornecedor",
        options=[ft.dropdown.Option(f) for f in fornecedores],
        width=300
    )

    categoria_dropdown = ft.Dropdown(
        label="* Categoria",
        options=[ft.dropdown.Option(c) for c in [
            "Alimentos", "Bebidas", "Limpeza", "Higiene",
            "Eletrônicos", "Vestuário", "Papelaria", "Outros"
        ]],
        width=300
    )

    data_field = ft.TextField(
        label="Data de Cadastro",
        value=datetime.date.today().strftime("%d/%m/%Y"),
        read_only=True,
        suffix=ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=abrir_calendario),
        width=300
    )

    def on_data_picker_change(e):
        data_field.value = e.control.value.strftime("%d/%m/%Y")
        page.update()

    calendario = ft.DatePicker(on_change=on_data_picker_change)
    page.overlay.append(calendario)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cadastrar/Editar Produto"),
        content=ft.Container(
            content=ft.Column([
                ft.Row([id_field, nome_field], spacing=10),
                descricao_field,
                preco_field,
                preco_promocional_field,
                custo_field,
                estoque_field,
                fornecedor_dropdown,
                categoria_dropdown,
                data_field
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=350,
            height=520,
            padding=10
        ),
        actions=[
            salvar_produto,
            ft.ElevatedButton(
                "Cancelar",
                tooltip="Clique aqui para cancelar o cadastro",
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                on_click=lambda e: setattr(dialog, 'open', False) or page.update()
            )
        ]
    )
    page.overlay.append(dialog)

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Exclusão"),
        content=ft.Text("Você realmente deseja excluir este produto?"),
        actions=[
            ft.TextButton("Cancelar", tooltip="Clique aqui para cancelar a exclusão", on_click=cancelar_exclusao),
            ft.TextButton("Excluir", tooltip="Clique aqui para excluir este produto", on_click=confirmar_exclusao)
        ]
    )
    page.overlay.append(confirm_dialog)

    campo_pesquisa = ft.TextField(
        label="Pesquisar produto (por nome, categoria, fornecedor ou ID)",
        visible=True,
        on_change=lambda e: filtrar_produtos(e.control.value),
        prefix_icon=ft.Icons.SEARCH,
        width=500
    )

    def filtrar_produtos(query):
        tabela.rows.clear()
        for i, p in enumerate(produtos):
            if (
                query.lower() in p["nome"].lower()
                or query.lower() in p["categoria"].lower()
                or query.lower() in (p["fornecedor"] or "").lower()
                or query == str(p["id"])
            ):
                tabela.rows.append(criar_linha_tabela(i, p))
        page.update()

    # Tabela que lista todos os produtos
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID")),
            ft.DataColumn(label=ft.Text("NOME")),
            ft.DataColumn(label=ft.Text("PREÇO")),
            ft.DataColumn(label=ft.Text("ESTOQUE")),
            ft.DataColumn(label=ft.Text("ESTOQUE MÍN")),
            ft.DataColumn(label=ft.Text("ESTOQUE MÁX")),
            ft.DataColumn(label=ft.Text("CATEGORIA")),
            ft.DataColumn(label=ft.Text("FORNECEDOR")),
            ft.DataColumn(label=ft.Text("CUSTO UNITÁRIO")),
            ft.DataColumn(label=ft.Text("DATA DE CADASTRO")),
            ft.DataColumn(label=ft.Text("DESCRIÇÃO")),
            ft.DataColumn(label=ft.Text("AÇÕES")),
        ],
        rows=[]
    )

    # Atualiza a tabela ao carregar a tela
    atualizar_lista()

    # Função separada para abrir o diálogo de cadastro
    def abrir_dialogo_cadastro(e):
        produto_para_edicao["index"] = None
        limpar_campos()
        dialog.open = True
        page.update()

    # Retorna a visualização final da tela de produtos
    return ft.View(
        route="/produtos",
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(name=ft.Icons.SHOPPING_CART, color=ft.Colors.WHITE),
                ft.Text("Produtos", color=ft.Colors.WHITE),
            ], spacing=10),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Clique aqui para voltar", icon_color=ft.Colors.WHITE, on_click=voltar_home),
            bgcolor=ft.Colors.BLUE_500,
        ),
        controls=[
            ft.Stack(
                controls=[
                    ft.Column(
                        controls=[
                            campo_pesquisa, ft.Divider(),
                            tabela, ft.Divider()
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.FloatingActionButton(
                            text="Cadastrar",
                            icon=ft.Icons.ADD,
                            on_click=abrir_dialogo_cadastro,
                            bgcolor=ft.Colors.BLUE_500,
                            foreground_color=ft.Colors.WHITE
                        ),
                        left=20,
                        bottom=20,
                        alignment=ft.alignment.bottom_left
                    )
                ],
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START
    )
