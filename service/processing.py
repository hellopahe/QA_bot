import string
import os
import sys
import numpy as np
import pandas as pd
from nltk import word_tokenize
from rake_nltk import Rake
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from clip_client import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.path import *


class Elastic(object):
    def __init__(self, _index_name, _doc_type_name, stop_words_file=STOP_WORD_PATH):
        self.stop_list = set()
        self.read_stop_words(stop_words_file)
        # self.bert = Client(server='grpc://35.189.189.239:51000')
        self.bert = Client(server='grpc://0.0.0.0:51000')  # 连接到bert_server
        # self.bert = BertClient(port=86500, port_out=86501, show_server_config=True, timeout=1000000)
        # self.bert = Client('grpcs://demo-cas.jina.ai:2096')
        self.index_name = _index_name
        self.doc_type_name = _doc_type_name
        self.es = Elasticsearch([{"host": "35.189.189.239", "port": 9200}], timeout=3600)  # 这里连接到Elastic
        self.es_status = False
        self.check_es_status()  # 检查ES状态
        self.punctuation = set(string.punctuation)

    def read_stop_words(self, file):
        if file:
            with open(file, encoding='utf-8') as f:
                lines = f.readlines()
            self.stop_list.update([x.strip() for x in lines])

    def check_es_status(self):
        print('==========')
        if self.check_exist_index(self.index_name):
            print('[OK] index:', self.index_name)
            if self.check_exist_doc_type(self.index_name, self.doc_type_name):
                print('[OK] doc type:', self.doc_type_name)
                self.es_status = True
            else:
                print('[WARN] not found doc type: %s in index: %s' % (self.index_name, self.doc_type_name))
        else:
            print('[WARN] not found index:', self.index_name)

        if self.es_status:
            print('Enjoy query!')
        else:
            print('Please load data to es from file or textlist!')
        print('==========')

    def check_exist_index(self, _index_name):
        return self.es.indices.exists(index=_index_name)

    def check_exist_doc_type(self, _index_name, _doc_type_name):
        return self.es.indices.exists_type(index=_index_name, doc_type=_doc_type_name)

    def set_mapping(self):
        my_mapping = {"mappings": {
            self.doc_type_name: {
                "properties": {
                    "context": {"type": "text", "index": "false"},  # 原问题不作任何索引
                    "splwords": {"type": "text", "index": "false"},  # 分词结果
                    "keywords": {"type": "text", "analyzer": "simple"},  # 抽取出的关键词
                    "embeding": {"type": "object", "enabled": "false"},  # 句向量
                    "context_id": {"type": "text"}}  # id
            }}
        }

        # 创建Index和Mapping
        self.es.indices.delete(index=self.index_name, ignore=[400, 404])
        create_index = self.es.indices.create(index=self.index_name, body=my_mapping)

        if not create_index["acknowledged"]:
            print("Index data bug...")

    def make_action(self, fields, actions, _id):
        splwords, keywords, embeding = self.split_words(fields)

        if not keywords:
            print('[Error] not found any keywords:', fields)
            return
        if embeding is None:
            return

        try:
            action = {
                "_index": self.index_name,
                "_type": self.doc_type_name,
                "_source": {
                    "context": fields,
                    "splwords": splwords,
                    "keywords": keywords,
                    "embeding": embeding,
                    "context_id": _id,
                }
            }
            actions.append(action)
        except Exception as e:
            print('fields:', fields)
            print(e)

    def load_data_from_file(self, input_file, overwrite=False):

        # 覆盖模式或者ES未准备好得状态下：重新定义mapping
        if overwrite or (not self.es_status):
            self.set_mapping()

        print("Indexing data.....")

        actions = []  # 创建ACTIONS

        df = pd.read_csv(input_file)  # 读取csv并给列编号
        df.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']

        for i in range(len(df)):  # 逐行处理csv数据
            self.make_action(df["e"][i], actions, i)
            err, _ = bulk(
                self.es, actions, index=self.index_name, raise_on_error=True)
            print('已加载%d行' % err)

    @staticmethod
    def to_bert(list_query):
        bert = Client(server='grpc://0.0.0.0:51000')  # 连接到bert_server
        result = bert.encode(list_query)[0]
        # print(result)
        return result

    def split_words(self, query):
        embeding = self.bert.encode([query])[0]
        # embeding = self.to_bert([query])
        splwords = word_tokenize(query)

        rake_nltk_var = Rake()
        rake_nltk_var.extract_keywords_from_sentences(query.split())
        keywords = rake_nltk_var.get_ranked_phrases()

        return splwords, keywords, embeding

    @staticmethod
    def calc_blue(sent1, sent2):  # 计算blue得分（分词得到的相似度）

        len_1 = len(sent1)
        len_2 = len(sent2)

        # 计算惩罚因子BP
        if len_2 >= len_1:
            bp = 1
        else:
            bp = np.exp(1 - len_1 / len_2)

        # 计算输出预测精度p
        pv = [min(sent1.count(w), sent2.count(w)) for w in set(sent2)]

        return bp * np.log(sum(pv) / len_2)

    @staticmethod
    def calc_bert_sim(em1, em2):  # 计算两个句向量em1，em2间的余弦相似度
        num = float(np.mat(em1) * np.mat(em2).T)
        de_nom = np.linalg.norm(np.mat(em1)) * np.linalg.norm(np.mat(em2))
        cos = num / de_nom
        return cos

    def query(self, sentences):  # 处理对话请求的部分

        # 用传进来的句子生成分词splwords，关键词keywords，词向量embeding
        splwords = "/".join(word_tokenize(sentences))
        rake_nltk_var = Rake()
        rake_nltk_var.extract_keywords_from_sentences(sentences.split())
        keywords = " ".join(rake_nltk_var.get_ranked_phrases())
        # embeding = self.bert.encode(sentences.split()).tolist()[0]
        embeding = self.bert.encode([sentences])[0]
        # embeding = self.to_bert([sentences])
        # embeding = self.to_bert([sentences])

        # 用生成的关键词去elastic数据库检索具有相同关键词的条目
        query_words = ' '.join([word for word in keywords.split(' ') if word not in self.stop_list])
        query = {'query': {"match": {"keywords": query_words}}}
        res = self.es.search(self.index_name, self.doc_type_name, body=query)
        hits = res['hits']['hits']

        #  给hits去重
        temp = []
        _hits = []
        for hi in hits:
            _context_id = hi['_source']['context_id']
            if _context_id in temp:
                continue
            else:
                temp.append(_context_id)
                _hits.append(hi)
        hits = _hits

        # 通过计算两个得分（blue & similarity）来从得到的hits中筛选出相似度最高的3个条目
        blues = []
        similar = []
        for hit in hits:
            embed = hit['_source']['embeding']
            spl_word = hit['_source']['splwords']
            blue = self.calc_blue(splwords.split('/'), spl_word)
            # similar_num = self.calc_similarity(embed, np.array(embeding))
            similar_num = self.calc_bert_sim(embed, embeding)
            blues.append(blue)
            similar.append(similar_num)

        scores = np.array(blues) + np.array(similar)  # 计算总得分
        scores_idx = np.argsort(scores)[::-1]  # 将结果从优到劣排序

        read_csv = pd.read_csv(DATA_PATH)
        read_csv.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']

        context_id = []
        context = []
        score = []
        ans = []

        for idx in scores_idx[:3]:  # 取结果队列的前3个
            print(hits[idx]['_source']['context_id'])
            context_id.append(hits[idx]['_source']['context_id'])
            context.append(hits[idx]['_source']['context'])
            score.append(scores[idx])
            ans.append(read_csv["f"][hits[idx]['_source']['context_id']])

        return splwords, keywords, context_id, context, str(score)
