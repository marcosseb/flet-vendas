#CÓDIGO COMPLETO TESTADO
import flet as ft
from data import fornecedores
import re
from database.fornecedores_controller import FornecedoresController

def View(page: ft.Page):
    db_fornecedores = FornecedoresController(page.client_storage.get("user_db"))

    fornecedor_para_excluir = {"index": None}
    id_field = ft.TextField(label="ID", read_only=True, width=120)

    def voltar_home(e):
        """
        Retorna para a tela de home.

        Args:
            e (flet.Event): O evento que disparou a função.
        """
        page.go("/home")

    def criar_linha_tabela(i, f):
        """
        Cria uma linha da tabela com os dados do fornecedor.

        Args:
            i (int): O índice do fornecedor na lista de fornecedores.
            f (dict): O dicionário com os dados do fornecedor.

        Returns:
            ft.DataRow: A linha da tabela com os dados do fornecedor.
        """
        observacoes_text = ft.Text(
            f["observacoes"],
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
            size=12,
            text_align=ft.TextAlign.JUSTIFY
        )
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(f["id"]))),
                ft.DataCell(ft.Text(f["nome_fantasia"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataCell(ft.Text(f["razao_social"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataCell(ft.Text(f["cnpj"])),
                ft.DataCell(ft.Text(f["telefone"])),
                ft.DataCell(ft.Text(f["email"])),
                ft.DataCell(observacoes_text),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, idx=i: editar_fornecedor(idx)(e)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, idx=i: excluir_fornecedor(idx)(e)
                        ),
                    ], spacing=5)
                ),
            ]
        )

    def atualizar_lista():
        """
        Atualiza a lista de fornecedores na tabela.
        """
        fornecedores.clear()
        fornecedores.extend(db_fornecedores.listar_fornecedores())
        
        tabela.rows.clear()
        for i, f in enumerate(fornecedores):
            tabela.rows.append(criar_linha_tabela(i, f))
        page.update()

    def editar_fornecedor(index):
        
        """
        Edita o fornecedor com base no índice fornecido.

        Args: 
            index (int): O índice do fornecedor na lista de fornecedores.

        Returns:
            function: Uma função que edita o fornecedor com base no índice fornecido.
        """
        def handler(e):
            globals()['fornecedor_em_edicao'] = index
            f = fornecedores[index]
            id_field.value = f["id"]
            nome_fantasia_field.value = f["nome_fantasia"]
            razao_social_field.value = f["razao_social"]
            cnpj_field.value = f["cnpj"]
            telefone_field.value = f["telefone"]
            email_field.value = f["email"]
            observacoes_field.value = f["observacoes"]
            
            dialog.open = True
            page.update()
        return handler

    def excluir_fornecedor(index):
        """
        Exclui o fornecedor com base no índice fornecido.

        Args: 
            index (int): O índice do fornecedor na lista de fornecedores.

        Returns:
            function: Uma função que exclui o fornecedor com base no índice fornecido.
        """
        
        def handler(e):
            fornecedor_para_excluir["index"] = index
            confirm_dialog.open = True
            page.update()
        return handler

    def confirmar_exclusao(e):
        index = fornecedor_para_excluir["index"]
        if index is not None:
            try:
                fornecedor_id = fornecedores[index]["id"]  # Pegar o ID real
                if db_fornecedores.excluir_fornecedor(fornecedor_id):  # Excluir por ID
                    fornecedores.pop(index)  # Só remove da lista se exclusão no BD foi bem-sucedida
                    atualizar_lista()
                    # Mostrar mensagem de sucesso
                    page.open(
                        ft.SnackBar(
                            content=ft.Text("Fornecedor excluído com sucesso!"),
                            bgcolor=ft.Colors.PURPLE_400
                        )
                    )
                else:
                    raise Exception("Falha ao excluir fornecedor do banco de dados")
                    
            except Exception as erro:
                # Tratar erros e mostrar mensagem ao usuário
                print(f"Erro ao excluir fornecedor: {erro}")
                page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Erro ao excluir fornecedor: {str(erro)}"),
                        bgcolor=ft.Colors.RED
                    )
                )
        confirm_dialog.open = False
        page.update()

    def cancelar_exclusao(e):
        confirm_dialog.open = False
        page.update()

    def limpar_campos():
        id_field.value = ""
        nome_fantasia_field.value = ""
        razao_social_field.value = ""
        cnpj_field.value = ""
        telefone_field.value = ""
        email_field.value = ""
        observacoes_field.value = ""
        for f in [nome_fantasia_field, cnpj_field]:
            f.error_text = None
            
    def formatar_cnpj(e):
        numero = ''.join(filter(str.isdigit, cnpj_field.value))
        if len(numero) == 14:
            cnpj_field.value = f"{numero[:2]}.{numero[2:5]}.{numero[5:8]}/{numero[8:12]}-{numero[12:]}"
        page.update()

    def formatar_telefone(e):
        v = re.sub(r"\D", "", telefone_field.value)
        if len(v) == 11:
            telefone_field.value = f"({v[:2]}) {v[2:7]}-{v[7:]}"
        elif len(v) == 10:
            telefone_field.value = f"({v[:2]}) {v[2:6]}-{v[6:]}"
        else:
            telefone_field.value = v
        page.update()

    def salvar_fornecedor_click(e):
        campos_obrigatorios = [
            (nome_fantasia_field, "nome fantasia"),
            (telefone_field, "telefone"),
        ]
        faltando = False
        for campo, nome in campos_obrigatorios:
            if not campo.value:
                campo.error_text = f"* {nome} obrigatório"
                campo.border_color = ft.Colors.RED_400
                faltando = True
            else:
                campo.error_text = None
                campo.border_color = None

        if faltando:
            page.update()
            return

        novo_fornecedor = {
            "nome_fantasia": nome_fantasia_field.value,
            "razao_social": razao_social_field.value,
            "cnpj": cnpj_field.value,
            "telefone": telefone_field.value,
            "email": email_field.value,
            "observacoes": observacoes_field.value,
        }

        try:
            if globals().get('fornecedor_em_edicao') is None:
                # CADASTRO NOVO
                fornecedor_id = db_fornecedores.cadastrar_fornecedor(novo_fornecedor)
                if fornecedor_id:
                    novo_fornecedor["id"] = fornecedor_id
                    fornecedores.append(novo_fornecedor)
                    # Mostrar mensagem de sucesso
                    page.open(
                        ft.SnackBar(
                            content=ft.Text("Fornecedor cadastrado com sucesso!"),
                            bgcolor=ft.Colors.GREEN
                        )
                    )
                else:
                    raise Exception("Falha ao cadastrar fornecedor no banco de dados")
            else:
                # EDIÇÃO
                index = globals()['fornecedor_em_edicao']
                fornecedor_id = fornecedores[index]["id"]
                
                if db_fornecedores.atualizar_fornecedor(fornecedor_id, novo_fornecedor):
                    novo_fornecedor["id"] = fornecedor_id
                    fornecedores[index] = novo_fornecedor
                    # Mostrar mensagem de sucesso
                    page.open(
                        ft.SnackBar(
                            content=ft.Text("Fornecedor atualizado com sucesso!"),
                            bgcolor=ft.Colors.GREEN
                        )
                    )
                else:
                    raise Exception("Falha ao atualizar fornecedor no banco de dados")

            # Se chegou até aqui, operação foi bem-sucedida
            globals()['fornecedor_em_edicao'] = None
            atualizar_lista()
            dialog.open = False
            page.update()
            
        except Exception as erro:
            # Tratar erros e mostrar mensagem ao usuário
            print(f"Erro ao salvar fornecedor: {erro}")
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao salvar fornecedor: {str(erro)}"),
                    bgcolor=ft.Colors.RED
                )
            )
            # Manter o diálogo aberto para o usuário tentar novamente
            page.update()

    salvar_fornecedor = ft.ElevatedButton(
        "Salvar",
        on_click=salvar_fornecedor_click,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
        )
    )

    nome_fantasia_field = ft.TextField(label="* Nome Fantasia", autofocus=True)
    razao_social_field = ft.TextField(label="Razão Social")
    cnpj_field = ft.TextField(label="CNPJ", on_blur=formatar_cnpj)
    telefone_field = ft.TextField(label="Telefone", on_blur=formatar_telefone)
    email_field = ft.TextField(label="E-mail")
    observacoes_field = ft.TextField(label="Observações")

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cadastrar/Editar Fornecedor"),
        content=ft.Container(
            content=ft.Column([
                id_field,
                nome_fantasia_field,
                razao_social_field,
                cnpj_field := ft.TextField(label=" CNPJ", width=300, on_change=formatar_cnpj),
                telefone_field := ft.TextField(label="* Telefone", width=300, on_change=formatar_telefone),
                email_field,
                observacoes_field,
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=350,
            height=520,
            padding=10
        ),
        actions=[
            salvar_fornecedor,
            ft.ElevatedButton(
                "Cancelar",
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
        content=ft.Text("Você realmente deseja excluir este fornecedor?"),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_exclusao),
            ft.TextButton("Excluir", on_click=confirmar_exclusao),
        ]
    )
    page.overlay.append(confirm_dialog)

    campo_pesquisa = ft.TextField(
        label="Pesquisar fornecedor (por nome ou ID)",
        visible=True,
        on_change=lambda e: filtrar_fornecedores(e.control.value),
        prefix_icon=ft.Icons.SEARCH,
        width=500
    )

    def filtrar_fornecedores(query):
        tabela.rows.clear()
        for i, f in enumerate(fornecedores):
            if (
                query.lower() in f["nome_fantasia"].lower()
                or query == str(f["id"])
            ):
                tabela.rows.append(criar_linha_tabela(i, f))
        page.update()

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nome Fantasia")),
            ft.DataColumn(ft.Text("Razão Social")),
            ft.DataColumn(ft.Text("CNPJ")),
            ft.DataColumn(ft.Text("Telefone")),
            ft.DataColumn(ft.Text("E-mail")),
            ft.DataColumn(ft.Text("Observações")),
            ft.DataColumn(ft.Text("Ações")),
        ],
        rows=[]
    )

    atualizar_lista()

    return ft.View(
        route="/fornecedores",
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(name=ft.Icons.BUSINESS, color=ft.Colors.WHITE),
                ft.Text("Fornecedores", color=ft.Colors.WHITE),
            ], spacing=10),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=voltar_home),
            bgcolor=ft.Colors.RED
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
                            on_click=lambda e: (
                                globals().__setitem__('fornecedor_em_edicao', None),
                                limpar_campos(),
                                setattr(dialog, 'open', True),
                                page.update()
                            ),
                            bgcolor=ft.Colors.RED,
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