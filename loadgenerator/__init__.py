# -*- coding: UTF-8 -*-
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("..") # 这句是为了导入_config
from locustfile import SPECIFIC_TASK