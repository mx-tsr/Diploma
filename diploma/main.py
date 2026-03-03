import os
import requests
import time


''' To DO:
Идея, что сейчас нужно сделать:
1. Получить релевантную статью по заданной теме
2. По ее ID скачать ее и сохрнаить в папку
3. Извлечь из PDF текст и сохранить его в txt файл

4. Собрать все тексты статей в txt файлы (не json?)
5. Подумать, как сформировать промпт, в который можно будет подавать много текста, возможно текст одной статьи - это много. 
Как сделать так, чтобы ллм не забывала контекст и делала итеративно лучше. 
6. Сделать промпт, который будет доставать ключевую информацию из статей и сохранять в json файл.
7. Мета-анализ + Формирование json с мыслями?
8. Сделать промпт, который будет анализировать мысли, делать мета-анализ и остальное, что я закладывал
9. Засовывания идей в промпт и генерация обзора.  

P.S. Насчет того, что писать в результатах. Возможно сравнивать не просто с ручным анализом, а с ручным анализом + обращение к нейронке.
Плюсом описать, почему агенты круче, чем такой подход (такие статьи есть). 
'''

# def get_paper(paper_id: str, fields):
#     params = {
#         'fields': fields
#     }
#     headers = {}

#     response = requests.get(
#     f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}',
#     headers=headers,
#     params=params
#     )

#     response.raise_for_status()
#     time.sleep(1.0)
#     return response.json()


def download_pdf(url, path, user_agent = 'requests/2.0.0'):
    # send a user-agent to avoid server error
    headers = {
        'user-agent': user_agent,
    }

    # stream the response to avoid downloading the entire file into memory
    response = requests.get(
        url, 
        headers=headers, 
        stream=True, 
    verify=False)

    response.raise_for_status()

    if response.headers['content-type'] != 'application/pdf':
        raise Exception('The response is not a pdf')

    with open(path, 'wb') as f:
        # write the response to the file, chunk_size bytes at a time
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def download_paper(paper, directory='papers', user_agent='requests/2.0.0'):

    if not paper.get('isOpenAccess'):
        return None
    
    open_access = paper.get('openAccessPdf')

    if not open_access or not open_access.get('url'):
        return None

    paperId = paper['paperId']
    pdf_url = open_access['url']
    pdf_path = os.path.join(directory, f'{paperId}.pdf')

    # create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # check if the pdf has already been downloaded
    if not os.path.exists(pdf_path):
        download_pdf(pdf_url, pdf_path, user_agent=user_agent)

    return pdf_path


def search_for_papers(query, result_limit=15):
    if not query:
        return None
    response = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        headers={},
        params={
            "query": query,
            "limit": result_limit,
            "fields": "paperId,title,abstract,isOpenAccess,openAccessPdf,externalIds",
            "isOpenAccess": True
        },
    )
    response.raise_for_status()
    results = response.json()
    time.sleep(2.0)
    papers = results["data"]
    return papers


query = 'science automation using agentic systems'
papers = search_for_papers(query)
print(papers)

# for paper in papers:
#     try:
#         result = download_paper(paper)
#     except Exception as e:
#         print(f'Error downloading paper {paper["paperId"]}: {e}')
