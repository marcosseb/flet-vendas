import flet as ft
import re
from storage_manager import create_user, init_db

def View(page: ft.Page):
    """Tela de cadastro de usuários
    Possui os campos de nome completo, e-mail, nome de usuário, empresa, senha e confirmação de senha.
    """
    page.title = "Cadastro de Usuário"
    # Inicializa o banco de dados
    init_db()
    
    def VaiPraHome(e):
        page.go("/login")

    def verificar_forca_senha(senha):
        if len(senha) < 6:
            return "Fraca", ft.Colors.RED_700
        elif re.search(r"\d", senha) and re.search(r"[a-zA-Z]", senha) and len(senha) >= 8:
            return "Forte", ft.Colors.GREEN_700
        else:
            return "Média", ft.Colors.ORANGE_700

    def atualizar_forca_senha(e):
        forca, cor = verificar_forca_senha(txtSenha.value.strip())
        senha_status.value = f"Força da senha: {forca}"
        senha_status.color = cor
        page.update()

    def senhas(e):
        """Verifica se as senhas coincidem.
        Caso elas coincidam, um usuário é criado e redirecionado para a tela de login.
        """
        nome = txtNome.value.strip()
        email = txtEmail.value.strip()
        usuario = txtUsuario.value.strip()
        empresa = txtEmpresa.value.strip()
        senha = txtSenha.value.strip()
        conf_senha = txtConfirma.value.strip()

        if not nome or not email or not usuario or not empresa or not senha or not conf_senha:
            result.value = "Preencha todos os campos."
            result.color = ft.Colors.RED
            page.update()
            return

        if senha != conf_senha:
            result.value = "As senhas não coincidem."
            result.color = ft.Colors.RED
            page.update()
            return

        if create_user(nome, email, empresa, usuario, senha):
            result.value = "Usuário criado com sucesso!"
            result.color = ft.Colors.GREEN
            page.update()
            page.go("/login")
        else:
            result.value = "Usuário já cadastrado!"
            result.color = ft.Colors.RED
            page.update()

    appbar = ft.AppBar(
        title=ft.Text("Cadastro de Usuário", color=ft.Colors.WHITE),
        center_title=True,
        bgcolor=ft.Colors.GREEN_900,
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=VaiPraHome)
    )

    logo = ft.Image(src="seven.png", width=140)

    txtNome = ft.TextField(label="Nome completo", width=350)
    txtEmail = ft.TextField(label="E-mail", width=350)
    txtUsuario = ft.TextField(label="Nome de usuário", width=350)
    txtEmpresa = ft.TextField(label="Empresa", width=350)
    txtSenha = ft.TextField(label="Senha", password=True, width=350, on_change=atualizar_forca_senha)
    txtConfirma = ft.TextField(label="Confirme a senha", password=True, width=350)
    senha_status = ft.Text(value="", size=12)
    result = ft.Text()

    criar = ft.ElevatedButton(
        text="Criar",
        on_click=senhas,
        width=160,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.INDIGO_600,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15
        )
    )

    card = ft.Container(
        content=ft.Column(
            controls=[
                logo,
                txtNome,
                txtEmail,
                txtUsuario,
                txtEmpresa,
                txtSenha,
                senha_status,
                txtConfirma,
                criar,
                result
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=30,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        width=420,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12),
        alignment=ft.alignment.center,
    )

    return ft.View(
        route="/cadastro_login",
        appbar=appbar,
        controls=[
            ft.Container(
                content=card,
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        bgcolor=ft.Colors.BLUE_GREY_100,
        scroll=ft.ScrollMode.AUTO,
    )