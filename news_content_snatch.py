import bs4 as bs
import urllib2 as request
import os

URL_HEAD = 'http://www.bbc.com'


def get_full_content(link, silent=True, use_full_link=False):
    content_local = 'news/'
    full_link = URL_HEAD + link
    if use_full_link:
        full_link = link
    try:
        sauce = request.urlopen(full_link).read()
    except request.URLError:
        if not silent:
            print 'Error encountered at {}'.format(link)
        return
    soup = bs.BeautifulSoup(sauce, 'lxml')
    news_body = soup.body

    article = news_body.find('div', {'property': 'articleBody'})
    paragraphs = []
    try:
        ps = article.find_all(['p', 'h2'])
    except AttributeError:
        return
    for paragraph in ps:
        paragraphs.append(paragraph.get_text() + ' ')
    news_title = link.split('/')[2]
    news_path = content_local + news_title

    if not os.path.isfile(news_path):
        with open(news_path, 'w') as writer:
            for p in paragraphs:
                writer.write(p.encode('utf8'))
        if not silent:
            print 'news entry {} added'.format(news_title)
    else:
        if not silent:
            print 'news {} already in file'.format(news_title)


def scrape_page(link, silent=True, use_full_link=False):
    full_link = URL_HEAD + link
    if use_full_link:
        full_link = link
    try:
        sauce = request.urlopen(full_link).read()
    except request.URLError:
        print '404'
        return
    soup = bs.BeautifulSoup(sauce, 'lxml')
    page_body = soup.body

    for article_link in page_body.find_all('a', {'class': ['gs-c-promo-heading',
                                                           'title-link',
                                                           'faux-block-link__overlay-link']}):
        if article_link.get('href').split('/')[1] == 'newyddion':
            continue
        try:
            get_full_content(article_link.get('href'), silent)
        except request.URLError:
            print 'Error encountered at {}'.format(link)
            continue


def scrape(link='/news', mode='specified', silent=True):
    """
    scrapes the specified the topic link when the mode argument is set to 'specified'
    alternatively, when the mode argument is set to 'full', the link argument will be ignored
    and the full site that includes all topics wil be scraped
    :param silent: 
    :param link: 
    :param mode: 
    :return: 
    """
    if mode == 'specified':
        scrape_page(link, silent)
    elif mode == 'full':
        topic_dict = get_nav_links()
        for topic, sub_topics in topic_dict.iteritems():

            scrape_page(topic, silent)
            if not sub_topics == []:
                for sub in sub_topics:
                    scrape_page(sub, silent)
    else:
        print '{} is not an option'.format(mode)


def get_nav_links():
    """
    find all topics and sub-topics on the bbc news site
    :return: a dict of all topics, the dict follows a structure like 
    {_link_to_topic_: _link_to_sub_topics_}
    """
    sauce = request.urlopen(URL_HEAD + '/news').read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    body = soup.body
    nav = body.find('div', class_='navigation--wide')

    nav_links = {}

    for topic in nav.find_all('a'):
        topic_link = topic.get('href')

        if topic_link == '/news/video_and_audio/headlines':
            continue

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
            if sub_topic_link == 'http://www.bbc.co.uk/news/business/market_data' \
                    or sub_topic_link == '/news/business/markets':
                continue
            sub_links.append(sub_topic_link)

        nav_links[topic_link] = sub_links
    return nav_links


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', dest='mode', default='specified', type=str)
    parser.add_argument('--link', dest='link', default='/news', type=str)
    verbose_parser = parser.add_mutually_exclusive_group()
    verbose_parser.add_argument('--verbose', dest='silent', action='store_false')
    verbose_parser.add_argument('--silent', dest='silent', action='store_true')
    parser.set_defaults(silent=True)

    args = parser.parse_args()
    scrape(link=args.link, mode=args.mode, silent=args.silent)
