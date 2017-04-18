import bs4 as bs
import urllib2 as request


def get_full_content(link):
    content_local = 'news/'
    head = 'http://www.bbc.com'
    try:
        sauce = request.urlopen(head + link).read()
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
    print news_path
    with open(news_path, 'w') as writer:
        for p in paragraphs:
            print p
            writer.write(p.encode('utf8'))
