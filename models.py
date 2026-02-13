class Produto:
    def __init__(self, nome_produto, valor_total, forma_pagamento, parcelamento, link_produto):
        self.nome_produto = str(nome_produto[:100])
        self.valor_total = float(valor_total)
        self.forma_pagamento = str(forma_pagamento[:100])
        self.parcelamento = int(parcelamento.split(" ")[1].strip().replace("x", ""))
        self.link_produto = str(link_produto[:200])

