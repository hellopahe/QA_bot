from processing import ESearch
from utils.path import *

if __name__ == "__main__":

    # 初始化Elastic
    index_name = 'bert_test'
    doc_type_name = 'bert_test'
    es = ESearch(index_name, doc_type_name)

    # 删除es中现存的索引
    path = []
    for index in es.es.indices.get('*'):
        path.append(index)
    for index in path:
        es.es.indices.delete(index=index)

    # 从数据集构造索引
    es.load_data_from_file(DATA_PATH)
    print('done!')