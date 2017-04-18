import bs4 as bs
import urllib2 as request
import os

URL_HEAD = 'http://www.bbc.com'


def get_full_content(link):
    content_local = 'news/'
    try:
        sauce = request.urlopen(URL_HEAD + link).read()
    except request.HTTPError:
        print '404 encountered'
        return
    soup = bs.BeautifulSoup(sauce, 'lxml')
    news_body = soup.body

    article = news_body.find('div', {'property': 'articleBody'})
    paragraphs = []
    for paragraph in article.find_all(['p', 'h2']):
        paragraphs.append(paragraph.get_text())
    news_path = content_local + link.split('/')[2]

    if not os.path.isfile(news_path):
        with open(news_path, 'w') as writer:
            for p in paragraphs:
                writer.write(p.encode('utf8'))
        print 'news entry added'


def get_nav_links():
    sauce = request.urlopen(URL_HEAD + '/news').read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    body = soup.body
    nav = body.find('div', class_='navigation--wide')

    nav_links = {}

    for topic in nav.find_all('li'):
        if topic.get('class') == ' invisible':
            break
        topic_link = topic.find('a').get('href')

        if topic_link == '/news/video_and_audio/headlines':
            continue
        if topic_link == '/news/magazine':
            break

        sauce = request.urlopen(URL_HEAD + topic_link).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        body = soup.body

        try:
            sub_nav = body.find('nav', class_='navigation-wide-list--secondary').find('ul')
        except AttributeError:
            nav_links[topic_link] = []
            continue
        if sub_nav is None:
            nav_links[topic_link] = []
            continue

        sub_links = []
        for sub_topic in sub_nav.find_all('li', class_=None):
            sub_topic_link = sub_topic.find('a').get('href')
            if sub_topic_link == 'http://www.bbc.co.uk/news/business/market_data'\
                    or sub_topic_link == '/news/business/markets':
                continue
            sub_links.append(sub_topic_link)

        nav_links[topic_link] = sub_links
    return nav_links
