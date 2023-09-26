import spacy
from pypdf import PdfReader
from collections import Counter
from tqdm.notebook import tqdm

from spider import Spider
from utils.database import DataBase


class WordFrequency:
    def __init__(self):
        self.nlp = spacy.load("fr_dep_news_trf", disable=["ner", "parser", "textcat"])

    def wordFrequencyFromPDF(self, path="data/Les assassins de la 5e-B.pdf", start_page=14):

        reader = PdfReader(path)
        content = []
        for index in range(start_page, len(reader.pages)):
            content.append(reader.pages[index].extract_text())
        doc = self.nlp("\t".join(content))
        words = Counter(token.lemma_ for token in doc)
        filter_words = [item for item in sorted(words, key=lambda x: -x[1]) if item[1] <= 402]
        return filter_words


if __name__ == '__main__':
    db = DataBase()
    spider = Spider()
    wf = WordFrequency()
    filter_words = wf.wordFrequencyFromPDF()
    i = 0
    wordEntityList = []
    for wordTuple in filter_words:
        if i < 100:
            w = wordTuple[0]
            wordEntity = spider.request(w)
            wordEntityList.append(wordEntity)

    db.insert(wordEntityList)


