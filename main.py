import spacy

from pypdf import PdfReader

reader = PdfReader("data/Les assassins de la 5e-B.pdf")
content = []
for i in range(14, len(reader.pages)):
    content.append(reader.pages[i].extract_text())


nlp = spacy.load('zh_core_web_trf')
text = nlp('这是一个句子')
for t in text:
    print(t.text)