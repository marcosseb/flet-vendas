import flet as ft
from data import funcionarios
import datetime
import re
from database.funcionarios_controller import FuncionariosController  # Importa o controlador de funcionários

def View(page: ft.Page):
    # Instancia o controlador de funcionários
    db_funcionarios = FuncionariosController(page.client_storage.get("user_db"))
    funcionario_para_excluir = {"index": None}
    funcionario_em_edicao = {"index": None} 

    id_field = ft.TextField(label="ID", read_only=True, width=120)

    def voltar_home(e):
        page.go("/home")

    def criar_linha_tabela(i, p):
        """
        Cria uma linha da tabela com os dados do funcionário.

        Args:
            i (int): O índice do funcionário na lista de funcionários.
            p (dict): O dicionário com os dados do funcionário.

        Returns:
            ft.DataRow: A linha da tabela com os dados do funcionário.
        """
        observacoes_text = ft.Text(
            p["observacoes"],
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
            size=12,
            text_align=ft.TextAlign.JUSTIFY
        )
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(p["id"]))),
                ft.DataCell(ft.Text(p["nome"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataCell(ft.Text(p["cargo"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataCell(ft.Text(str(p["telefone"]))),
                ft.DataCell(ft.Text(p["email"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataCell(ft.Text(str(p["data_admissao"]))),
                ft.DataCell(observacoes_text),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Clique aqui para editar funcionário",
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, idx=i: editar_funcionario(idx)(e)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Clique aqui para excluir funcionário",
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, idx=i: excluir_funcionario(idx)(e)
                        ),
                    ], spacing=5)
                ),
            ]
        )

    def atualizar_lista():
        """Atualiza a lista de funcionários na tabela."""
        tabela.rows.clear()
        #for i, p in enumerate(funcionarios):
        #    tabela.rows.append(criar_linha_tabela(i, p))
        funcionarios.clear()
        funcionarios.extend(db_funcionarios.listar_funcionarios())
        for i, p in enumerate(funcionarios):
            tabela.rows.append(criar_linha_tabela(i, p))
        page.update()

    def editar_funcionario(index):
        """
        Edita o funcionário com base no índice fornecido.

        Args: 
            index (int): O índice do funcionário na lista de funcionários.
        Returns:
            function: Uma função que edita o funcionário com base no índice fornecido.
        """
        def handler(e):
            # Usando o dicionário para estado de edição
            funcionario_em_edicao["index"] = index
            funcionario = funcionarios[index]
            id_field.value = funcionario["id"]
            nome_field.value = funcionario["nome"]
            cargo_field.value = funcionario["cargo"]
            telefone_field.value = funcionario["telefone"]
            email_field.value = funcionario["email"]
            data_field.value = funcionario["data_admissao"]
            observacoes_field.value = funcionario["observacoes"]
            dialog.open = True
            page.update()
        return handler

    def excluir_funcionario(index):
        """Exclui o funcionário com base no índice fornecido.

        Args: 
            index (int): O índice do funcionário na lista de funcionários.
        Returns:
            function: Uma função que exclui o funcionário com base no índice fornecido.
        """
        def handler(e):
            funcionario_para_excluir["index"] = index
            confirm_dialog.open = True
            page.update()
        return handler

    def confirmar_exclusao(e):
        """Confirma a exclusão de um funcionário com base no índice fornecido.
        
        Verifica se o índice está disponível e, se sim, exclui o funcionário da
        lista de funcionários e atualiza a tabela. Em seguida, fecha o di ́ alogo de
        confirma ção.
        
        Args:
            e (object): O evento de clique.
        """

        index = funcionario_para_excluir["index"]
        if index is not None:
            funcionario_id = funcionarios[index]["id"]
            if db_funcionarios.excluir_funcionario(funcionario_id):
                funcionarios.pop(index)
                atualizar_lista()
        confirm_dialog.open = False
        page.update()

    def cancelar_exclusao(e):
        
        """
        Cancela a exclusão de um funcionário e fecha o diálogo de confirmação.

        Args:
            e (object): O evento de clique.
        """

        confirm_dialog.open = False
        page.update()

    def abrir_calendario(e):
        """
        Abre o calendário para que o usuário possa selecionar uma data.

        Args:
            e (object): O evento de clique.
        """

        calendario.open = True
        page.update()

    def limpar_campos():
        """Limpa todos os campos do formulário."""
        id_field.value = ""
        nome_field.value = ""
        cargo_field.value = ""
        telefone_field.value = ""
        email_field.value = ""
        data_field.value = datetime.date.today().strftime("%d/%m/%Y") # Formata a data atual - Modificar futuramente
        observacoes_field.value = ""
        # Limpar estado de edição
        funcionario_em_edicao["index"] = None 
        for f in [nome_field, telefone_field]:
            f.error_text = None
            f.border_color = None # Limpar a cor da borda também

    def formatar_telefone(e):
        # Remove todos os caracteres não numéricos
        """
        Formata o telefone no padrão (00) 00000-0000 ou (00) 0000-0000.
        """
        
        v = re.sub(r"\D", "", telefone_field.value)
        
        # Limita a 11 dígitos para formatação
        if len(v) > 11:
            v = v[:11]

        formatted_v = ""
        if len(v) > 0:
            if len(v) <= 2:
                formatted_v = f"({v}"
            elif len(v) <= 7:
                formatted_v = f"({v[:2]}) {v[2:]}"
            elif len(v) <= 11:
                # Trata 9 dígitos para celular (5 primeiros) e 4 para o restante
                if len(v) == 11:
                    formatted_v = f"({v[:2]}) {v[2:7]}-{v[7:]}"
                else: # 10 dígitos para telefone fixo ou celular antigo (4 primeiros)
                    formatted_v = f"({v[:2]}) {v[2:6]}-{v[6:]}"
        
        telefone_field.value = formatted_v
        page.update()

    def salvar_funcionario_click(e):
        """
        Salva um novo funcionário ou edita um existente.

        Verifica se os campos obrigatórios foram preenchidos. Se sim, salva o
        funcionário no banco de dados e atualiza a lista de funcionários.

        Se o funcionário estiver em edição, salva as alterações no banco de dados
        e atualiza a lista de funcionários.

        Args:
            e (object): O evento de clique.
        """
        campos_obrigatorios = [
            (nome_field, "Nome"),
            (telefone_field, "Telefone"),
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

        novo_funcionario = {
            #"id": int(id_field.value),
            "nome": nome_field.value,
            "cargo": cargo_field.value,
            "telefone": telefone_field.value,
            "email": email_field.value,
            "data_admissao": data_field.value,
            "observacoes": observacoes_field.value,
        }

        # Usa o dicionário para verificar o estado de edição
        if funcionario_em_edicao["index"] is None:
            funcionario_id = db_funcionarios.cadastrar_funcionario(novo_funcionario)
            if funcionario_id:
                novo_funcionario["id"] = funcionario_id
                funcionarios.append(novo_funcionario)
        else:
            #funcionarios[funcionario_em_edicao["index"]] = novo_funcionario
            index = funcionario_em_edicao["index"]
            funcionario_id = funcionarios[index]["id"]
            if db_funcionarios.atualizar_funcionario(funcionario_id, novo_funcionario):
                novo_funcionario["id"] = funcionario_id
                funcionarios[funcionario_em_edicao["index"]] = novo_funcionario

        # Limpar estado de edição após salvar
        funcionario_em_edicao["index"] = None
        atualizar_lista()
        dialog.open = False
        page.update()

    salvar_funcionario = ft.ElevatedButton(
        "Salvar",
        on_click=salvar_funcionario_click,
        tooltip="Clique aqui para salvar este funcionário", # Adicionado tooltip
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
        )
    )

    # Campos de entrada
    nome_field = ft.TextField(label="* Nome", width=180)
    cargo_field = ft.TextField(label="Cargo")
    telefone_field = ft.TextField(
        label="* Telefone",
        on_change=formatar_telefone, # Usa on_change para formatação em tempo real
        max_length=15, # Limita o comprimento do texto no campo, incluindo a formatação
        keyboard_type=ft.KeyboardType.NUMBER, # Sugere teclado numérico
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]?", replacement_string="") # Permite apenas dígitos
    )
    email_field = ft.TextField(label="E-mail")
    observacoes_field = ft.TextField(label="Observações")

    data_field = ft.TextField(
        label="Data de admissão",
        value=datetime.date.today().strftime("%d/%m/%Y"),
        read_only=True,
        suffix=ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=abrir_calendario),
        width=300
    )

    def on_data_picker_change(e):
        """Atualiza o campo de data de admissão com o valor selecionado no calendário."""

        data_field.value = e.control.value.strftime("%d/%m/%Y")
        page.update()

    calendario = ft.DatePicker(on_change=on_data_picker_change)
    page.overlay.append(calendario)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cadastrar/Editar Funcionário"),
        content=ft.Container(
            content=ft.Column([
                ft.Row([id_field, nome_field], spacing=10), # Agrupando para layout
                cargo_field,
                telefone_field, # Correção: usando a instância já definida
                email_field,
                data_field,
                observacoes_field
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=350,
            height=520,
            padding=10
        ),
        actions=[
            salvar_funcionario,
            ft.ElevatedButton(
                "Cancelar",
                tooltip="Clique aqui para cancelar o cadastro", # Adicionado tooltip
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
        content=ft.Text("Você realmente deseja excluir este funcionário?"),
        actions=[
            ft.TextButton("Cancelar", tooltip="Clique aqui para cancelar a exclusão", on_click=cancelar_exclusao), # Adicionado tooltip
            ft.TextButton("Excluir", tooltip="Clique aqui para excluir este funcionário", on_click=confirmar_exclusao), # Adicionado tooltip
        ]
    )
    page.overlay.append(confirm_dialog)

    campo_pesquisa = ft.TextField(
        label="Pesquisar funcionário (por nome ou ID)",
        visible=True,
        on_change=lambda e: filtrar_funcionarios(e.control.value),
        prefix_icon=ft.Icons.SEARCH,
        width=500
    )

    def filtrar_funcionarios(query):
        """Filtrar a lista de funcionários com base na pesquisa."""
        tabela.rows.clear()
        for i, p in enumerate(funcionarios):
            if (
                query.lower() in p["nome"].lower()
                or query == str(p["id"])
            ):
                tabela.rows.append(criar_linha_tabela(i, p))
        page.update()

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("NOME")), # Alterado para maiúsculas como em produtos
            ft.DataColumn(ft.Text("CARGO")), # Alterado para maiúsculas como em produtos
            ft.DataColumn(ft.Text("TELEFONE")), # Alterado para maiúsculas como em produtos
            ft.DataColumn(ft.Text("E-MAIL")), # Alterado para maiúsculas como em produtos
            ft.DataColumn(ft.Text("DATA ADMISSÃO")), # Alterado para maiúsculas como em produtos
            ft.DataColumn(ft.Text("OBSERVAÇÕES")), # Alterado para maiúsculas como em produtos
            ft.DataColumn(ft.Text("AÇÕES")), # Alterado para maiúsculas como em produtos
        ],
        rows=[]
    )

    atualizar_lista()

    def abrir_dialogo_cadastro(e):
        """
        Abre o diálogo para cadastro/edição de funcionários.

        Args:
            e (event): O evento que disparou esta função.
        """
        funcionario_em_edicao["index"] = None
        limpar_campos()
        dialog.open = True
        page.update()


    return ft.View(
        route="/funcionarios",
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(name=ft.Icons.PERSON, color=ft.Colors.WHITE),
                ft.Text("Funcionários", color=ft.Colors.WHITE),
            ], spacing=10),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Clique aqui para voltar", icon_color=ft.Colors.WHITE, on_click=voltar_home),
            bgcolor=ft.Colors.ORANGE
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
                            bgcolor=ft.Colors.ORANGE,
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
