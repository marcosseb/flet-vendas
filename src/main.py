import flet as ft
from routes import login, home, cadastro_login, clientes, vendas, cadastro_vendas, \
                    fornecedores, produtos, relatorios, funcionarios, configuracoes, \
                    estoque


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1200
    page.window.height = 700
    page.window.left = 950
    page.window.top = 10
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

    page.window.always_on_top = True
    page.title = "SEVEN SYSTEM"

    def route_change(e: ft.RouteChangeEvent):
        # Sempre limpe a pilha de views e adicione a view inicial
        # Isso garante que você está sempre começando com uma tela limpa para a rota atual
        page.views.clear() 

        # Adicione a view da rota atual
        if page.route == "/login":
            page.views.append(login.View(page))
        elif page.route == "/home":
            page.views.append(home.View(page))
        elif page.route == "/cadastro_login":
            page.views.append(cadastro_login.View(page))
        elif page.route == "/produtos":
            page.views.append(produtos.View(page))
        elif page.route == "/clientes":
            page.views.append(clientes.View(page))
        elif page.route == "/vendas":
            page.views.append(vendas.View(page))
        elif page.route == "/fornecedores": 
            page.views.append(fornecedores.View(page))
        elif page.route == "/cadastro_vendas":
            page.views.append(cadastro_vendas.View(page))
        elif page.route == "/relatorios":
            page.views.append(relatorios.View(page))
        elif page.route == "/funcionarios":
            page.views.append(funcionarios.View(page))
        elif page.route == "/configuracoes":
            page.views.append(configuracoes.View(page))
        elif page.route == "/estoque":
            page.views.append(estoque.View(page))
        
        page.update()

    # Função para manipular o "voltar" do appbar (se houver)
    def view_pop(e: ft.ViewPopEvent):
        page.views.pop() # Remove a view atual da pilha
        top_view = page.views[-1] # Pega a view anterior
        page.go(top_view.route) # Navega para a rota da view anterior
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop # Adicione este manipulador
    page.go("/login") # Inicia na rota home

ft.app(target=main) # Use 'target' para main