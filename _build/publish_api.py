# -*- coding: utf-8 -*-
"""通过 GitHub Contents API 把项目文件发布到已创建的空仓库（git push 被代理拦截时的替代方案）。"""
import os, base64, json, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "Zzz04W"
REPO = "college-affairs-agent"
TOKEN = os.environ["GH_TOKEN"]
API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

EXCLUDE = {".git", ".gitignore_is_not_excluded"}
EXCLUDE_FILES = {"01_素材/咨询群聊记录_原始_含个人信息.csv"}  # 含个人信息，不发布

def walk():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in EXCLUDE]
        for f in fn:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if rel in EXCLUDE_FILES:
                continue
            out.append(rel)
    return sorted(out)

def put(path, content):
    url = f"{API}/{urllib.parse.quote(path)}"
    body = json.dumps({"message": f"publish {path}", "content": content}).encode()
    req = urllib.request.Request(url, data=body, method="PUT",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return f"ERR {e.code} {e.read().decode()[:120]}"

import urllib.parse
files = walk()
print(f"待发布文件数：{len(files)}")
ok = 0
for rel in files:
    full = os.path.join(ROOT, rel)
    with open(full, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    st = put(rel, b64)
    if isinstance(st, int) and 200 <= st < 300:
        ok += 1
        print(f"  ✓ {rel} -> {st}")
    else:
        print(f"  ✗ {rel} -> {st}")
print(f"\n完成：{ok}/{len(files)} 个文件发布成功")
