import flet as ft
import datetime
import asyncio
from database import vendas_controller, clientes_controller, produtos_controller

def View(page: ft.Page):
    """Tela inicial do sistema"""
    db = page.client_storage.get("user_db")
    db_vendas = vendas_controller.VendasController(db)
    db_clientes = clientes_controller.ClientesController(db)
    db_produtos = produtos_controller.ProdutosController(db)

    drawer_open = False

    page.theme_mode = ft.ThemeMode.LIGHT  # Padrão: tema claro
    if page.client_storage.get("dark_mode"):
        page.theme_mode = ft.ThemeMode.DARK

    nome_empresa = ft.Text(
        color=ft.Colors.WHITE,
        size=16,
        weight=ft.FontWeight.BOLD,
    )

    def toggle_theme(e):
        """Alterna entre tema claro e escuro"""
        page.theme_mode = (
            ft.ThemeMode.DARK 
            if page.theme_mode == ft.ThemeMode.LIGHT 
            else ft.ThemeMode.LIGHT
        )
        botao_tema.icon = ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.DARK_MODE
        page.client_storage.set("dark_mode", page.theme_mode == ft.ThemeMode.DARK)
        page.update()

    botao_tema = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        icon_color=ft.Colors.WHITE,
        tooltip="Alternar para modo escuro",
        on_click=toggle_theme,
    )

    # Atualiza com o valor mais recente
    nome_empresa.value = page.client_storage.get("empresa_logada") or "Empresa não identificada"

    def logout(e):
        """Limpa os dados do client storage e redireciona para a tela de login"""
        nonlocal drawer_open
        drawer_open = False
        menu_container.visible = False
        page.client_storage.remove("usuario_logado")
        page.client_storage.remove("empresa_logada")
        page.client_storage.remove("nome_usuario")
        page.client_storage.remove("email_usuario")

        page.update()
        page.go("/login")

    def ir_para(route):
        def handler(e):
            nonlocal drawer_open
            drawer_open = False
            menu_container.visible = False
            page.update()
            page.go(route)
        return handler

    def menu_item(icon, title, route, icon_color=ft.Colors.WHITE, text_color=ft.Colors.WHITE):
        return ft.ListTile(
            leading=ft.Icon(icon, color=icon_color),
            title=ft.Text(title, color=text_color),
            on_click=ir_para(route),
            hover_color=ft.Colors.GREEN_900,
        )

    menu_container = ft.Container(
        content=ft.ListView(
            controls=[
                ft.Divider(color=ft.Colors.WHITE),
                menu_item(ft.Icons.HOME, "Início", "/home"),
                menu_item(ft.Icons.SHOPPING_BAG, "Produtos", "/produtos"),
                menu_item(ft.Icons.PEOPLE, "Clientes", "/clientes"),
                menu_item(ft.Icons.POINT_OF_SALE, "Vendas", "/vendas"),
                menu_item(ft.Icons.LOCAL_SHIPPING, "Fornecedores", "/fornecedores"),
                menu_item(ft.Icons.INVENTORY, "Estoque", "/estoque"),
                menu_item(ft.Icons.ASSESSMENT, "Relatórios", "/relatorios"),
                menu_item(ft.Icons.PERSON, "Funcionários", "/funcionarios"),
                ft.Divider(color=ft.Colors.WHITE),
                menu_item(ft.Icons.SETTINGS, "Configurações", "/configuracoes"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.WHITE),
                    title=ft.Text("Sair", color=ft.Colors.WHITE),
                    on_click=logout
                ),
            ],
            spacing=5,
            expand=True,
            padding=0
        ),
        width=220,
        bgcolor=ft.Colors.GREEN_900,
        padding=10,
        border_radius=ft.border_radius.only(top_right=12, bottom_right=12),
        visible=False
    )

    page.overlay.append(menu_container)

    def toggle_menu(e):
        """Abre e fecha o menu lateral"""
        nonlocal drawer_open
        drawer_open = not drawer_open
        menu_container.visible = drawer_open
        page.update()

    # Texto do horário que será atualizado
    texto_horario = ft.Text(
        f"Hoje: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
        color=ft.Colors.WHITE
    )

    appbar = ft.AppBar(
        title=nome_empresa,
        bgcolor=ft.Colors.GREEN_900,
        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_menu, icon_color=ft.Colors.WHITE),
        actions=[
            botao_tema,
            texto_horario,
            ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, on_click=logout, tooltip="Sair")
        ])

    def atualizar_hora():
        """Atualiza o texto do horário"""
        texto_horario.value = f"Hoje: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        page.update()

    async def atualiza_tempo():
        """Atualiza o horário de forma assíncrona"""
        while True:
            atualizar_hora()
            await asyncio.sleep(1)

    vendas = db_vendas.listar_vendas()
    
    total_vendas = sum(venda["total"] for venda in vendas) if vendas else 0.0
    total_clientes = len(db_clientes.listar_clientes())
    total_produtos = len(db_produtos.listar_produtos())

    indicadores = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.MONEY, color=ft.Colors.GREEN_500),
                ft.Text("Total de Vendas", size=16, weight="bold", color=ft.Colors.BLACK),
                ft.Text(f"R$ {total_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        size=20, color=ft.Colors.GREEN_500)
            ]),
            padding=10,
            bgcolor=ft.Colors.GREEN_100,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SHOPPING_CART, color=ft.Colors.BLUE_500),
                ft.Text("Produtos", size=16, weight="bold", color=ft.Colors.BLACK),
                ft.Text(str(total_produtos), size=20, color=ft.Colors.BLUE_500)
            ]),
            padding=10,
            bgcolor=ft.Colors.BLUE_100,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PERSON, color=ft.Colors.PURPLE_500),
                ft.Text("Clientes", size=16, weight="bold", color=ft.Colors.BLACK),
                ft.Text(str(total_clientes), size=20, color=ft.Colors.PURPLE_500)
            ]),
            padding=10,
            bgcolor=ft.Colors.PURPLE_100,
            border_radius=10,
            expand=True
        )
    ], spacing=15)

    atalhos = ft.GridView(
    expand=True,
    max_extent=200,
    spacing=15,
    run_spacing=15,
    controls=[
        ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ADD_SHOPPING_CART , color=ft.Colors.WHITE),
                    ft.Text("Nova Venda", color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            on_click=ir_para("/cadastro_vendas"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=0),
                bgcolor=ft.Colors.GREEN,
                padding=20
            )
        ),
        ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ADD_BOX , color=ft.Colors.WHITE),
                    ft.Text("Novo Produto", color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            on_click=ir_para("/produtos"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=0),
                bgcolor=ft.Colors.BLUE_500,
                padding=20
            )
        ),
        ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PERSON_ADD , color=ft.Colors.WHITE),
                    ft.Text("Clientes", color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            on_click=ir_para("/clientes"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=0),
                bgcolor=ft.Colors.PURPLE,
                padding=20
            )
        ),
        ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOCAL_SHIPPING , color=ft.Colors.WHITE),
                    ft.Text("Fornecedor", color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            on_click=ir_para("/fornecedores"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=0),
                bgcolor=ft.Colors.RED,
                padding=20
            )
        )
    ]
)

    page.run_task(atualiza_tempo)

    return ft.View(
        route="/home",
        appbar=appbar,
        controls=[
            ft.Row([
                ft.Column([
                    ft.Text("Visão Geral", size=24, weight=ft.FontWeight.BOLD),
                    indicadores,
                    ft.Divider(color=ft.Colors.WHITE),
                    ft.Text("Atalhos", size=24, weight=ft.FontWeight.BOLD),
                    atalhos
                ], expand=True, scroll=ft.ScrollMode.AUTO)
            ], expand=True)
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        bgcolor=page.bgcolor,
        scroll=ft.ScrollMode.AUTO
    )