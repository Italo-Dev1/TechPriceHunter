import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
def limpa_texto(texto: str, caracteres: list[str]) -> str:
    for c in caracteres:
        texto = texto.replace(c, "")
    return texto

def moeda_para_float(valor: str | None) -> float | None:
    if not valor:
        return None
    try:
        return float(
            valor.replace("R$", "")
                 .replace("\xa0", "")
                 .replace(".", "")
                 .replace(",", ".")
                 .strip()
        )
    except ValueError:
        return None

def converte_texto(element, selector, default="ESGOTADO"):
    tag = element.select_one(selector)
    return tag.text if tag else default


def formata_valor_excel(ws=None):
    for cell in ws["C"][1:]:
        if isinstance(cell.value, (int, float)):
            cell.number_format = 'R$ #,##0.00'



def abre_conexao_bd(logging):
    cur = None
    conn = None
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
        cur = conn.cursor()
        logging.info("Aberto Conexão com o banco de dados.")
    except:
        logging.alert("Erro ao abrir conexão com o banco de dados.")
    return cur, conn


def fecha_conexao_bd(cur, conn, logging):
    try:
        if cur:
            cur.close()
        if conn:
            conn.close()
        logging.info("Conexão com o banco de dados encerrada.")
    except Exception as e:
        logging.error(f"Erro ao fechar conexão: {e}")

def grava_item_banco(cur, conn, logging, obj_produto):
    try:
        produto_existe = verifica_item_banco(cur, logging, obj_produto)

        if produto_existe:
            logging.info(f"Produto já existe no banco: {obj_produto.nome_produto}")
            return False

        cur.execute("""
            INSERT INTO core_produto
            (nome, valor_total, forma_de_pagamento, parcelamento, link_produto)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            obj_produto.nome_produto,
            obj_produto.valor_total,
            obj_produto.forma_pagamento,
            obj_produto.parcelamento,
            obj_produto.link_produto
        ))

        conn.commit()
        logging.info(f"Produto inserido com sucesso: {obj_produto.nome_produto}")
        return True

    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao gravar no banco: {e}")
        return False




def verifica_item_banco(cur, logging, obj_produto):
    try:
        cur.execute("""
            SELECT 1
            FROM core_produto
            WHERE nome = %s
              AND forma_de_pagamento = %s
              AND valor_total = %s
              AND parcelamento = %s
              AND link_produto = %s
        """, (
            obj_produto.nome_produto,
            obj_produto.forma_pagamento,
            obj_produto.valor_total,
            obj_produto.parcelamento,
            obj_produto.link_produto
        ))

        return cur.fetchone() is not None

    except Exception as e:
        logging.error(f"Erro ao verificar produto no banco: {e}")
        return False

