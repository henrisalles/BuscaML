import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from unidecode import unidecode


def confere_nome_produto(produto_nome: str, palavras_chave: list[str], palavras_chave_exclusora: list[str]):
    produto_nome = unidecode(produto_nome)

    x = True
    for palavra in palavras_chave:
        palavra = unidecode(palavra)
        if palavra.lower() not in produto_nome.lower().split():
            x = False
            break
    if palavras_chave_exclusora:
        for palavra in palavras_chave_exclusora:
            palavra = unidecode(palavra)
            if palavra.lower() in produto_nome.lower().split():
                x = False
                break
    return x


def classifica_produto(search_frame, palavras_chave, palavras_chave_exclusora):
            '''
            Le os produtos da pagina e retorna um DataFrame com as informacoes
            :param search_frame:
            :return:
            '''
            df = pd.DataFrame(
                columns=['nome_produto', 'preco_produto', 'quantidade', 'vendedor','cor', 'frete_gratis', 'img_produto',
                         'link_produto'])
            for prod in search_frame:
                produto_nome = prod.find('h2', class_="ui-search-item__title").text
                if confere_nome_produto(produto_nome, palavras_chave, palavras_chave_exclusora):
                    raw_produto_preco = prod.find('span', class_='andes-money-amount__fraction').text
                    url_img_produto = prod.find('img', class_='ui-search-result-image__element')['data-src']
                    link_produto = prod.find('a', class_='ui-search-link')['href']

                    quantidade, vendedor, cor = ler_pag_produto(link_produto)
                    # Pode dar erro em valores sem centavos
                    try:
                        raw_produto_preco_cents = prod.find('span', class_='andes-money-amount__cents--superscript-24').text
                        produto_preco = raw_produto_preco + ',' + raw_produto_preco_cents
                    except:
                        produto_preco = raw_produto_preco

                    try:
                        if prod.find('span', class_='ui-search-item__group__element ui-search-installments ui-search-color--LIGHT_GREEN'):
                            tipo_anuncio = 'Premium'
                        else:
                            tipo_anuncio = 'Clássico'
                    except:
                        tipo_anuncio = 'Clássico'

                    # Pode dar erro se sem Frete Gratis
                    try:
                        raw_frete_gratis = prod.find('span', class_='ui-pb-highlight').text
                        if raw_frete_gratis == 'Frete grátis':
                            frete = 1
                        else:
                            frete = 0
                    except:
                        frete = 0

                    # Poda dar erro se sem Entrega Full
                    try:
                        raw_full = prod.find('svg', class_='ui-pb-icon ui-pb-icon--full')
                        if raw_full:
                            tipo_anuncio = 'Full'
                    except:
                        pass

                    novo_produto = pd.DataFrame({'nome_produto': [produto_nome],
                                                 'preco_produto': [produto_preco],
                                                 'tipo_anuncio': [tipo_anuncio],
                                                 'quantidade': [quantidade],
                                                 'vendedor': [vendedor],
                                                 'cor': [cor],
                                                 'frete_gratis': [frete],
                                                 'img_produto': [url_img_produto],
                                                 'link_produto': [link_produto]})
                    df = pd.concat([df, novo_produto], ignore_index=True)
            return df


def ler_pag_produto(url):
    '''
    Le a pagina de anuncio do produto
    :param url: url do produto/anuncio
    :return: quantidade, vendedor, cor
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        vendedor = soup.find('div', class_='ui-pdp-seller__header__title').text
        if vendedor[:len('Vendido por')] == 'Vendido por':
            vendedor = vendedor.removeprefix('Vendido por')
        elif vendedor[:len('Loja oficial')] == 'Loja oficial':
            vendedor = vendedor.removeprefix('Loja oficial')
        else:
            pass
    except:
        vendedor = None

    try:
        quantidade = soup.find('span', class_='ui-pdp-buybox__quantity__available').text
        quantidade = re.findall(r'\d+', quantidade)
        quantidade = quantidade[0]

    except:
        quantidade = 1

    try:
        cor = soup.find('span', class_='ui-pdp-variations__selected-label ui-pdp-color--BLACK').text.lower()
    except:
        cor = None

    try:
        cor = cor.split('/')[0]
        cor = cor.split('-')[0]
        cor = cor.split(' ')[0]
        cor = cor.split('+')[0]
        cor = cor.split(',')[0]
    except:
        pass

    if cor == 'pto' or cor == 'pta' or cor == 'preta':
        cor = 'preto'
    elif cor == 'bco' or cor == 'bca' or cor == 'branca':
        cor = 'branco'
    elif cor == 'vde' or cor == 'lim' or cor == 'lima' or cor == 'limão':
        cor = 'verde'

    return quantidade, vendedor, cor


def ler_pagina(url: str, palavras_chave: list[str], palavras_chave_exclusora: list[str]=None):
    '''
    Le a pagina URL e retorna um DataFrame com os principais valores do anuncio
    :param url: url da pagina
    :param palavras_chave: palavras chave que irão excluir os produtos cujo no nome não contenham TODAS estas palavras
    :param palavras_chave_exclusora: palavras chave que se encontradas no nome do produto excluem da pesquisa
    :return: DataFrame
    '''

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrapping do produto
    search_frame = soup.find_all('li', class_="ui-search-layout__item")

    # Limitando Frame de Busca
    search_frame = search_frame[:40]

    # Multiprocessamento
    n_processos = 16

    lista_frames = [search_frame[i * len(search_frame) // n_processos:(i+1)*len(search_frame)//n_processos]
                    for i in range(n_processos)]

    with ThreadPoolExecutor(max_workers=n_processos) as executor:
        futures = []
        for frame in lista_frames:
            futures.append(executor.submit(classifica_produto,
                                           search_frame=frame,
                                           palavras_chave=palavras_chave,
                                           palavras_chave_exclusora=palavras_chave_exclusora))

        novo_df = pd.DataFrame(columns=['nome_produto', 'cor', 'preco_produto', 'quantidade', 'tipo_anuncio', 'vendedor',
                                        'frete_gratis', 'img_produto', 'link_produto'])
        for future in as_completed(futures):
            novo_df = pd.concat([novo_df, future.result()], ignore_index=True)

    print("Pagina Lida com Sucesso ...")
    return novo_df
