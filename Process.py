import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from Url import URL
from Leitor_paginas import ler_pagina
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


def process(nome_produto:str, palavras_chave:list, palavras_chave_exclusora:list, progress, lbl, arquivo_padrao):

    tempo_inicio = time.time()

    total_paginas = 20


    def catch_search_url(nome_produto:str):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)

        driver.get('https://www.mercadolivre.com.br/')
        time.sleep(4)
        try:
            search = driver.find_element(by='xpath', value=r'//*[@id="cb1-edit"]')
        except:
            time.sleep(2)
            search = driver.find_element(by='xpath', value=r'//*[@id="cb1-edit"]')

        search.send_keys(nome_produto)
        search.send_keys(Keys.ENTER)
        time.sleep(0.25)

        # Aceitar Cookies
        try:
            driver.find_element('xpath', '/html/body/div[2]/div[1]/div/div[2]/button[1]').click()
        except:
            pass

        driver.find_element('xpath', r'//*[@id="root-app"]/div/div[3]/section/nav/ul/li[3]/button').click()
        time.sleep(0.25)
        return URL(driver.current_url)

    object_url = catch_search_url(nome_produto)
    progress.set(0.05)
    lbl.set('URL pega com sucesso ...')
    print('URL pega com sucesso ...')
    df = pd.DataFrame(columns=['nome_produto','cor', 'preco_produto', 'tipo_anuncio', 'quantidade', 'vendedor',
                               'frete_gratis', 'img_produto', 'link_produto'])

    if total_paginas <= 4:
        max_workers = total_paginas
    else:
        max_workers = 4

    # Criar urls
    lista_urls = []
    for i in range(total_paginas):
        lista_urls.append(object_url.ajuste_url(i*40))
    progress.set(0.1)
    lbl.set('Criada Lista de URLs ...')
    print('Criada Lista de URLs ...')

    # Multiprocessing
    var = 0.1
    i = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url in lista_urls:
            futures.append(executor.submit(ler_pagina,
                                           url=url,
                                           palavras_chave=palavras_chave,
                                           palavras_chave_exclusora=palavras_chave_exclusora))

        for future in as_completed(futures):
            var += 0.04
            i += 1
            progress.set(var)
            lbl.set(f'Paginas Lidas: {i} de {total_paginas}')
            df = pd.concat([df, future.result()], ignore_index=True)

    lbl.set(f'Todas Páginas Lidas com Sucesso, tempo: {time.time() - tempo_inicio}\n '
            f'Seu Arquivo Excel já foi atualizado!')
    print(f'Todas Páginas Lidas com Sucesso, tempo: {time.time() - tempo_inicio}')

    # Retirando duplicatas
    df = df.drop_duplicates(['link_produto'])
    df = df.drop_duplicates(['nome_produto', 'preco_produto', 'quantidade', 'vendedor', 'frete_gratis',
                             'cor', 'tipo_anuncio'])
    if not arquivo_padrao:
        nome_arquivo = f"pesquisaML_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    else:
        nome_arquivo = 'resultado_programa.xlsx'
    df.to_excel(nome_arquivo)
    progress.set(1)
    print(time.time() - tempo_inicio)
