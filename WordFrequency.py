import spacy
import string
import os

from pypdf import PdfReader
from collections import Counter
from typing import List, Tuple
import logging
import time

from tqdm import tqdm

from WordSpider import Spider
from utils.database import Resource, DataBase, Word

logging.disable(logging.DEBUG)


class WordFrequency:
    def __init__(self):
        self.db = DataBase()
        self.spider = Spider()

    def wordFrequencyFromPDF(self, output_path, input_path=None, start_page=14, freq_ub=402) -> List[Tuple[str, int]]:

        if not os.path.exists(output_path):
            nlp = spacy.load("fr_dep_news_trf", disable=["ner", "parser", "textcat"])
            reader = PdfReader(input_path)
            pages = reader.pages
            text = "\t".join([page.extract_text() for index, page in enumerate(pages) if index >= start_page])
            print("NLP Analysis begin")
            doc = nlp(text)
            print("NLP Analysis end")
            words = [token.lemma_ for token in doc if self.sanitized(token.lemma_)]
            word_count = Counter(words).items()
            word_count = sorted(word_count, key=lambda x: -int(x[1]))
            result = [r for r in word_count if r[1] <= freq_ub]

            with open(output_path, 'w') as f:
                for d in result:
                    f.write(f"{d[0]},{d[1]}\n")

        result = []
        with open(output_path, "r") as f:
            for row in f.readlines():
                word, freq = row.split(",")
                result.append((word, int(freq.strip())))
        return result

    def insertWordFrequency(self, wordTuple: List[Tuple[str, int]], resource: str):
        existWordList = []
        missingWordList = []

        for wordStr, freq in wordTuple:
            resc = Resource()
            resc.freq = freq
            resc.resource = resource

            word = self.db.searchDict(wordStr)
            if word:
                resc.word_id = word.id
                existWordList.append(resc)
            else:
                word = Word()
                word.word = wordStr
                word.resources.append(resc)
                missingWordList.append(self.spider.request(word))
                print(word.word, end=' ')
        print()
        print(f'exist: {len(existWordList)}', end='')
        print(f'not exist: {len(missingWordList)}', end='')
        total = existWordList + missingWordList

        self.db.insert([item for item in total if item])

    @staticmethod
    def sanitized(word: str) -> bool:
        word = word.strip()
        if len(word) < 2:
            return False
        if word[0] in string.punctuation or word[-1] in string.punctuation:
            return False
        if word.isdigit():
            return False
        if word.startswith('’') or word.endswith('’'):
            return False
        return True


if __name__ == '__main__':
    wf = WordFrequency()
    result = wf.wordFrequencyFromPDF("data/Les assassins de la 5e-B.csv", "data/Les assassins de la 5e-B.pdf")
    for i in tqdm(range(7, 200)):
        wf.insertWordFrequency(result[20*i:20*i+20], "Les assassins de la 5e-B.pdf")


# if __name__ == '__main__':
#     db = DataBase()
#     # db.createTable()
#     spider = Spider()
#     wf = WordFrequency()
#     word_count = wf.wordFrequencyFromPDF(output_path='data/word')
#     i = 0
#     wordEntityList = []
#     for word, count in tqdm(word_count):
#         if i >= 110:
#             break
#         elif i >= 100:
#             wordEntity = spider.request(word)
#             if wordEntity:
#                 wordEntityList.append(wordEntity)
#         i += 1
#     db.insert(wordEntityList)


