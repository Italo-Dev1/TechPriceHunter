from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
from utils import limpa_texto, moeda_para_float
import logging
import time

url_kabum = "https://www.kabum.com.br"


def troca_pagina_kabum(driver):
    try:
        if not driver.execute_script("""return document.querySelector('a.nextLink')?.ariaDisabled === "true";"""):
            driver.execute_script("document.getElementsByClassName('nextLink')[0].click();")
            WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.ID, "Filter")))
            pg_atual = driver.execute_script("return document.getElementsByClassName('page active')[0].textContent;")
            logging.info(f"Trocando de página. Indo para a página {pg_atual}\n")
        else:
            logging.info("Está é a última página.\n")
    except Exception as erro_encerra_navegador:
        logging.error(f"Erro ao trocar de página: {erro_encerra_navegador}")
        return False
    return True


def coleta_kabum(driver, produto_alvo=None, lista_produtos_kabum=None):
    try:
        logging.info(f"Buscando na kabum, produto: {produto_alvo}")
        driver.get(url_kabum)

        wait = WebDriverWait(driver, 20)

        # Realiza a busca do produto
        wait.until(ec.element_to_be_clickable((By.ID, "inputBusca")))
        campo = driver.find_element(By.ID, "inputBusca")
        campo.clear()
        campo.send_keys(produto_alvo)

        # Clica pra buscar
        driver.execute_script("""document.querySelector('button[data-testid="buttonBuscaKabum"]').click();""")
        try:
            wait.until(ec.presence_of_element_located((By.ID, "Filter")))
        except:
            try:
                msg = driver.find_element(By.ID, "listingEmpty").text
                if "Lamentamos" in msg:
                    logging.info("Nenhum produto encontrado.")
                    return lista_produtos_kabum
            except Exception:
                logging.error("Falha ao validar retorno da busca.")
                return lista_produtos_kabum

        # Ordenação e paginação
        selects = driver.find_elements(By.CSS_SELECTOR, "select")
        Select(selects[0]).select_by_visible_text("Preço crescente")
        Select(selects[1]).select_by_visible_text("100 por página")
        time.sleep(3)

        try:
            # Fecha pesquisa de satisfação
            driver.execute_script("""document.querySelector('dialog').querySelector('button').click();""")
        except:
            pass

        logging.info(f"\n--------------------------------- KABUM ---------------------------------\n")

        paginas = driver.execute_script("""return [...document.querySelectorAll('#listingPagination ul li')].slice(1, -1).length;""")
        pg = 1
        while pg <= paginas:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            produtos = soup.select("article.productCard")
            for produto in produtos:

                nome_produto = produto.select_one("span.nameCard").text
                valor_total = moeda_para_float(produto.select_one("span.priceCard").text)
                fp_valor_total = produto.select_one("div.priceTextCard").contents[0].text
                parcelamento_total = " ".join(produto.select_one("div.priceTextCard").contents[1].text.split(" ")[1::])
                link_produto = f"""{url_kabum}{produto.select_one("a").get("href")}"""

                log_txt = limpa_texto(
                    f"{nome_produto} | {fp_valor_total} | {valor_total} | {parcelamento_total} | {link_produto}",
                    ["–", "\u202f", "\xa0"]
                )
                logging.info(log_txt)

                lista_produtos_kabum.append([
                    nome_produto,
                    fp_valor_total,
                    valor_total,
                    parcelamento_total,
                    link_produto
                ])

            if not troca_pagina_kabum(driver):
                break
            else:
                pg += 1
    except Exception as erro_kabum:
        logging.error(f"Erro ao buscar na kabum: {erro_kabum}")
    return lista_produtos_kabum
