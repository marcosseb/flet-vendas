# src/utils.py
import csv
import os

def exportar_para_csv(lista_produtos, caminho):
    campos = lista_produtos[0].keys() if lista_produtos else []
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(lista_produtos)


def formatar_cnpj(cnpj: str) -> str:
    # Formata o CNPJ no padrão 00.000.000/0000-00
    cnpj = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def formatar_telefone(telefone: str) -> str:
    # Formata telefone no padrão (00) 00000-0000
    telefone = ''.join(filter(str.isdigit, telefone))
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return 





