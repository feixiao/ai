# -*- coding: utf-8 -*-
"""pytest 共享配置: 把包根目录加入 import 路径, 便于测试直接导入同级模块。"""

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))
