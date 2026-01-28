import logging
import os
import pandas as pd
from datetime import datetime
from browser import cria_driver, fecha_navegador
from kabum import coleta_kabum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(
                        os.path.join(rf"{os.getcwd()}\Logs",
                                     f"log_erros_tech_price_hunter_{datetime.now().strftime('%d-%m-%Y')}.txt"))])



produto_alvo = input("Digite o nome do produto que deseja: ")
gerar_excel = input("""Deseja gerar excel com os todos os produtos? Digite: 'S' para "Sim" e 'N' para "Não": """)
if gerar_excel != 'S' and  gerar_excel != 'N':
    print("Selecione uma opção válida para o arquivo em Excel.")
else:
    driver = cria_driver(headless=True)
    if driver:
        try:
            lista_produtos_kabum = []
            caminho_excel = rf"{os.getcwd()}\Dados produtos em excel\extracao_dados_excel_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.xlsx"
            retorno_kabum = coleta_kabum(driver=driver, produto_alvo=produto_alvo, lista_produtos_kabum=lista_produtos_kabum)
            if not retorno_kabum:
                logging.info("Erro ao buscar produto no site da Kabum")

            try:
                if gerar_excel == 'S':
                    colunas_excel_kabum = ["NOME_PRODUTO","FORMA_PAGAMENTO","VALOR_TOTAL","PARCELAMENTO","LINK_PRODUTO"]

                    with pd.ExcelWriter(caminho_excel, engine="openpyxl") as writer:

                        escreveu_algo = False

                        if lista_produtos_kabum:
                            df_kabum = pd.DataFrame(lista_produtos_kabum, columns=colunas_excel_kabum)

                            df_kabum.to_excel(writer, sheet_name="Produtos_Kabum", index=False)
                            ws = writer.sheets["Produtos_Kabum"]

                            for cell in ws["C"][1:]:
                                if isinstance(cell.value, (int, float)):
                                    cell.number_format = 'R$ #,##0.00'
                            escreveu_algo = True

                        if not escreveu_algo:
                            pd.DataFrame(
                                {"Info": ["Nenhum produto encontrado"]}
                            ).to_excel(
                                writer,
                                sheet_name="Resultado",
                                index=False
                            )
            except Exception as e:
                logging.info(f"Erro ao gerar Excel: {e}")
        finally:
            fecha_navegador(driver)