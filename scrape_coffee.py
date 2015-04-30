from __future__ import print_function
import sys

import BeautifulSoup
import csv
import datetime
import urllib
import urlparse


SITE_URL = "http://www.torrefacto.ru"
PAGE_URL = "http://www.torrefacto.ru/catalog/roasted/"


def fetch_prices(sort_url):
    """Used to retrieve the prices of the precise sort"""
    # by default prices for roasted 150/450 grammes are retrieved
    data = urllib.urlopen(sort_url)
    soup = BeautifulSoup.BeautifulSoup(data)

    price_tags = soup.findAll('div', attrs={'class': 'row obj'})
    if len(price_tags) == 0:
        # out of stock
        return None, None
    # in case of markup changes -> fail here
    assert len(price_tags) == 2
    prices = []
    for price in price_tags:
        str_price = price.find("input").get("value")
        prices.append(int(str_price.split('-')[1]))
    return tuple(prices)


def fetch_data():
    data = urllib.urlopen(PAGE_URL).read()
    soup = BeautifulSoup.BeautifulSoup(data)

    sorts = soup.findAll("div", attrs={"class": "morh"})
    results = []
    for sort in sorts:
        url_tag = sort.find("a")
        num_tag = sort.find("span", attrs={"class": "num"})
        url = urlparse.urljoin(SITE_URL, url_tag.get("href"))
        num = int(num_tag.text.replace('&nbsp;', ''))
        price_s, price_l = fetch_prices(url)
        results.append((num, url, price_s, price_l))
    return sorted(results, key=lambda x: x[0])


def main():
    out_csv = '--csv' in sys.argv
    stream = sys.stdout
    if not out_csv:
        for res in fetch_data():
            print("#%d %s\n" % (res[0], res[1]), file=stream)
    else:
        header_writer = csv.writer(stream)
        # set current date and time
        date = datetime.datetime.strftime(datetime.datetime.now(),
                                          '%Y-%m-%d %H:%M:%S')
        header_writer.writerow(["Torrefacto prices %s" % date])
        writer = csv.DictWriter(
            stream,
            fieldnames=['number', 'url', '150 gr', '450 gr'])
        writer.writeheader()
        for res in fetch_data():
            writer.writerow({'number': "# %d" % res[0], 'url': res[1],
                             '150 gr': res[2], '450 gr': res[3]})

if __name__ == "__main__":
    main()
