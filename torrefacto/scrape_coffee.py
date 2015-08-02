from __future__ import print_function
from functools import reduce
import sys

import collections
import csv
import datetime
from pyquery import PyQuery as pq
import urllib.parse
import urllib.request


SITE_URL = "http://www.torrefacto.ru"
PAGE_URL = "http://www.torrefacto.ru/catalog/roasted/"


def _get_dom(url):
    """Fetch data and build beautiful soup tree"""
    req = urllib.request.Request(PAGE_URL)
    with urllib.request.urlopen(req) as response:
        data = response.read()
    return pq(data)


def _tuple_print(data, stream):
    tuple_str = reduce(lambda x, y: x + y, ["%s " % elem for elem in data],
                       "#")
    print(tuple_str, file=stream)


# FIXME change to normal exception workflow on page source change
def _assert_one(col):
    assert(len(col) == 1)
    return col[0]


def fetch_data():
    # here a mapping 'order num/coffee url' is stored
    results = {}

    dom = _get_dom(PAGE_URL)
    sorts = dom.find('li[id*="bx_"]')

    for sort in sorts:
        sort_info = _assert_one(sort.find_class('morh'))
        price_info = sort.find_class('price-hold')
        # No price info means that coffee is out of stock
        if not price_info:
            continue
        else:
            price_info = _assert_one(price_info)

        # there should be precisely 1 element containing item number
        num_tag = _assert_one(sort_info.find_class('n'))
        name = sort_info.find('h3').text.encode('utf-8').strip()
        url = urllib.parse.urljoin(SITE_URL, sort_info.find('a').get('href'))
        num = int(num_tag.tail.strip())
        price_block = _assert_one(price_info.find_class('price-block'))
        # fetch weight and price for different combinations
        sizes = []
        for div in price_block.findall('div'):
            weight = _assert_one(div.find_class('weight'))
            price = _assert_one(div.find_class('price'))
            sizes.append((weight.text.strip(), int(price.text.strip())))
        # coffee can be ordered
        # FIXME remove direct tuple index reference
        results[num] = {"url": url, "150 gr": sizes[0][1],
                        "450 gr": sizes[1][1], "name": name,
                        "num": num}
    return collections.OrderedDict(sorted(results.items()))


def fetch_data_as_csv(stream):
    sorts = fetch_data()
    header_writer = csv.writer(stream)
    # set current date and time
    date = datetime.datetime.strftime(datetime.datetime.now(),
                                      '%Y-%m-%d %H:%M:%S')
    header_writer.writerow(["Torrefacto prices %s" % date])
    writer = csv.DictWriter(
        stream,
        fieldnames=['num', 'url', 'price', 'name'])
    writer.writeheader()
    for coffee_num in sorts:
        sort = sorts[coffee_num]
        for size in ['150 gr', '450 gr']:
            writer.writerow({'num': "# %d (%s)" % (coffee_num, size),
                             'url': sort['url'],
                             'price': sort[size],
                             'name': sort['name']})


def main():
    out_csv = '--csv' in sys.argv
    stream = sys.stdout

    sorts = fetch_data()
    if not out_csv:
        for coffee_num in sorts:
            print("#%(num)s %(url)s %(150 gr)s %(450 gr)s %(name)s" %
                  sorts[coffee_num], file=stream)

    else:
        fetch_data_as_csv(stream)

if __name__ == "__main__":
    main()
