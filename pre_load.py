# encoding=utf-8
# Created by Ge Zhang @ 2019
# Contact zhangge9194@pku.edu.cn
#
# preload variables from file
# to avoid multiple loading processes in different scripts
# TO BE EDITED

import json
from config import key_methods_path


with open(key_methods_path, 'r') as f:
    key_methods = json.load(f)
