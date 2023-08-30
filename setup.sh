conda create -n spacy38 python=3.8
conda activate spacy38
pip install -U pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -U spacy -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m spacy download zh_core_web_trf
python -m spacy download en_core_web_trf
python -m spacy download fr_dep_news_trf
python -m spacy download fr_core_news_sm
pip install googletrans pandas -i https://pypi.tuna.tsinghua.edu.cn/simple