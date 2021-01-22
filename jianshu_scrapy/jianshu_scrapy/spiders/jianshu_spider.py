import scrapy
import re
from scrapy import Request
from ..items import JianshuScrapyItem
from ..items import relationItem


class jianshuSpider(scrapy.Spider):
    name = "jianshu_spider"
    allowed_domains = ["jianshu.com"]

    base_headers = {'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                    'Connection': 'keep-alive',
                    'Referer': 'http://www.baidu.com'}

    def start_requests(self):
        yield Request("http://www.jianshu.com/u/12532d36e4da", headers=self.base_headers)
        yield Request("http://www.jianshu.com/u/9b20c7d63b77", headers=self.base_headers)
        yield Request("http://www.jianshu.com/u/94bbc48171c7", headers=self.base_headers)
        yield Request("http://www.jianshu.com/u/181e7b1b1423", headers=self.base_headers)
        yield Request("http://www.jianshu.com/u/8faa58cbfde1", headers=self.base_headers)
        yield Request("http://www.jianshu.com/u/8530ab416e50", headers=self.base_headers)

    def parse(self, response):
        """
        filename='jianshu'
        with open(filename,'wb') as f:
            f.write(response.body)
        """
        info_item = JianshuScrapyItem()
        uid = response.xpath('/html/body/div[1]/div/div[1]/div[1]/div[2]/a/@href').extract_first().split('/')[-1]
        nickname = response.xpath('/html/body/div[1]/div/div[1]/div[1]/div[2]/a/text()').extract_first()
        head_pic = response.xpath('/html/body/div[1]/div/div[1]/div[1]/a[1]/img/@src').extract_first()
        gender = 'to-do'
        following_num = response.xpath(
            '/html/body/div[1]/div/div[1]/div[1]/div[3]/ul/li[1]/div/a/p/text()').extract_first()
        follower_num = response.xpath(
            '/html/body/div[1]/div/div[1]/div[1]/div[3]/ul/li[2]/div/a/p/text()').extract_first()
        articles_num = response.xpath(
            '/html/body/div[1]/div/div[1]/div[1]/div[3]/ul/li[3]/div/a/p/text()').extract_first()
        words_num = response.xpath('/html/body/div[1]/div/div[1]/div[1]/div[3]/ul/li[4]/div/p/text()').extract_first()
        beliked_num = response.xpath('/html/body/div[1]/div/div[1]/div[1]/div[3]/ul/li[5]/div/p/text()').extract_first()

        info_item['uid'] = uid
        info_item['nickname'] = nickname
        info_item['head_pic'] = head_pic
        info_item['gender'] = gender
        info_item['following_num'] = int(following_num)
        info_item['follower_num'] = int(follower_num)
        info_item['articles_num'] = int(articles_num)
        info_item['words_num'] = int(words_num)
        info_item['beliked_num'] = int(beliked_num)
        yield info_item
        yield Request("http://www.jianshu.com/users/{uid}/followers".format(uid=uid), headers=self.base_headers,
                      callback=self.parser_followers)
        yield Request("http://www.jianshu.com/users/{uid}/following?page=1".format(uid=uid), headers=self.base_headers,
                      callback=self.parser_followering)

    def parser_followering(self, response):
        """
        filename=response.url.split('/')[-2]
        with open(filename,'wb') as f:
            f.write(response.body)
        #print ('+++++++++++++++++',response.status,'+++++++++++++++++++++')
        """
        author_uid = response.url.split('/')[-2]
        followers_per_page = 9
        followering_num = int(
            response.xpath('/html/body/div[1]/div/div[1]/ul/li[1]/a/text()').extract_first().split(' ')[-1])
        range_end = 10
        if followering_num < followers_per_page:
            range_end = followering_num
        for i in range(1, range_end):
            followering_uid = response.xpath(
                '/html/body/div[1]/div/div[1]/div[2]/ul/li[{id}]/div[1]/a/@href'.format(id=i)).extract_first().split(
                '/')[-1]
            info_relation = relationItem()
            info_relation['uid'] = author_uid
            info_relation['follower'] = followering_uid
            yield info_relation
            # print ( "http://www.jianshu.com/u/{uid}".format(uid=followering_uid) )
            yield Request("http://www.jianshu.com/u/{uid}".format(uid=followering_uid), headers=self.base_headers,
                          callback=self.parse)

    def parser_followers(self, response):
        """
            filename='followers.html'
            with open(filename,'wb') as f:
                f.write(response.body)
        """
        author_uid = response.url.split('/')[-2]
        followers_per_page = 9
        followers_num = response.xpath(
            '/html/body/div/div[1]/div[1]/div[1]/div[3]/ul/li[2]/div/a/p/text()').extract_first()
        page_num = int(int(followers_num) / followers_per_page)

        range_end = 10
        if int(followers_num) <= 9:
            range_end = int(followers_num)
        for i in range(1, range_end):
            follers_xpath = '/html/body/div/div[1]/div[1]/div[2]/ul/li[{id}]/div[1]/a/@href'.format(id=i)
            follower_uid = response.xpath(follers_xpath).extract_first().split('/')[-1]
            yield Request("http://www.jianshu.com/u/{uid}".format(uid=follower_uid), headers=self.base_headers,
                          callback=self.parse)
            info_relation = relationItem()
            info_relation['uid'] = author_uid
            info_relation['follower'] = follower_uid
            yield info_relation

        if page_num >= 2:
            for i in range(2, page_num):
                url = 'http://www.jianshu.com/users/{uid}/followers?page={num}'.format(uid=author_uid, num=i)
                yield Request(url, headers=self.base_headers, callback=self.parser_followers_nextpage)

    def parser_followers_nextpage(self, response):
        """
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        filename='followers_nextpage.html'
        with open(filename,'wb') as f:
            f.write(response.body)
        """
        for i in range(1, 10):
            followers_path = '/html/body/div/div[1]/div[1]/div[2]/ul/li[{num}]/div[1]/a/@href'.format(num=i)
            result = response.xpath(followers_path).extract_first().split('/')
            # if result is not empty
            if len(result):
                followers_uid = result[-1]
                # print "http://www.jianshu.com/u/{uid}".format(uid=followers_uid)
                yield Request("http://www.jianshu.com/u/{uid}".format(uid=followers_uid), headers=self.base_headers,
                              callback=self.parse)

