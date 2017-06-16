from io import StringIO
from urllib.parse import urlparse

import requests
from lxml.html import parse


class BaseCrawler:
    def __init__(self, start_url, **kwargs):
        self.start_url = start_url
        self.queue = {start_url}
        self.allowed_hosts = {urlparse(start_url).netloc}
        self.allowed_hosts.add(
            kwargs.get('allowed_hosts', set())
        )
        self.add_empty = kwargs.get('add_empty', False)
        self.visited = set()
        self.session = requests.session()
        self.result = dict()
        self.not200 = set()
        self.main_loop()

    def get_links(self, lxml_document):
        return {link for el, attr, link, _ in lxml_document.iterlinks()
                if all([el.tag == 'a', urlparse(link).netloc, urlparse(link).netloc in self.allowed_hosts])}

    def main_loop(self):
        while self.queue:
            current_url = self.queue.pop()
            print(current_url)
            res = self.session.get(current_url)

            if res.status_code == 200:
                doc = parse(StringIO(res.text)).getroot()
                link_data = urlparse(current_url)
                doc.make_links_absolute(link_data.scheme + "://" + link_data.netloc)
                self.visited.add(current_url)

                # соберем все ссылки со страницы
                a_hrefs = self.get_links(doc)

                # в r1 положим ссылки которые еще не посещали
                r1 = a_hrefs.difference(self.visited)

                # сравним со ссылками которые стоят в очереди
                r1 = r1.difference(self.queue)

                # добавим те ссылки которых нет ни в очереди, ни в посещенных
                self.queue.update(r1)
                # вызов функции которую должен переопределить пользователь
                wrk_result = self.do_work(doc)

                # в self.result добавим результат работы do_work()
                if self.add_empty:
                    self.result[current_url] = wrk_result
                elif wrk_result:
                    self.result[current_url] = wrk_result
            else:
                # в это множество будем сохранять страницы с кодом отличным от 200
                self.not200.add((current_url, res.status_code))

    def do_work(self, lxml_doc):
        pass
