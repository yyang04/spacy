import requests
import browser_cookie3
import logging
from lxml import etree
from paddleocr import PaddleOCR
from urllib.parse import quote

from utils.pic2word import pic2word
from utils.database import Word, Definition, Sentence, DataBase
from typing import Optional


class Spider:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        self.cookies = browser_cookie3.chrome()
        self.img2Cha = {}

    def request(self, wordStr) -> Optional[Word]:
        url = f"https://www.frdic.com/dicts/fr/{quote(wordStr)}"
        resp = requests.get(url, cookies=self.cookies)
        if resp.status_code != 200:
            logging.error(f"Network Error Word: {wordStr}")
            return

        word = Word()
        word.word = wordStr
        html = etree.HTML(resp.text)
        data = html.xpath("//div[@id='ExpFCChild'][1]/*")

        for elem in data:
            if elem.attrib.get('class') == 'cara':
                definition = Definition()
                definition.pos = elem.text
                word.definitions.append(definition)

            if elem.attrib.get('class') == 'exp':
                egs = elem.xpath('./* | ./text()')
                word.definitions[-1].definition = ''
                for eg in egs:
                    if isinstance(eg, str):
                        word.definitions[-1].definition += eg
                    elif eg.tag == 'img':
                        url = eg.attrib.get('src')
                        char = self.img2Cha.get(url, pic2word(self.ocr, url, self.cookies))
                        if char:
                            self.img2Cha[url] = char
                        word.definitions[-1].definition += char

            if elem.attrib.get('class') == 'eg':
                egs = elem.xpath("./* | ./text()")
                sentence = Sentence()
                sentence.sentence = ""
                word.definitions[-1].sentences.append(sentence)

                for eg in egs:
                    if isinstance(eg, str):
                        word.definitions[-1].sentences[-1].sentence += eg
                    elif eg.tag == 'br':
                        sentence = Sentence()
                        sentence.sentence = ""
                        word.definitions[-1].sentences.append(sentence)
                    elif eg.tag == 'img':
                        url = eg.attrib.get('src')
                        char = self.img2Cha.get(url, pic2word(self.ocr, url, self.cookies))
                        if char:
                            self.img2Cha[url] = char
                        word.definitions[-1].sentences[-1].sentence += char

        for definition in word.definitions:
            new_sentence = []
            for sentence in definition.sentences:
                if sentence.sentence != "":
                    new_sentence.append(sentence)
            definition.sentences = new_sentence
        return word


if __name__ == '__main__':
    db = DataBase()
    spider = Spider()
    # word = spider.request("éviter")
    db.search("éviter")
    # db.createTable()
    # db.insert(word)

    print(1)
    # frenchWord = spider.classTranfer(response)
    # db.insertFrenchWord([frenchWord])













