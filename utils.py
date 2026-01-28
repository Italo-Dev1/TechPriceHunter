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
