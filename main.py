import spacy
from pypdf import PdfReader
from collections import Counter
from tqdm import tqdm
import string
import os

from spider import Spider
from utils.database import DataBase


class WordFrequency:
    def __init__(self):
        self.nlp = spacy.load("fr_dep_news_trf", disable=["ner", "parser", "textcat"])

    def wordFrequencyFromPDF(self, output_path, input_path=None, start_page=14):

        if os.path.exists(output_path):
            result = []
            with open(output_path, "r") as f:
                for row in f.readlines():
                    word, freq = row.split(",")
                    result.append((word, (freq.strip())))
            return result
        else:
            reader = PdfReader(input_path)
            content = []
            for index in range(start_page, len(reader.pages)):
                content.append(reader.pages[index].extract_text())
            doc = self.nlp("\t".join(content))
            words = [token.lemma_ for token in doc if self.sanitized(token.lemma_)]
            word_count = Counter(words)
            word_count = sorted(word_count, key=lambda x: -x[1])
            result = [r for r in word_count if r[1] <= 402]

            with open(output_path, 'w') as f:
                for d in result:
                    f.write(f"{d[0]},{d[1]}\n")
            return result

    @staticmethod
    def sanitized(word):
        if len(word) < 2:
            return False
        if word[0] in string.punctuation or word[1] in string.punctuation:
            return False
        if word.isdigit():
            return False
        return True


if __name__ == '__main__':
    db = DataBase()
    # db.createTable()
    spider = Spider()
    wf = WordFrequency()
    word_count = wf.wordFrequencyFromPDF(output_path='data/word')
    i = 0
    wordEntityList = []
    for word, count in tqdm(word_count):
        if i >= 110:
            break
        elif i >= 100:
            wordEntity = spider.request(word)
            if wordEntity:
                wordEntityList.append(wordEntity)
        i += 1
    db.insert(wordEntityList)


