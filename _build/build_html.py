# -*- coding: utf-8 -*-
"""读取 kb.json，生成自包含的 agent/index.html（移动端优先、三段式作答）。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kb = json.load(open(os.path.join(ROOT, "agent", "kb.json"), encoding="utf-8"))

SAFETY = [
    {"type":"医疗健康","keywords":["药","诊断","睡不着","睡眠","心理","抑郁","治疗","看病"],
     "conclusion":"我不提供任何用药或诊断建议。",
     "text":"本智能体仅依据学院事务制度文件作答，不涉及医疗健康判断。",
     "nextstep":"如持续睡眠或情绪困扰，建议联系学校心理健康教育中心或前往正规医疗机构就诊。"},
    {"type":"投资理财","keywords":["理财","投资","收益","炒股","基金","投钱"],
     "conclusion":"我不提供任何投资或理财建议。",
     "text":"本智能体服务范围为学院事务咨询，不包含投资理财。",
     "nextstep":"学费请按学校规定用途使用；理财请咨询持牌金融机构或家长。"},
    {"type":"处分个案","keywords":["撤销处分","把处分撤","想办法把","疏通","帮忙撤销","把处分"],
     "conclusion":"我无法代办、不提供规避路径，须按程序处理。",
     "text":"处分认定与撤销属个案，依据学生管理规定由相关部门核实。",
     "nextstep":"请联系所在学院学生工作办公室，由老师核实后按程序答复。"},
    {"type":"代办决策","keywords":["代写","代办","定稿","替我写","直接定稿","写一份","申请书"],
     "conclusion":"我不代为生成定稿文书或代办决策。",
     "text":"个案决策与代办超出本智能体服务范围。",
     "nextstep":"建议先咨询学院辅导员与教务处，明确后果后再自行办理。"},
]
FALLBACK = {
    "conclusion":"资料中未收录该问题，我不能推测。",
    "text":"五份语料（教学管理制度2024、奖助学金2025、宿舍报修2024、教室多媒体2024、教务FAQ2025）中均无相关条款。",
    "nextstep":"建议联系所在学院教学办公室或教务处学籍科咨询（电话见各文件维护部门）。"}

NEXT = {
    "教学与考试":"通过教务系统办理；具体以教务处当期通知为准（教学保障电话 0411-0000-0002）。",
    "奖助学金":"向所在学院学生工作办公室提交申请；评审与发放详见学生工作处规定。",
    "后勤报修":'通过“后勤服务”线上平台提交报修单；紧急情况拨打后勤值班电话 0411-0000-0000。',
}

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>学院事务咨询助手</title>
<style>
  :root{--bg:#f5f7fa;--card:#fff;--brand:#2563eb;--brand2:#1e40af;--ok:#0f9d58;--warn:#d97706;--text:#1f2937;--sub:#6b7280;--line:#e5e7eb;}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);font-size:16px;line-height:1.6}
  header{background:linear-gradient(135deg,var(--brand),var(--brand2));color:#fff;padding:18px 16px 16px}
  header h1{margin:0;font-size:20px;font-weight:700}
  header p{margin:6px 0 0;font-size:13px;opacity:.92}
  .wrap{max-width:680px;margin:0 auto;padding:14px 14px 40px}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
  .chip{background:#eef2ff;color:var(--brand2);border:1px solid #dbe3ff;border-radius:999px;padding:6px 12px;font-size:13px;cursor:pointer}
  .chip:active{transform:scale(.96)}
  .box{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
  .row{display:flex;gap:8px}
  textarea{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px;font-size:16px;resize:none;height:64px;font-family:inherit}
  button{background:var(--brand);color:#fff;border:0;border-radius:10px;padding:0 18px;font-size:16px;font-weight:600;cursor:pointer}
  button:active{background:var(--brand2)}
  .ans .seg{margin:10px 0}
  .seg .lab{display:inline-block;font-weight:700;color:var(--brand2);font-size:13px;background:#eef2ff;border-radius:6px;padding:1px 8px;margin-bottom:4px}
  .seg .val{margin:0;white-space:pre-wrap;word-break:break-word}
  .ev{font-size:13px;color:var(--sub);border-left:3px solid #c7d2fe;padding-left:8px;margin-top:4px}
  .tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:999px;margin-left:6px;vertical-align:middle}
  .tag.s{background:#fee2e2;color:#b91c1c}
  .tag.f{background:#dcfce7;color:#15803d}
  .tag.b{background:#fef3c7;color:#b45309}
  .meta{font-size:12px;color:var(--sub);margin-top:6px}
  .foot{text-align:center;font-size:12px;color:var(--sub);margin-top:18px}
  .empty{color:var(--sub);font-size:14px;text-align:center;padding:18px 0}
</style>
</head>
<body>
<header>
  <h1>学院事务咨询助手</h1>
  <p>覆盖补考 / 缓考 / 重修 / 成绩复核 / 奖助学金 / 宿舍与教室报修六大类事务 · 仅依据学院现行制度文件作答</p>
</header>
<div class="wrap">
  <div class="chips" id="chips"></div>
  <div class="box">
    <div class="row">
      <textarea id="q" placeholder="试着问我：补考申请要在多久内提交？"></textarea>
    </div>
    <div class="row" style="margin-top:8px;justify-content:flex-end">
      <button id="ask">提问</button>
    </div>
  </div>
  <div id="out"><div class="empty">在上方输入问题，或点选上面的常见问题。</div></div>
  <div class="foot">资料以文件生效日期为准；本页为课堂练习用虚构语料，电话与金额为教学设定。</div>
</div>
<script>
const KB = __KB__;
const SAFETY = __SAFETY__;
const FALLBACK = __FALLBACK__;
const NEXT = __NEXT__;
const QUICK = ["补考申请要在多久内提交？","缓考要交什么材料？","重修要交学费吗？最多能重修几次？","国家奖学金多少钱？","助学金分几档？一等多少钱？","宿舍漏水怎么报修？多久能来？","教室投影打不开找谁？","交换生的学分怎么认定？"];

function scoreEntry(e,q){let s=0;for(const k of e.keywords){if(q.indexOf(k)>=0)s++;}return s*(e.weight||1);}
function answer(q){
  for(const s of SAFETY){if(s.keywords.some(k=>q.indexOf(k)>=0)){return {mode:'safety',type:s.type,conclusion:s.conclusion,text:s.text,nextstep:s.nextstep,entries:[]};}}
  const scored=KB.map(e=>[scoreEntry(e,q),e]).filter(x=>x[0]>=2).sort((a,b)=>b[0]-a[0]);
  if(!scored.length){return {mode:'fallback',...FALLBACK,entries:[]};}
  const seen=new Set(),entries=[];
  for(const [s,e] of scored){if(seen.has(e.id))continue;seen.add(e.id);entries.push(e);}
  return {mode:'kb',entries};
}
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function render(r){
  const out=document.getElementById('out');
  if(r.mode==='kb'){
    let cats=new Set(r.entries.map(e=>e.category));
    let nextHtml=[...cats].map(c=>`<p class="val">▸ ${esc(NEXT[c]||'')}</p>`).join('');
    let ev=r.entries.map(e=>`<div class="ev">《${esc(e.file_full)}》${esc(e.clause)}：${esc(e.text)}</div>`).join('');
    let conc=r.entries.map(e=>'· '+esc(e.conclusion)).join('<br>');
    out.innerHTML=`<div class="box ans">
      <div class="seg"><span class="lab">结论</span><p class="val">${conc}</p></div>
      <div class="seg"><span class="lab">依据</span>${ev}</div>
      <div class="seg"><span class="lab">下一步</span>${nextHtml}</div>
    </div>`;
  } else {
    let tag = r.mode==='safety' ? '<span class="tag s">越界·转介</span>' : '<span class="tag b">资料未收录</span>';
    out.innerHTML=`<div class="box ans">
      <div class="seg"><span class="lab">结论</span><p class="val">${esc(r.conclusion)} ${tag}</p></div>
      <div class="seg"><span class="lab">依据</span><p class="val">${esc(r.text)}</p></div>
      <div class="seg"><span class="lab">下一步</span><p class="val">▸ ${esc(r.nextstep)}</p></div>
    </div>`;
  }
}
function ask(){const q=document.getElementById('q').value.trim();if(!q)return;render(answer(q));}
document.getElementById('ask').addEventListener('click',ask);
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();ask();}});
const chips=document.getElementById('chips');
QUICK.forEach(t=>{const c=document.createElement('span');c.className='chip';c.textContent=t;c.onclick=()=>{document.getElementById('q').value=t;ask();};chips.appendChild(c);});
</script>
</body>
</html>"""

html = (HTML
        .replace("__KB__", json.dumps(kb, ensure_ascii=False))
        .replace("__SAFETY__", json.dumps(SAFETY, ensure_ascii=False))
        .replace("__FALLBACK__", json.dumps(FALLBACK, ensure_ascii=False))
        .replace("__NEXT__", json.dumps(NEXT, ensure_ascii=False)))

with open(os.path.join(ROOT, "agent", "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("index.html written, bytes =", len(html))
