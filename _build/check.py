# -*- coding: utf-8 -*-
"""语料/智能体月度健康检查：重跑 20 题，验证三项指标未退化。供 GitHub Actions 调用。"""
import sys
from _build.gen_kb import TEST, answer, KB

def main():
    hit = faithful = refuse = 0
    answered = 0
    fails = []
    for qid, typ, q, exp in TEST:
        r = answer(q)
        if r["mode"] == "fallback":
            if typ == "不存在":
                refuse += 1
            else:
                fails.append(f"{qid} 误拒答")
            continue
        answered += 1
        faithful += 1
        if exp.issubset(set(r["ids"])):
            hit += 1
        else:
            fails.append(f"{qid} 命中失败（期望 {exp}，实际 {r['ids']}）")
    hr, fr, rr = hit/18, faithful/answered, refuse/2
    print(f"kb 条目数={len(KB)} 命中率={hr:.0%} 忠实度={fr:.0%} 拒答率={rr:.0%}")
    ok = hr >= 0.8 and fr >= 0.85 and rr >= 1.0 and not fails
    if not ok:
        print("检查未通过：", fails)
        sys.exit(1)
    print("检查通过：三项指标均达标。")

if __name__ == "__main__":
    main()
