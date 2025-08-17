import flet as ft
import globals
import datetime
import pandas as pd
import os
from database.vendas_controller import VendasController

_clock_task_vendas = None

def View(page: ft.Page):
    db_vendas = VendasController(page.client_storage.get("user_db"))
    global _clock_task_vendas
    venda_para_excluir = {'index': None}

    vendas = db_vendas.listar_vendas() 
    print("Vendas carregadas:", vendas) # Para depuração
    

    def voltar_home(e):
        # Ao sair da View, cancela a tarefa do relógio (se estiver rodando)
        if _clock_task_vendas and not _clock_task_vendas.done():
            _clock_task_vendas.cancel()
            print("Tarefa atualiza_tempo cancelada (Vendas).") # Para depuração
        page.go("/home")

    def ir_para_cadastro_vendas(e):
        globals.venda_em_edicao = None # Garante que estamos criando uma nova venda
        page.go("/cadastro_vendas")

    def editar_venda(venda_id):
        def handler(e):
            globals.venda_em_edicao = venda_id
            page.go("/cadastro_vendas")
        return handler

    def excluir_venda(venda_id):
        def handler(e):
            venda_para_excluir['index'] = venda_id # Armazena o ID da venda a ser excluída
            confirm_dialog.open = True
            page.update()
        return handler

    def confirmar_exclusao(e):
        venda_id = venda_para_excluir['index']
        # Fecha o diálogo
        if venda_id is not None:
            try:
                db_vendas.excluir_venda(venda_id) # Chama o método de exclusão do controlador
                page.open = ft.SnackBar(
                    ft.Text(f"Venda {venda_id} excluída com sucesso!", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_700
                )
                atualizar_lista() # Atualiza a lista de vendas
            except Exception as ex:
                page.open = ft.SnackBar(
                    ft.Text(f"Erro ao excluir venda: {ex}", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_700
                )
        confirm_dialog.open = False # Fecha o diálogo de confirmação
        page.update()

    def cancelar_exclusao(e):
        # Apenas fecha o diálogo
        page.dialog.open = False
        page.update()

    # --- Componentes de UI ---
    pesquisa = ft.TextField(
        hint_text="Pesquisar vendas (Cliente, Data, Status, Vendedor)...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: atualizar_lista(),
        expand=True,
        filled=True, # Adiciona estilo preenchido
        fill_color=ft.Colors.GREY_100, # Cor de preenchimento
    )

    lista_vendas = ft.Column(
        scroll=ft.ScrollMode.AUTO, # Permite rolagem dentro da coluna
        expand=True, # Permite que a coluna se expanda
    )


    # Relógio na AppBar
    hora_atual = ft.Text("", color=ft.Colors.WHITE)
    def atualizar_hora_vendas():
        hora_atual.value = f"Hoje: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        page.update()

    async def atualiza_tempo_vendas():
        while True:
            atualizar_hora_vendas()
            await asyncio.sleep(1)

    # --- Lógica de Agrupamento e Listagem ---
    def atualizar_lista():
        lista_vendas.controls.clear()

        termo = pesquisa.value.lower() if pesquisa.value else "" # Termo de pesquisa
        
        # Filtra as vendas com base no termo de pesquisa
        vendas_filtradas = [
            v for v in vendas
            if termo in v["cliente_nome"].lower()
            or termo in v["data_venda"].lower()
            or termo in v["status"].lower()
            or termo in v["funcionario_nome"].lower()
            or termo in str(v["id"]) # Permite pesquisar pelo ID da venda
        ]

        # Agrupar vendas
        vendas_agrupadas = {}
        for v in vendas_filtradas:
            try:
                # Tenta converter a data para o formato desejado
                data_venda = datetime.datetime.strptime(v["data_venda"], "%d/%m/%Y %H:%M:%S")
            except:
                data_venda = datetime.datetime.now() # Se falhar, usa a data atual

            titulo_dia = f"{data_venda.strftime('%A, %d/%m/%Y')}" # Agrupa por dia da semana e data

            # Adiciona ao agrupamento (pode ser ajustado para só um tipo de agrupamento se preferir)
            if titulo_dia not in vendas_agrupadas:
                vendas_agrupadas[titulo_dia] = []
            vendas_agrupadas[titulo_dia].append(v) # Guarda o índice original e a venda

        # Ordena os grupos por data (do mais recente para o mais antigo)
        dias_ordenados = sorted(vendas_agrupadas.keys(),
                                key=lambda x: datetime.datetime.strptime(x.split(", ")[1],
                                                                         "%d/%m/%Y"), reverse=True)

        # Adiciona os grupos e as vendas à lista_vendas
        if not vendas_agrupadas:
            lista_vendas.controls.append(ft.Text("Nenhuma venda encontrada.", italic=True, color=ft.Colors.GREY))
        else:
            for dia in dias_ordenados:
                lista_vendas.controls.append(
                    ft.Container(
                        content=ft.Text(dia, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                        padding=ft.padding.only(top=15, bottom=5)
                    )
                )
                for v in vendas_agrupadas[dia]:
                    print(f"Adicionando venda para o dia {dia}: {v}") # Para depuração
                    status_color = ft.Colors.GREEN_500 if v["status"] == "Concluída" else \
                                   ft.Colors.ORANGE_500 if v["status"] == "Pendente" else \
                                   ft.Colors.RED_500
                    
                    # Usar replace para formatação de moeda brasileira
                    total_formatado = f"R$ {v['total']:.2f}".replace(".", "X").replace(",", ".").replace("X", ",")

                    linha = ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"ID: {v['id']}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800), # Adiciona o ID
                                    ft.Text(f"Cliente: {v['cliente_nome']}", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Total: {total_formatado}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.DEEP_PURPLE_500),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(f"Status: {v['status']}", color=status_color),
                                    ft.Text(f"Vendedor: {v['funcionario_nome']}", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Data: {v['data_venda']}"), # Mantém a data completa aqui
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            icon_color=ft.Colors.BLUE,
                                            tooltip="Editar venda",
                                            on_click=editar_venda(v['id']) # Passa o índice da venda
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED,
                                            tooltip="Excluir venda",
                                            on_click=excluir_venda(v['id']) # Passa o índice da venda
                                        ),
                                    ])
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ])
                        ),
                        elevation=2, # Sombra para destacar o card
                        color=ft.Colors.WHITE, # Fundo do card
                    )
                    lista_vendas.controls.append(linha)
                    lista_vendas.controls.append(ft.Divider(height=5, color=ft.Colors.TRANSPARENT)) # Espaçamento entre cards
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Exclusão"),
        content=ft.Text("Você tem certeza que deseja excluir esta venda?"),
        actions=[
            ft.TextButton("Confirmar", on_click=confirmar_exclusao),
            ft.TextButton("Cancelar", on_click=cancelar_exclusao)
        ]
    )
    page.overlay.append(confirm_dialog)

    # --- Função de Download ---
    def _pick_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            folder_path.value = e.path
            folder_path.update()
            
            # Obtém o tipo de relatório selecionado
            report_type = report_type_dropdown.value

            df = pd.DataFrame(vendas)
            
            # Converte a coluna 'data' para datetime
            df['data_dt'] = pd.to_datetime(df['data'].str.split(' ').str[0], format='%d/%m/%Y')
            
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_vendas_{report_type.lower()}_{current_time}.csv"
            full_path = os.path.join(e.path, filename)

            if report_type == "Diário":
                today = datetime.date.today()
                df_filtered = df[df['data_dt'].dt.date == today]
            elif report_type == "Semanal":
                # Pega o início da semana atual (segunda-feira)
                today = datetime.date.today()
                start_of_week = today - datetime.timedelta(days=today.weekday())
                end_of_week = start_of_week + datetime.timedelta(days=6)
                df_filtered = df[(df['data_dt'].dt.date >= start_of_week) & (df['data_dt'].dt.date <= end_of_week)]
            elif report_type == "Mensal":
                today = datetime.date.today()
                start_of_month = datetime.date(today.year, today.month, 1)
                # Calcula o último dia do mês
                if today.month == 12:
                    end_of_month = datetime.date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    end_of_month = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
                df_filtered = df[(df['data_dt'].dt.date >= start_of_month) & (df['data_dt'].dt.date <= end_of_month)]
            else: # Todos
                df_filtered = df.copy()
                filename = f"relatorio_vendas_completo_{current_time}.csv"
                full_path = os.path.join(e.path, filename)

            # Remove a coluna temporária de data
            df_filtered = df_filtered.drop(columns=['data_dt'])
            
            if not df_filtered.empty:
                try:
                    df_filtered.to_csv(full_path, index=False, sep=';', decimal=',') # Separador ; e decimal ,
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Relatório '{report_type}' exportado para: {full_path}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN_700
                    )
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Erro ao exportar relatório: {ex}", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED_700
                    )
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Não há vendas para o período '{report_type}'.", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_700
                )
            page.snack_bar.open = True
            page.update()

        download_dialog.open = False
        page.update()

    folder_path = ft.Text("Nenhuma pasta selecionada")
    file_picker = ft.FilePicker(on_result=_pick_folder_result)
    page.overlay.append(file_picker)
    report_type_dropdown = ft.Dropdown(
        label="Tipo de Relatório",
        options=[
            ft.dropdown.Option("Diário"),
            ft.dropdown.Option("Semanal"),
            ft.dropdown.Option("Mensal"),
            ft.dropdown.Option("Todos")
        ],
        value="Diário",
        width=200
    )

    download_dialog = ft.AlertDialog(
        modal=True,
            title=ft.Text("Baixar Relatório de Vendas"),
            content=ft.Column([
                ft.Text("Escolha o tipo de relatório e a pasta de destino."),
                report_type_dropdown,
                ft.Row([
                    ft.ElevatedButton(
                        "Selecionar Pasta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda _: file_picker.get_directory_path()
                    ),
                    folder_path,
                ]),
            ], tight=True),
            actions=[
                ft.TextButton("Baixar", on_click=lambda e: _pick_folder_result(ft.FilePickerResultEvent(path=folder_path.value))),
                ft.TextButton("Cancelar", on_click=lambda e: (setattr(download_dialog, 'open', False), page.update())),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    page.overlay.append(download_dialog)

    def abrir_dialog_download(e):
        download_dialog.open = True
        page.update()

    # --- Inicialização da View ---
    # Inicia a tarefa do relógio apenas uma vez por View
    import asyncio # Garante que asyncio esteja importado
    if not _clock_task_vendas or _clock_task_vendas.done():
        _clock_task_vendas = page.run_task(atualiza_tempo_vendas)
        print("Tarefa atualiza_tempo iniciada (Vendas).")

    # Garante que a lista é atualizada ao entrar na página
    page.on_ready = lambda: atualizar_lista()

    return ft.View(
        route="/vendas",
        appbar=ft.AppBar(
            title=ft.Text("Vendas Registradas", color=ft.Colors.WHITE),
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=voltar_home
            ),
            actions=[
                hora_atual, # Relógio na AppBar
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Baixar Relatório",
                        on_click=abrir_dialog_download
                    ),
                    bgcolor=ft.Colors.BLUE_500, # Cor para o botão de download
                    border_radius=5,
                    padding=ft.padding.all(5)
                )
            ],
            bgcolor=ft.Colors.BLUE_700, # Cor da AppBar igual ao cadastro
            automatically_imply_leading=False # Controle o leading manualmente
        ),
        floating_action_button=ft.FloatingActionButton(
            text="Registrar Venda",
            icon=ft.Icons.POINT_OF_SALE,
            bgcolor="#4990fc", # Mesma cor da AppBar
            on_click=ir_para_cadastro_vendas # Usa a nova função
        ),
        # Posição do FAB: bottom-left
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT, # Agora END_FLOAT ou START_FLOAT
        
        controls=[
            ft.Container(
                content=ft.Column([
                    pesquisa,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT), # Espaçamento
                    # A lista de vendas está dentro de um Container para controlar a rolagem
                    ft.Container(
                        content=lista_vendas,
                        expand=True, # Faz com que o container da lista preencha o espaço
                        padding=ft.padding.only(left=10, right=10), # Um pouco de padding lateral
                        #scroll=ft.ScrollMode.AUTO # Garante que a lista interna role se necessário
                    )
                ], expand=True), # A coluna principal também se expande
                padding=ft.padding.all(20), # Padding geral para o conteúdo principal
                expand=True,
            )
        ],
        bgcolor=ft.Colors.BLUE_500, # Cor de fundo da View
        scroll=ft.ScrollMode.AUTO, # Rolagem geral da View se necessário
    )