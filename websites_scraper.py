import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from requests_html import HTMLSession

def get_mof_faq():
    url = 'https://www.mof.gov.my/portal/ms/berita/soalan-lazim/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    df = pd.DataFrame(columns=['url', 'question', 'answer'])
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        faqs = soup.find_all('a', string=lambda text: text and "Soalan Lazim" in text)
        faq_links = [faq['href'] for faq in faqs if 'hubungi' not in faq['href']]
        for link in  faq_links:
            faq_url = 'https://www.mof.gov.my' + link
            faq_response = requests.get(faq_url, headers=headers)
            if faq_response.status_code == 200:
                soup2 = BeautifulSoup(faq_response.content, 'html.parser')
                # Find all <button> tags
                qna = soup2.find_all('div', class_='sppb-panel sppb-panel-custom')
                # Extract the text from the <span> tags with class "sppb-panel-title" if they exist
                for item in qna:
                    span = item.find('span', class_='sppb-panel-title')
                    if span:
                        question = span.get_text()
                    paragraph = item.find('p')
                    if paragraph:
                        answer = paragraph.get_text()
                    else: 
                        paragraph = item.find('div', class_='sppb-addon sppb-addon-text-block')
                        answer = paragraph.get_text()
                    df = pd.concat([df, pd.DataFrame({'url': [faq_url], 'question': [question], 'answer': [answer]})])
            else:
                print(f"Failed to retrieve the page {faq_url}. Status code: {response.status_code}")
        df.to_csv('soalan_lazim.csv', index=False)
    else:
        print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")


def get_mof_media():
    url = 'https://www.mof.gov.my/portal/ms/arkib3/siaran-media?catid[0]=9&catid[1]=17&start=30'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    df = pd.DataFrame(columns=['url', 'article'])
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        medias = soup.find_all('div', class_='row0') + soup.find_all('div', class_='row1') 
        media_urls = [media.find('a')['href'] for media in medias]
        for link in  media_urls:
            media_url = 'https://www.mof.gov.my' + link
            media_response = requests.get(media_url, headers=headers)
            if media_response.status_code == 200:
                soup2 = BeautifulSoup(media_response.content, 'html.parser')
                article = soup2.find('div', itemprop='articleBody')
                df = pd.concat([df, pd.DataFrame({'url': [media_url], 'article': [article.get_text()]})])
            else:
                print(f"Failed to retrieve the page {media_url}. Status code: {media_response.status_code}")
        df.to_csv('siaran_media.csv', index=False)
    else:
        print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")


def search_the_edge(keyword):
    keyword = keyword.replace(' ','%20')
    today = datetime.today().strftime('%Y-%m-%d')
    session = HTMLSession()
    df = pd.DataFrame(columns=['url', 'title', 'article'])
    url = f"https://theedgemalaysia.com/news-search-results?keywords={keyword}&to={today}&from=1999-01-01&language=english&offset=0"
    response = session.get(url)
    if response.status_code == 200:
        # Render the JavaScript
        response.html.render(timeout=20)
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.html.html, 'html.parser')
        # Find the news articles
        articles = soup.find_all('div', class_='NewsList_newsListText__hstO7')
        urls = dict()
        for article in articles:
            urls[article.find('span', class_='NewsList_newsListItemHead__dg7eK').get_text()] = article.find('a')['href']
        for title,link in urls.items():
            article_url = 'https://theedgemalaysia.com' + link
            article_response = requests.get(article_url)
            if article_response.status_code == 200:
                soup2 = BeautifulSoup(article_response.content, 'html.parser')
                article = soup2.find('div', class_='news-detail_newsTextDataWrap__PkAu5')
                df = pd.concat([df, pd.DataFrame({'url': [article_url], 'title': [title], 'article': [article.get_text()]})])
            else:
                print(f"Failed to retrieve the page {article_url}. Status code: {article_response.status_code}")
        df.to_csv(f'the_edge_{keyword}.csv', index=False)
    else:
        print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")












