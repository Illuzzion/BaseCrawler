import csv

from crawler import BaseCrawler

CSS_SELECTORS = ('.catalog-description_top', '.catalog-description_bottom')


class PCCrawler(BaseCrawler):
    def get_links(self, lxml_document):
        l = super().get_links(lxml_document)
        disallowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tga", ".zip", ".rar", ".pdf"}

        return {link for link in l
                if not any(map(lambda ext: link.lower().endswith(ext), disallowed_ext)) and "?" not in link}

    def do_work(self, lxml_doc):
        css_selectors = CSS_SELECTORS
        select_result = {selector: lxml_doc.cssselect(selector) for selector in css_selectors}
        result = dict()

        for key, value in select_result.items():
            if value:
                result[key] = [v.text_content() for v in value]

        return result


if __name__ == '__main__':
    pc = PCCrawler(start_url='http://www.premiumcosmet.ru/',
                   allowed_hosts=('premiumcosmet.ru')
                   )

    csv_header = ["url"] + list(CSS_SELECTORS)

    with open("premiumcosmet.csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, csv_header, delimiter='\t')
        writer.writeheader()

        for url, data in pc.result.items():
            new_data = {key: " ".join(value) for key, value in data.items()}
            new_data.update({"url": url})
            writer.writerow(new_data)
            # writer.writerows()
