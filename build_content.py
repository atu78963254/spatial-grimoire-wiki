# -*- coding: utf-8 -*-
"""把 故事聖經 wiki/markdown 轉成 Quartz content/：
- 去掉檔頭 H1（Quartz 用 frontmatter title）
- 結尾「分類：[[分類:X]]、…」→ frontmatter tags
- 重定向檔 → 目標頁的 aliases（Quartz 會自動產生轉址頁）
- 產生 index.md 首頁
"""
import os, re, shutil, sys, collections

SRC = r"C:\Users\atu78\Desktop\靈感被搞\故事聖經_20260907\wiki\markdown"
DST = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\atu78\Desktop\靈感被搞\空間魔導書wiki-quartz\content"

FOLDERS = ["世界觀", "人物", "勢力", "器物", "地理", "設定"]

# 重定向：alias -> target
aliases = collections.defaultdict(list)
for f in sorted(os.listdir(os.path.join(SRC, "重定向"))):
    if not f.endswith(".md"):
        continue
    t = open(os.path.join(SRC, "重定向", f), encoding="utf-8").read()
    m = re.search(r"\[\[([^\]|]+)", t)
    if m:
        aliases[m.group(1)].append(f[:-3])

def yaml_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def convert(title, text):
    lines = text.rstrip("\n").split("\n")
    # 去 H1
    if lines and lines[0].strip() == "# " + title:
        lines = lines[1:]
    elif lines and lines[0].startswith("# "):
        lines = lines[1:]
    # 結尾分類
    tags = []
    body = "\n".join(lines).rstrip()
    m = re.search(r"\n(?:---\n)?分類：(.*)\s*$", body)
    if m:
        tags = re.findall(r"\[\[分類:([^\]]+)\]\]", m.group(1))
        body = body[: m.start()].rstrip()
    body = re.sub(r"\[\[分類:([^\]]+)\]\]", r"#\1", body)  # 保險
    fm = ["---", "title: " + yaml_str(title)]
    if tags:
        fm.append("tags:")
        fm += ["  - " + yaml_str(t) for t in tags]
    if aliases.get(title):
        fm.append("aliases:")
        fm += ["  - " + yaml_str(a) for a in aliases[title]]
    fm.append("---")
    return "\n".join(fm) + "\n\n" + body.lstrip("\n") + "\n"

if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST)

count = 0
titles = set()
for folder in FOLDERS:
    os.makedirs(os.path.join(DST, folder))
    for f in sorted(os.listdir(os.path.join(SRC, folder))):
        if not f.endswith(".md"):
            continue
        title = f[:-3]
        titles.add(title)
        text = open(os.path.join(SRC, folder, f), encoding="utf-8").read()
        open(os.path.join(DST, folder, f), "w", encoding="utf-8", newline="\n").write(convert(title, text))
        count += 1

# 全條目索引
idx = open(os.path.join(SRC, "全條目索引.md"), encoding="utf-8").read()
open(os.path.join(DST, "全條目索引.md"), "w", encoding="utf-8", newline="\n").write(convert("全條目索引", idx))

# 未對應到的重定向
missing = [(a, t) for t, al in aliases.items() for a in al if t not in titles]

# 首頁
book = open(os.path.join(SRC, "世界觀", "空間魔導書與少年魔法師.md"), encoding="utf-8").read()
chapters = re.findall(r"^\| ([一二三四五六七八九]) \| \[\[([^\]]+)\]\]", book, re.M)
chap_lines = "\n".join(f"{i+1}. [[{v}]]" for i, (k, v) in enumerate(chapters))
index = f"""---
title: "首頁"
---

**歡迎來到《空間魔導書與少年魔法師》wiki。**

本站整理小說全九篇的人物、勢力、地理、器物與魔法設定，共 {count} 個條目。每條資料均以原文為準，未在原文出現的資訊一律不補。左側可展開資料夾瀏覽，右上角可全文搜尋，每頁右側有關係圖與反向連結。

## 從這裡開始

- [[空間魔導書與少年魔法師]]：作品總覽
- [[世界觀]]：兩塊大陸與帝國、聯邦、共和國、教廷的格局
- [[年表]]：全書時間線
- [[全條目索引]]：全部條目一覽，依篇幅排序

## 九篇

{chap_lines}

## 分類

- [[人物/|人物]]、[[勢力/|勢力]]、[[地理/|地理]]、[[器物/|器物]]、[[設定/|設定]]、[[世界觀/|世界觀與篇章]]
- 標籤： #人物 #勢力 #地點 #器物 #設定 #篇章 ，完整標籤列表見 [tags](tags/)

## 專題

- [[思想與論戰]]、[[意識形態批判]]：全書的論述線
- [[魔法體系]]、[[位階體系]]：魔法設定入口
- [[法術一覽・低階]]、[[法術一覽・中階]]、[[法術一覽・聖階與傳奇]]
"""
open(os.path.join(DST, "index.md"), "w", encoding="utf-8", newline="\n").write(index)

print("pages:", count, "+ index + 全條目索引")
print("aliases:", sum(len(v) for v in aliases.values()), "missing targets:", missing)
print("chapters:", [v for _, v in chapters])
