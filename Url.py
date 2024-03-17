import re


class URL:
    def __init__(self, url_inicial: str):
        self.url = url_inicial
        self.inicio_url, self.fim_url = self.separa_url(url_inicial)

    def separa_url(self, url_inicial: str):
        i_desde = re.search('_Desde_', url_inicial).end()
        inicio_url = url_inicial[:i_desde]
        i = 0
        for caractere in url_inicial[i_desde:]:
            if caractere.isdigit():
                i += 1
            else:
                break
        fim_url = url_inicial[i_desde+i:]
        return inicio_url, fim_url

    @property
    def primeiro_ajuste(self):
        return self.inicio_url + '0' + self.fim_url

    def ajuste_url(self, novo_numero: int):
        return self.inicio_url + str(novo_numero) + self.fim_url
