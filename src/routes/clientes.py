#CÓDIGO COMPLETO JÁ TESTADO
import flet as ft
import datetime
import re
import requests
from data import clientes
from database.clientes_controller import ClientesController

def View(page: ft.Page):
    db_clientes = ClientesController(page.client_storage.get("user_db"))
    cliente_para_excluir = {"index": None}
    cliente_em_edicao = {"index": None}
    id_field = ft.TextField(label="ID", read_only=True, width=120)

    def voltar_home(e):
        page.go("/home")

    def criar_linha_tabela(i, c):
        endereco_completo = ""
        if c.get("endereco"):
            endereco_completo += c["endereco"]
        if c.get("numero"):
            if endereco_completo:
                endereco_completo += f", {c['numero']}"
            else:
                endereco_completo = c["numero"]
        if c.get("complemento"):
            endereco_completo += f" {c['complemento']}"

        return ft.DataRow(
            cells=[
            ft.DataCell(ft.Text(str(c["id"]))),
            ft.DataCell(ft.Text(c["nome"], max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(c["cpf_cnpj"], max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(c["telefone"], max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(c["email"], max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(endereco_completo, max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(c["cep"], max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(c.get("bairro", ""), max_lines=2, overflow="ellipsis")),
            ft.DataCell(ft.Text(c["data_cadastro"], max_lines=2, overflow="ellipsis")),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, idx=i: editar_cliente(idx)(e)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, idx=i: excluir_cliente(idx)(e)
                        ),
                    ], spacing=5)
                ),
            ]
        )

    def atualizar_lista():
        tabela.rows.clear()
        if clientes:
            for i, c in enumerate(clientes):
                print(i, c)
                tabela.rows.append(criar_linha_tabela(i, c))
        elif not clientes:
            clientes.clear()
            clientes.extend(db_clientes.listar_clientes())
            for i, c in enumerate(clientes):
                tabela.rows.append(criar_linha_tabela(i, c))  
        page.update()

    def editar_cliente(index):
        def handler(e):
            cliente_em_edicao["index"] = index
            c = clientes[index]
            id_field.value = str(c["id"])
            nome_field.value = c["nome"]
            cpf_cnpj_field.value = c["cpf_cnpj"]
            telefone_field.value = c["telefone"]
            email_field.value = c["email"]
            cep_field.value = c["cep"]
            bairro_field.value = c.get("bairro", "")
            cidade_field.value = c.get("cidade", "")
            estado_field.value = c.get("estado", "")
            endereco_field.value = c.get("endereco", "")
            numero_field.value = c.get("numero", "")
            complemento_field.value = c.get("complemento", "")
            data_field.value = c["data_cadastro"]
            cliente_data = {
                "id": c["id"],
                "nome": c["nome"],
                "cpf_cnpj": c["cpf_cnpj"],
                "telefone": c["telefone"],
                "email": c["email"],
                "cep": c["cep"],
                "bairro": c.get("bairro", ""),
                "cidade": c.get("cidade", ""),
                "estado": c.get("estado", ""),
                "endereco": c.get("endereco", ""),
                "numero": c.get("numero", ""),
                "complemento": c.get("complemento", ""),
                "data_cadastro": c["data_cadastro"]
            }
            db_clientes.atualizar_cliente(c["id"], cliente_data)
            print(db_clientes.listar_clientes())
            dialog.open = True
            page.update()
        return handler

    def excluir_cliente(index):
        def handler(e):
            cliente_para_excluir["index"] = index
            confirm_dialog.open = True
            page.update()
        return handler

    def confirmar_exclusao(e):
        index = cliente_para_excluir["index"]
        if index is not None:
            clientes.pop(index)
            db_clientes.excluir_cliente(index)
            atualizar_lista()
        confirm_dialog.open = False
        page.update()

    def cancelar_exclusao(e):
        confirm_dialog.open = False
        page.update()

    def abrir_calendario(e):
        calendario.open = True
        page.update()

    def limpar_campos():
        id_field.value = str(max([c["id"] for c in clientes], default=0) + 1)
        nome_field.value = ""
        cpf_cnpj_field.value = ""
        telefone_field.value = ""
        email_field.value = ""
        cep_field.value = ""
        bairro_field.value = ""
        cidade_field.value = ""
        estado_field.value = ""
        endereco_field.value = ""
        numero_field.value = ""
        complemento_field.value = ""
        data_field.value = datetime.date.today().strftime("%d/%m/%Y")
        for f in [nome_field, cpf_cnpj_field, telefone_field]:
            f.error_text = None

    def salvar_cliente_click(e):
        campos_obrigatorios = [
            (nome_field, "Nome"),
            (telefone_field, "Telefone")
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

        page.update()

        if faltando:
            return

        novo_cliente = {
            "id": int(id_field.value),
            "nome": nome_field.value,
            "cpf_cnpj": cpf_cnpj_field.value,
            "telefone": telefone_field.value,
            "email": email_field.value,
            "cep": cep_field.value,
            "bairro": bairro_field.value,
            "cidade": cidade_field.value,
            "estado": estado_field.value,
            "endereco": endereco_field.value,
            "numero": numero_field.value,
            "complemento": complemento_field.value,
            "data_cadastro": data_field.value
        }

        if cliente_em_edicao["index"] is None:
            clientes.append(novo_cliente)
            db_clientes.cadastrar_cliente(novo_cliente)
        else:
            clientes[cliente_em_edicao["index"]] = novo_cliente

        atualizar_lista()
        dialog.open = False
        page.update()

    def on_data_picker_change(e):
        data_field.value = e.control.value.strftime("%d/%m/%Y")
        page.update()

    def buscar_cep(e):
        cep = cep_field.value.strip().replace("-", "")
        if re.fullmatch(r"\d{8}", cep):
            try:
                r = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
                if "erro" not in r:
                    endereco_field.value = r.get("logradouro", "")
                    bairro_field.value = r.get("bairro", "")
                    cidade_field.value = r.get("localidade", "")
                    estado_field.value = r.get("uf", "")
                    numero_field.value = ""
                    complemento_field.value = ""
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("CEP não encontrado."), bgcolor=ft.Colors.RED)
                    page.snack_bar.open = True
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("Erro ao buscar o CEP."), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True

    def formatar_cpf_cnpj(e):
        v = re.sub(r"\D", "", cpf_cnpj_field.value)
        if len(v) <= 11:
            cpf_cnpj_field.value = re.sub(r"(\d{3})(\d{3})(\d{3})(\d{2})", r"\1.\2.\3-\4", v) if len(v) == 11 else v
        else:
            cpf_cnpj_field.value = re.sub(r"(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})", r"\1.\2.\3/\4-\5", v) if len(v) == 14 else v
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

    def formatar_cep(e):
        v = re.sub(r"\D", "", cep_field.value)
        if len(v) == 8:
            cep_field.value = f"{v[:5]}-{v[5:]}"
        else:
            cep_field.value = v
        page.update()

    calendario = ft.DatePicker(on_change=on_data_picker_change)
    page.overlay.append(calendario)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cadastrar/Editar Cliente"),
        content=ft.Container(
            content=ft.Column([
                ft.Row([id_field, nome_field := ft.TextField(label="* Nome", width=180)], spacing=10),
                cpf_cnpj_field := ft.TextField(label=" CPF/CNPJ", width=300, on_change=formatar_cpf_cnpj),
                telefone_field := ft.TextField(label="* Telefone", width=300, on_change=formatar_telefone),
                email_field := ft.TextField(label="Email", width=300),
                cep_row := ft.Row([
                    cep_field := ft.TextField(label="CEP", width=190, on_change=formatar_cep),
                    ft.IconButton(icon=ft.Icons.SEARCH, tooltip="Buscar CEP", on_click=buscar_cep)
                ]),
                ft.Row([
                    cidade_field := ft.TextField(label="Cidade", width=140),
                    estado_field := ft.TextField(label="Estado", width=60),
                ], spacing=10),
                bairro_field := ft.TextField(label="Bairro", width=300),
                endereco_field := ft.TextField(label="Endereço (Rua, Av, Travessa etc.)", width=300),
                ft.Row([
                    numero_field := ft.TextField(label="Número", width=90),
                    complemento_field := ft.TextField(label="Complemento", width=190),                 
                ], spacing=10),
                data_field := ft.TextField(
                    label="Data de Cadastro",
                    value=datetime.date.today().strftime("%d/%m/%Y"),
                    read_only=True,
                    suffix=ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=abrir_calendario),
                    width=300
                ),
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            width=380,
            height=600,
            padding=10
        ),
        actions=[
            ft.ElevatedButton("Salvar", on_click=salvar_cliente_click, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)),
            ft.ElevatedButton("Cancelar", on_click=lambda e: setattr(dialog, "open", False) or page.update(), style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE))
        ]
    )
    page.overlay.append(dialog)

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Exclusão"),
        content=ft.Text("Você realmente deseja excluir este cliente?"),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_exclusao),
            ft.TextButton("Excluir", on_click=confirmar_exclusao),
        ]
    )
    page.overlay.append(confirm_dialog)

    campo_pesquisa = ft.TextField(
        label="Pesquisar cliente (por nome, CPF/CNPJ, telefone ou ID)",
        visible=True,
        on_change=lambda e: filtrar_clientes(e.control.value),
        prefix_icon=ft.Icons.SEARCH,
        width=500
    )

    def filtrar_clientes(query):
        tabela.rows.clear()
        for i, c in enumerate(clientes):
            if (
                query.lower() in c["nome"].lower()
                or query in c["cpf_cnpj"].lower()
                or query in c["telefone"].lower()
                or query == str(c["id"])
            ):
                tabela.rows.append(criar_linha_tabela(i, c))
        page.update()

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID")),
            ft.DataColumn(label=ft.Text("Nome")),
            ft.DataColumn(label=ft.Text("CPF/CNPJ")),
            ft.DataColumn(label=ft.Text("Telefone")),
            ft.DataColumn(label=ft.Text("Email")),
            ft.DataColumn(label=ft.Text("Endereço")),
            ft.DataColumn(label=ft.Text("CEP")),
            ft.DataColumn(label=ft.Text("Bairro")),
            ft.DataColumn(label=ft.Text("Cadastro")),
            ft.DataColumn(label=ft.Text("Ações")),
        ],
        rows=[]
    )

    atualizar_lista()

    return ft.View(
        route="/clientes",
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(name=ft.Icons.PEOPLE, color=ft.Colors.WHITE),
                ft.Text("Clientes", color=ft.Colors.WHITE),
            ], spacing=10),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=voltar_home),
            bgcolor=ft.Colors.PURPLE
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
                                cliente_em_edicao.update({"index": None}), # Reseta o estado
                                limpar_campos(),
                                setattr(dialog, 'open', True),
                                page.update()
                            ),
                            bgcolor=ft.Colors.PURPLE,
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