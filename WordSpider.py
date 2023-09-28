import requests
import asyncio
import browser_cookie3
import logging
from lxml import etree
from paddleocr import PaddleOCR
from urllib.parse import quote

from utils.pic2word import pic2word
from utils.database import Word, Definition, Sentence, DataBase, Resource
from typing import Optional, List
from tqdm import tqdm
import aiohttp


class Spider:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        self.cookies = browser_cookie3.chrome()
        self.img2Cha = {}

    def processResponse(self, word: Word, response: str, lock) -> None:
        data = etree.HTML(response).xpath("//div[@id='ExpFCChild'][1]/*")

        pos = ""
        for elem in data:
            if elem.attrib.get('class') == 'cara':
                pos = elem.text
            elif elem.attrib.get('class') == 'exp':
                exps = elem.xpath('./* | ./text()')

                definition = Definition()
                definition.pos = pos
                definition.definition = ''

                FOUND = False
                for exp in exps:
                    if isinstance(exp, str):
                        definition.definition += exp
                    elif exp.tag == 'img':
                        url = exp.attrib.get('src')
                        rec_word = pic2word(self.ocr, url, self.cookies)
                        with lock:
                            char = self.img2Cha.get(url, rec_word)
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
                                rec_word = pic2word(self.ocr, url, self.cookies)
                                with lock:
                                    char = self.img2Cha.get(url, rec_word)
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
                        rec_word = pic2word(self.ocr, url, self.cookies)
                        with lock:
                            char = self.img2Cha.get(url, rec_word)
                            if char:
                                self.img2Cha[url] = char
                        word.definitions[-1].sentences[-1].sentence += char
            elif elem.text == '常见用法':
                break

            # post-processing
            for definition in word.definitions:
                new_sentence = []
                for sentence in definition.sentences:
                    if sentence.sentence != "":
                        new_sentence.append(sentence)
                definition.sentences = new_sentence


    def request(self, w, lock) -> Optional[Word]:
        if isinstance(w, str):
            word = Word()
            word.word = w
        elif isinstance(w, Word):
            word = w
        else:
            return None

        try:
            wordStr = word.word
            url = f"https://www.frdic.com/dicts/fr/{quote(wordStr)}"
            response = requests.get(url, cookies=self.cookies).text
            self.processResponse(word, response, lock)
            return word

        except Exception as e:
            print(e)
            return None


# async def main():
#     results = []
#     spider = Spider()
#     lock = asyncio.Lock()
#     tasks = [spider.request(w) for w in ['luire', 'rester']]
#     with tqdm(total=len(tasks)) as pbar:
#         while tasks:
#             done, tasks = asyncio.wait(tasks, return_when)
#     for task in asyncio.as_completed(tasks):
#         result = await task
#         results.append(result)
#
#     return results


if __name__ == '__main__':
    pass

    # db = DataBase()
    # db.createTable()
    # spider = Spider()
    # word = spider.request("luire")
    # db.insert(word)
