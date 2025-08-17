import flet as ft
from database import vendas_controller, clientes_controller, produtos_controller


def gerar_relatorios(vendas, clientes, itens, produtos):
    vendas_por_cliente = {}
    vendas_por_produto = {}
    total_geral = 0

    # Agrupar vendas por cliente
    for venda in vendas:
        cliente_id = venda['cliente_id']
        cliente_nome = next((c['nome'] for c in clientes if c['id'] == cliente_id), "Desconhecido")
        vendas_por_cliente[cliente_nome] = vendas_por_cliente.get(cliente_nome, 0) + 1
        total_geral += venda['total']

        # Agrupar vendas por produto
        for item in itens:
            if item['venda_id'] == venda['id']:
                produto_id = item['produto_id']
                produto_nome = next((p['nome'] for p in produtos if p['id'] == produto_id), "Desconhecido")
                vendas_por_produto[produto_nome] = vendas_por_produto.get(produto_nome, 0) + item['quantidade']

    vendas_por_cliente = dict(sorted(vendas_por_cliente.items(), key=lambda item: item[1], reverse=True))
    vendas_por_produto = dict(sorted(vendas_por_produto.items(), key=lambda item: item[1], reverse=True))
    

    return vendas_por_cliente, vendas_por_produto, total_geral


def formatar_moeda(valor):
    """Formata um valor monetário para o padrão brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def criar_card(titulo, valor, icone, cor_icon, cor_fundo):
    return ft.Container(
        content=ft.Row([
            ft.Icon(icone, size=40, color=cor_icon),
            ft.Column([
                ft.Text(titulo, size=14, weight="w500", color=ft.Colors.GREY_800),
                ft.Text(valor, size=22, weight="bold", color=cor_icon),
            ], spacing=2)
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        bgcolor=cor_fundo,
        border_radius=15,
        expand=True,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        )
    )


def criar_tabela(titulo, dados, col1, col2):
    return ft.Column([
        ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_900),
        ft.Container(
            content=ft.Text("Nenhuma venda registrada.") if not dados else ft.DataTable(
                heading_row_color=ft.Colors.GREY_100,
                columns=[
                    ft.DataColumn(label=ft.Text(col1, weight="bold")),
                    ft.DataColumn(label=ft.Text(col2, weight="bold")),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(k))),
                        ft.DataCell(ft.Text(str(v))),
                    ])
                    for k, v in dados.items()
                ]
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10
        ),
        ft.Divider()
    ], spacing=10)


def View(page: ft.Page):
    db = page.client_storage.get("user_db")
    db_vendas = vendas_controller.VendasController(db)
    db_clientes = clientes_controller.ClientesController(db)
    db_produtos = produtos_controller.ProdutosController(db)
    produtos = db_produtos.listar_produtos()
    vendas = db_vendas.listar_vendas()
    clientes = db_clientes.listar_clientes()
    itens = db_vendas.listar_itens_venda()
    def VaiPraHome(e):
        page.go("/home")

    vendas_por_cliente, vendas_por_produto, total_geral = gerar_relatorios(vendas, clientes, itens, produtos)

    cards = ft.Row([
        criar_card("Total de Vendas", formatar_moeda(total_geral), ft.Icons.ATTACH_MONEY,
                   ft.Colors.GREEN_500, ft.Colors.GREEN_50),
        criar_card("Produtos", str(len(produtos)), ft.Icons.INVENTORY_2,
                   ft.Colors.BLUE_500, ft.Colors.BLUE_50),
        criar_card("Clientes", str(len(clientes)), ft.Icons.PEOPLE,
                   ft.Colors.ORANGE_500, ft.Colors.ORANGE_50),
    ], spacing=15)

    return ft.View(
        route="/relatorios",
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(name=ft.Icons.ASSESSMENT_ROUNDED, color=ft.Colors.WHITE),
                ft.Text("Relatórios", color=ft.Colors.WHITE),
            ], spacing=10),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=VaiPraHome),
            bgcolor=ft.Colors.YELLOW_700
        ),
        controls=[
            ft.Container(cards, padding=20),
            ft.Container(
                content=ft.Column([
                    criar_tabela("📊 Vendas por Cliente", vendas_por_cliente, "Cliente", "Qtd. de Vendas"),
                    criar_tabela("📦 Vendas por Produto", vendas_por_produto, "Produto", "Qtd. Vendida"),
                    ft.Text(
                        f"💰 Total Geral de Vendas: {formatar_moeda(total_geral)}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_700
                    )
                ], spacing=20),
                padding=20
            )
        ],
        scroll=ft.ScrollMode.AUTO
    )
