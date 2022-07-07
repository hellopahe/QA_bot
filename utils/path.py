import pathlib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

root_dir = pathlib.Path(__file__).parent.parent

DATA_PATH = os.path.join(root_dir, 'data', 'findao_config_cfg_faq.csv')  # 数据集

STOP_WORD_PATH = os.path.join(root_dir, 'data', 'stop_words.txt')  # 停用词表




