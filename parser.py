from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
import json


@dataclass
class Parser:
    web: str
    website: str  # url to visit
    page_limit: int = 5  # default limit page to search

    def get_settings(self):
        with open('settings.json') as settings:
            data = json.load(settings)
            web_object = {}
            web_object['soup_tag'] = data[self.web][0]['soup_tag']
            web_object['next_page_path'] = data[self.web][0]['next_page_path'] # noqa
            web_object['starts_with'] = data[self.web][0]['starts_with']
            web_object['next_page_index'] = data[self.web][0]['next_page_index'] # noqa
            web_object['price_tag'] = data[self.web][0]['price_tag']
            web_object['price_class'] = data[self.web][0]['price_class']
            web_object['coin_tag'] = data[self.web][0]['coin_tag']
            web_object['coin_class'] = data[self.web][0]['coin_class']

            print(web_object)
            return web_object

    def get_link_data(self, link, webObject):
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        price = soup.find(webObject['price_tag'], class_=webObject['price_class']).get_text() # noqa
        print('price', price)
        coin = soup.find(webObject['coin_tag'], class_=webObject['coin_class']).get_text()# noqa
        return [coin, price]

    def url_search_list(self, webObject):
        next_pages = [self.website]
        # refactor names
        page_args = webObject['next_page_path']
        index = webObject['next_page_index'] + 1
        i = 0

        while i < self.page_limit:
            next_pages.append(self.website + page_args + str(index))
            index = index + webObject['next_page_index']
            i += 1

        return next_pages

    def extract_links(self):
        data = {}
        data['link_list'] = []
        webObject = self.get_settings()
        pages = self.url_search_list(webObject)

        for url in pages:
            print('parsing for ', url)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            # get all the links from the page in <soup_tag /> tags
            links = soup.find_all(webObject['soup_tag'])
            outfile = open('data.json', 'w')
            dict1 = {}
            for link in links:
                current_url = link.get('href')
                try:
                    if current_url.startswith(webObject['starts_with']):
                        if(self.web == 'argen_prop'):
                            current_url = 'https://www.argenprop.com' + current_url # noqa
                        print(current_url)
                        link_data = self.get_link_data(current_url, webObject)
                        dict1[hash(current_url)] = {
                                'url': current_url,
                                'coin': link_data[0],
                                'price': link_data[1],
                                }
                        print("--", current_url)
                except: # noqa
                    pass
            json.dump(dict1, outfile)


@dataclass
class Parser_Zonaprops:
    website: str
    soup_tag: str  # html tag to extract links
    page_limit: int = 5  # default limit page to search
    zona: str = 'capital-federal.html'
    next_page_tag: str = '-pagina-'

    def url_search_list(self):
        pages = [self.website + '-q-' + self.zona]
        i = 2
        while i < self.page_limit:
            page = (self.website + self.next_page_tag + str(i) + '-q-' + self.zona) # noqa
            pages.append(page)
            i += 1
        return pages

    def extract_links(self):
        data = {}
        data['link_list'] = []
        pages = self.url_search_list()

        for url in pages:
            print('parsing ', url)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            # get all the links from the page in <soup_tag /> tags
            links = soup.find_all('div') # noqa
            print(links)
            print("flag")
            # for link in links:
            #    current_url = link
            #    try:
            #        print(current_url)
            #    except: # noqa
            #        pass
