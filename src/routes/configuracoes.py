import flet as ft
import hashlib
import os
from storage_manager import get_db_connection, get_user_data

def View(page: ft.Page):
    usuario_logado = page.client_storage.get("usuario_logado")
    user_data = get_user_data(usuario_logado)
    
    if not user_data:
        page.go("/login")
        return

    nome, email, empresa = user_data
    nome_empresa_text = ft.Text(f"{empresa}", size=20, weight="bold")

    def abrir_edicao_empresa(e):
        nome_empresa_input = ft.TextField(label="Nome da Empresa", value=empresa, width=400)

        def salvar_nome_empresa(ev):
            nonlocal empresa
            empresa = nome_empresa_input.value
            nome_empresa_text.value = empresa
            
            # Atualiza no banco de dados
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE usuarios SET empresa = ? WHERE usuario = ?",
                    (empresa, usuario_logado)
                )
                conn.commit()

            # Atualiza no client storage
            page.client_storage.set("empresa_logada", empresa)

            dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Nome da empresa atualizado!"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Nome da Empresa"),
            content=nome_empresa_input,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo(dialog)),
                ft.TextButton("Salvar", on_click=salvar_nome_empresa),
            ],
            actions_alignment="end"
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def abrir_dialogo_alterar_senha(e):
        senha_atual = ft.TextField(label="Senha Atual", password=True, can_reveal_password=True)
        nova_senha = ft.TextField(label="Nova Senha", password=True, can_reveal_password=True)
        confirmar_senha = ft.TextField(label="Confirmar Nova Senha", password=True, can_reveal_password=True)
        mensagem_feedback = ft.Text("", color=ft.Colors.RED, size=12, opacity=0)

        def senha_forte(s):
            return (
                len(s) >= 8 and
                any(c.islower() for c in s) and
                any(c.isupper() for c in s) and
                any(c.isdigit() for c in s) and
                any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in s)
            )

        def mostrar_mensagem(texto, cor):
            mensagem_feedback.value = texto
            mensagem_feedback.color = cor
            mensagem_feedback.opacity = 1
            page.update()

        def limpar_mensagem():
            mensagem_feedback.opacity = 0
            page.update()

        def confirmar_alteracao(ev):
            # Verifica se a senha atual está correta
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT senha_hash, salt FROM usuarios WHERE usuario = ?", 
                    (usuario_logado,)
                )
                result = cursor.fetchone()
                
                if result:
                    stored_hash, salt = result
                    salt = bytes.fromhex(salt)
                    current_hash = hashlib.pbkdf2_hmac(
                        'sha512', 
                        senha_atual.value.encode('utf-8'), 
                        salt, 
                        100000
                    ).hex()
                    
                    if current_hash != stored_hash:
                        mostrar_mensagem("Senha atual incorreta!", ft.Colors.RED)
                        return

            # Validações da nova senha
            if nova_senha.value != confirmar_senha.value:
                mostrar_mensagem("As senhas novas não coincidem!", ft.Colors.RED)
            elif not senha_forte(nova_senha.value):
                mostrar_mensagem("A nova senha não é forte o suficiente!", ft.Colors.RED)
            else:
                # Atualiza a senha no banco de dados
                new_salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
                new_hash = hashlib.pbkdf2_hmac(
                    'sha512', 
                    nova_senha.value.encode('utf-8'), 
                    new_salt, 
                    100000
                ).hex()
                
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE usuarios SET senha_hash = ?, salt = ? WHERE usuario = ?",
                        (new_hash, new_salt.hex(), usuario_logado)
                    )
                    conn.commit()

                mostrar_mensagem("Senha alterada com sucesso!", ft.Colors.GREEN)
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Alterar Senha"),
            content=ft.Column(
                [senha_atual, nova_senha, confirmar_senha, mensagem_feedback],
                tight=True
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo(dialog)),
                ft.TextButton("Salvar", on_click=confirmar_alteracao),
            ],
            actions_alignment="end"
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def fechar_dialogo(dialog):
        dialog.open = False
        page.update()

    return ft.View(
        route="/configuracoes",
        appbar=ft.AppBar(
            title=ft.Text("Configurações", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_900,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=lambda e: page.go("/home"))
        ),
        controls=[
            ft.Column([
                ft.Row([
                    nome_empresa_text,
                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar Nome da Empresa", on_click=abrir_edicao_empresa)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=500),
                ft.Divider(),
                ft.Text("Preferências", style="titleMedium"),
                ft.Switch(label="Receber notificações", value=True),
                ft.Divider(),
                ft.ElevatedButton("Alterar Senha", icon=ft.Icons.LOCK, on_click=abrir_dialogo_alterar_senha),
                ft.Divider(),
                ft.Text("Sobre o App", style="titleMedium"),
                ft.Text("Versão: 1.0.0"),
                ft.Text(f"Usuário: {usuario_logado}"),
                ft.Text(f"Email: {email}"),
                ft.Text("© 2025 - Todos os direitos reservados"),
            ],
            spacing=20,
            width=500
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )