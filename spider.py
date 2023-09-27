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
        try:
            url = f"https://www.frdic.com/dicts/fr/{quote(wordStr)}"
            resp = requests.get(url, cookies=self.cookies)
            if resp.status_code != 200:
                logging.error(f"Network Error Word: {wordStr}")
                return

            word = Word()
            word.word = wordStr
            html = etree.HTML(resp.text)
            data = html.xpath("//div[@id='ExpFCChild'][1]/*")

            pos = ""
            for elem in data:
                if elem.attrib.get('class') == 'cara':
                    pos = elem.text

                elif elem.attrib.get('class') == 'exp':
                    exps = elem.xpath('./* | ./text()')
                    # 初始化第一个定义并赋值
                    definition = Definition()
                    definition.pos = pos
                    definition.definition = ''

                    FOUND = False
                    for exp in exps:
                        if isinstance(exp, str):
                            definition.definition += exp
                        elif exp.tag == 'img':
                            url = exp.attrib.get('src')
                            char = self.img2Cha.get(url, pic2word(self.ocr, url, self.cookies))
                            if char:
                                self.img2Cha[url] = char
                            definition.definition += char

                        elif exp.attrib.get('class') == 'eg':
                            FOUND = True
                            word.definitions.append(definition)

                            egs = exp.xpath("./* | ./text()")
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

                            definition = Definition()
                            definition.pos = pos
                            definition.definition = ''

                        elif exp.text == '常见用法':
                            break

                    if not FOUND:
                        word.definitions.append(definition)

                elif elem.attrib.get('class') == 'eg':
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

                elif elem.text == '常见用法':
                    break

            for definition in word.definitions:
                new_sentence = []
                for sentence in definition.sentences:
                    if sentence.sentence != "":
                        new_sentence.append(sentence)
                definition.sentences = new_sentence
            return word
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    db = DataBase()
    db.createTable()
    spider = Spider()
    word = spider.request("luire")
    db.insert(word)
