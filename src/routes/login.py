import flet as ft
from storage_manager import verify_user, get_user_data

def View(page: ft.Page):
    """Tela de login do sistema
    Possui os campos de login, senha e botão de login.
    """
    page.title = "Login"

    if not page.client_storage.get("usuario_logado"):
        page.go("/login")

    def VaiPraHome(e):
        """Chama a tela de Home se o login for realizado com sucesso
        Senão, exibe uma mensagem de erro na tela de login."""
        usuario = txtLogin.value.strip()
        senha = txtSenha.value.strip()
        
        db_name = verify_user(usuario, senha)
        if db_name:
            mensagem_erro.visible = False
            mensagem_erro.value = ""

            # Armazena os dados do usuário no client_storage
            user_data = get_user_data(usuario)
            if user_data:
                nome, email, empresa = user_data
                page.client_storage.set("usuario_logado", usuario)
                page.client_storage.set("empresa_logada", empresa)
                page.client_storage.set("nome_usuario", nome)
                page.client_storage.set("email_usuario", email)
                page.client_storage.set("user_db", db_name)

            page.go("/home")
        else:
            mensagem_erro.visible = True
            mensagem_erro.value = "Usuário ou senha incorretos!"
            page.update()

    def VaiPraCadastro(e):
        page.go("/cadastro_login")

    logo = ft.Image(
        src="seven.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN
    )

    txtLogin = ft.TextField(
        label="Usuário",
        prefix_icon=ft.Icons.PERSON,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_100,
    )

    txtSenha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        border_color=ft.Colors.BLUE_100,
    )

    btnEntrar = ft.ElevatedButton(
        text="ENTRAR",
        on_click=VaiPraHome,
        style=ft.ButtonStyle(
            bgcolor="#649C33",
            color=ft.Colors.WHITE,
            padding=ft.padding.symmetric(horizontal=40, vertical=15),
            shape=ft.RoundedRectangleBorder(radius=12),
        )
    )

    mensagem_erro = ft.Text(
        value="",
        color=ft.Colors.RED_700,
        visible=False,
        size=14,
        weight=ft.FontWeight.BOLD
    )

    row_buttons = ft.TextButton(
        "Não tem uma conta? Cadastre-se",
        on_click=VaiPraCadastro
    )

    card_login = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text("SEVEN SYSTEM", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                ft.Text("Acesse sua conta", size=16, color=ft.Colors.GREY_600),
                txtLogin,
                txtSenha,
                mensagem_erro,
                btnEntrar,
                row_buttons,
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=30,
        width=360,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLUE_GREY_100, spread_radius=0.5),
    )

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=card_login,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLUE_GREY_50
            )
        ]
    )