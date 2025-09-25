#!/usr/bin/env python3

from prompt.system import default_params
from utils.utils import pretty_print_dataclass

# 方法1: 使用dataclass的__str__方法
print("方法1 - 使用 print()")
print(default_params)

# 方法2: 使用通用美化函数
print("方法2 - 使用 pretty_print_dataclass()")
pretty_print_dataclass(default_params) 