""" pwbot.spiders.store_item_spider
"""

import json
import treq
from twisted.internet.defer import inlineCallbacks
from scrapy import Request
from scrapy import signals
from scrapy.exporters import PythonItemExporter
from scrapy.exceptions import DropItem
from pwbot import settings, parsers, utils
from pwbot.spiders import BasePwbotCrawlSpider
from pwbot.settings import config


class StoreItemPageSpider(BasePwbotCrawlSpider):
    """ pwbot.spiders.store_item_spider.StoreItemPageSpider
    """

    name = 'StoreItemPageSpider'

    allowed_domains = ['amazon.com', 'amazon.ca', 'walmart.com', 'walmart.ca', 'www.walmart.ca', ]

    _domain = None
    _skus = []
    _urls = []
    _crawl_variations = True

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        if 'domain' in kw:
            self._domain = kw['domain'] if kw['domain'] in self.allowed_domains else self._domain
        if 'skus' in kw:
            self._skus = kw['skus'].split(',')
        if 'urls' in kw:
            self._urls = kw['urls'].split(',')
        if 'crawl_variations' in kw:
            self._crawl_variations = utils.true_or_false(kw['crawl_variations'])

    def start_requests(self):
        if len(self._skus) > 0:
            for sku in self._skus:
                if self._domain in ['amazon.com', 'amazon.ca',]:
                    url = settings.AMAZON_ITEM_LINK_FORMAT.format(self._domain, sku, settings.AMAZON_ITEM_VARIATION_LINK_POSTFIX)
                    callback = parsers.parse_amazon_item
                elif self._domain in ['walmart.com',]:
                    url = settings.WALMART_COM_ITEM_LINK_FORMAT.format(self._domain, sku)
                    callback = parsers.parse_walmart_com_item
                elif self._domain in ['walmart.ca',]:
                    url = settings.WALMART_CA_ITEM_LINK_FORMAT.format(self._domain, sku)
                    callback = parsers.parse_walmart_ca_item
                else:
                    continue
                yield Request(url,
                            callback=callback,
                            errback=parsers.resp_error_handler,
                            cb_kwargs={
                                'domain': self._domain,
                                'job_id': self._job_id,
                                'crawl_variations': self._crawl_variations,
                            })
        if len(self._urls) > 0:
            for url in self._urls:
                domain = utils.extract_domain_from_url(url)
                if domain in ['amazon.com', 'amazon.ca',]:
                    callback = parsers.parse_amazon_item
                elif domain in ['walmart.com',]:
                    callback = parsers.parse_walmart_com_item
                elif domain in ['walmart.ca',]:
                    callback = parsers.parse_walmart_ca_item
                else:
                    continue
                yield Request(url,
                            callback=callback,
                            errback=parsers.resp_error_handler,
                            cb_kwargs={
                                'crawl_variations': self._crawl_variations,
                                'domain': domain,
                                'job_id': self._job_id,
                            })

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_scraped, signal=signals.item_scraped)
        return spider

    def _serialize(self, item, **kwargs):
        e = PythonItemExporter(binary=False, **kwargs)
        return e.export_item(item)

    def item_scraped(self, item, response, spider):
        # Send the scraped item to the server
        if type(item).__name__ not in ['ListingItem',]:
            raise DropItem("Invalid item type - {}".format(type(item).__name__))

        _logger = self.logger
        @inlineCallbacks
        def _cb(resp):
            text = yield resp.text(encoding='UTF-8')
            if resp.code >= 400:
                _logger.error("{}: HTTP Error: Failed to create/update item - {}".format(resp.code, text))

        d = treq.post('http://{}:{}/api/resource/raw_data/'.format(
                    config['PriceWatchWeb']['host'], config['PriceWatchWeb']['port']),
            json.dumps(self._serialize(item)).encode('ascii'),
            headers={b'Content-Type': [b'application/json']}
        )
        d.addCallback(_cb)
        # The next item will be scraped only after
        # deferred (d) is fired
        return d


# class AmazonItemPageSpider(StoreItemPageSpider):

#     """ crawl amazon items
#     """
#     name = 'AmazonItemPageSpider'

#     allowed_domains = ['amazon.com', 'amazon.ca',]
#     # handle_httpstatus_list = [404]

#     _domain = 'amazon.com'
#     __asins = []
#     __asin_cache = {}
#     _urls = []
#     __parse_pictures = True
#     _crawl_variations = True

#     def __init__(self, *a, **kw):
#         super().__init__(*a, **kw)
#         if 'domain' in kw:
#             self._domain = kw['domain'] if kw['domain'] in self.allowed_domains else self._domain
#         if 'asins' in kw:
#             self.__asins = self.__filter_asins(kw['asins'])
#         if 'urls' in kw:
#             self._urls = kw['urls'].split(',')
#             # _set_asins_from_urls = ( utils.extract_asin_from_url(u, self._domain) for u in kw['urls'].split(',') )
#             # if _set_asins_from_urls is not None:
#             #     self.__asins = self.__asins + list(_set_asins_from_urls - set(self.__asins))
#         if 'parse_pictures' in kw:
#             self.__parse_pictures = utils.true_or_false(kw['parse_pictures'])
#         if 'crawl_variations' in kw:
#             self._crawl_variations = utils.true_or_false(kw['crawl_variations'])

#     def start_requests(self):
#         if len(self.__asins) > 0:
#             for asin in self.__asins:
#                 yield Request(settings.AMAZON_ITEM_LINK_FORMAT.format(self._domain, asin, settings.AMAZON_ITEM_VARIATION_LINK_POSTFIX),
#                             callback=parsers.parse_amazon_item,
#                             errback=parsers.resp_error_handler,
#                             cb_kwargs={
#                                 'parse_pictures': self.__parse_pictures,
#                                 'crawl_variations': self._crawl_variations,
#                                 'domain': self._domain,
#                             })
#         if len(self._urls) > 0:
#             for url in self._urls:
#                 yield Request(url,
#                             callback=parsers.parse_amazon_item,
#                             errback=parsers.resp_error_handler,
#                             cb_kwargs={
#                                 'parse_pictures': self.__parse_pictures,
#                                 'crawl_variations': self._crawl_variations,
#                                 'domain': utils.extract_domain_from_url(url),
#                             })

#     def __filter_asins(self, asins):
#         filtered_asins = []
#         if isinstance(asins, str):
#             asins = asins.split(',')
#         for asin in asins:
#             asin = asin.strip()
#             if asin not in self.__asin_cache:
#                 self.__asin_cache[asin] = True
#                 filtered_asins.append(asin)
#         return filtered_asins

