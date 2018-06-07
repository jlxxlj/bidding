# coding=utf-8
# author="Jianghua Zhao"
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

res = []

with open("ttt.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = unicode(line)
        if u"|" in line:
            items = line.split(u"|")
        else:
            items = line
        for ch in items:
            if len(ch) > 1:
                res.append(ch)
            elif ord(ch) > 128 and ch not in res:
                res.append(ch)

with open("quantifier.txt", "w") as f:
    line = u"|".join(res) + "\n"
    f.writelines([line])
