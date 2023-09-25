import io

import requests
import browser_cookie3
from lxml import etree
from typing import List
from paddleocr import PaddleOCR
from urllib.parse import quote
from utils.pic2word import pic2word


class Word:
    def __init__(self):
        self.name = None  # 词汇名
        self.exp: List[Exp] = []  # 词解释


class Exp:
    def __init__(self):
        self.cara = None  # 词性
        self.key = None  # 翻译
        self.eg: List[str] = []  # 例句


class Spider:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        self.cookies = browser_cookie3.chrome()

    def request(self, w) -> Word:
        url = f"https://www.frdic.com/dicts/fr/{quote(w)}"
        response = requests.get(url, cookies=self.cookies)
        html = etree.HTML(response.text)
        data = html.xpath("//div[@id='ExpFCChild'][1]/*")
        html.xpath("//div[@id='ExpFCChild'][1]/*")[6].xpath("./* | ./text()")
        word = Word()
        word.name = w
        exps: List[Exp] = []

        for elem in data:
            if hasattr(elem, 'attrib'):
                if elem.attrib.get('class') == 'cara':
                    exp = Exp()
                    exp.cara = elem.text
                    exps.append(exp)
                if elem.attrib.get('class') == 'exp':
                    exps[-1].key = elem.text
                if elem.attrib.get('class') == 'eg':
                    egs = elem.xpath("./* | ./text()")
                    for eg in egs:
                        if isinstance(eg, str):
                            exps[-1].eg.append(eg)
                        elif eg.tag == 'br':
                            exps[-1].eg.append("")
                        elif eg.tag == 'img':
                            url = eg.attrib.get('src')
                            exps[-1].eg[-1] += pic2word(self.ocr, url, self.cookies)
        for exp in exps:
            new_eg = []
            for eg in exp.eg:
                if eg != "":
                    new_eg.append(eg)
            exp.eg = new_eg
        word.exp = exps

        return word


if __name__ == '__main__':

    spider = Spider()
    spider.request("éviter")








