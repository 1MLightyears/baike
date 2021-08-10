"""
baike的测试部分。
由于获取到的内容会随着网页变化而变化，自动化测试结果需要随着更新，比较繁琐，
先把可以用来测试的词放在这里。
"""

from json import load
from time import sleep, time
from random import random, seed
import logging

from baike import getBaike

with open("testcases.json", "r", encoding="utf-8") as f:
    test_words = load(f)

tot = len(test_words)
seed(time())
print("==========baike 测试(共{tot}项)=========")
for i in range(tot):
    print("=" * 12)
    print(
        f"{test_words[i].get('desc','测试')}:{test_words[i].get('args')[0]}({i+1}/{tot})\n"
    )
    try:
        print(getBaike(*test_words[i].get("args", []), **test_words[i]) + "\n\n")
    except Exception as e:
        print("*" * 12)
        print(f"错误:{i+1}/{tot}")
        logging.exception(e)
        print("*" * 12)
    sl = random()
    print(f"  (...{sl:.3f}s...)")
    sleep(sl)
