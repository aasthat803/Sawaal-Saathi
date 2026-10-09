import base64
import json

import sawaal as sw

PAGE = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sawaal Saathi 🎤</title>
<style>
body{font-family:system-ui,sans-serif;max-width:720px;margin:0 auto;padding:16px;background:#f6f4ff;color:#221b3a}
h1{margin:0}p.sub{margin:2px 0 12px;color:#5b5278}
button,select,textarea{font-size:16px;border-radius:10px;border:1px solid #d3cdf0;padding:10px;font-family:inherit}
button{background:#5b3fd6;color:#fff;border:0;cursor:pointer}button:disabled{opacity:.5}
.ghost{background:#fff;color:#221b3a;border:1px solid #d3cdf0}
.card{background:#fff;border:1px solid #d3cdf0;border-radius:14px;padding:14px;margin:12px 0}
#q{font-size:19px;font-weight:600;line-height:1.35}
textarea{width:100%;box-sizing:border-box;height:170px}
.meta{font-size:13px;color:#5b5278;margin:4px 0 10px}
.score{font-size:44px;font-weight:700;color:#5b3fd6}
.bar{height:10px;background:#e8e4fb;border-radius:6px;overflow:hidden}.bar i{display:block;height:100%;background:#5b3fd6;width:0}
.star span{display:inline-block;padding:4px 10px;border-radius:999px;margin:6px 6px 0 0;font-size:13px;background:#eee;color:#666}
.star span.on{background:#dff5e6;color:#166534}
pre{white-space:pre-wrap;font-family:inherit;line-height:1.5;margin:10px 0 0}
.src{font-size:11px;color:#7a7295;margin-top:6px}.glow{font-weight:600;color:#166534}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.note{font-size:12px;color:#7a7295;margin-top:12px}
</style></head><body>
<h1>Sawaal Saathi 🎤</h1>
<p class="sub">Your kind interview-practice buddy. Answer a question, get a scorecard and friendly coaching, then try again and watch your glow-up.</p>
<div class="row">
<select id="track"><option value="general">General HR</option><option value="tech">Tech / projects</option><option value="customer">Customer-facing</option></select>
<select id="lang"><option value="en">English coach</option><option value="hinglish">Hinglish coach</option></select>
<button class="ghost" onclick="newQ()">🎲 New question</button>
</div>
<div class="card"><div class="meta">Your question</div><div id="q">Loading a warm-up question...</div></div>
<textarea id="a" placeholder="Type your answer like you would say it out loud. Tip: situation, task, action, result." oninput="count()"></textarea>
<div class="meta" id="wc">0 words (aim for 60 to 180)</div>
<button id="go" onclick="score()">Score my answer</button>
<div class="card" id="res" style="display:none">
<div class="score" id="sc"></div><div id="lv" class="meta"></div>
<div class="bar"><i id="bar"></i></div>
<div class="star" id="star"></div>
<div class="glow" id="glow"></div>
<pre id="fb"></pre><div class="src" id="src"></div>
</div>
<div class="card" id="histc" style="display:none"><div class="meta">This session</div><div id="hist"></div></div>
<p class="note">Practice tool only. Nothing you type is stored. Feedback is automatic guidance, not a guarantee about any interview.</p>
<script>
const $=id=>document.getElementById(id);
let seen=[],attempts={},busy=false;
async function post(p){const r=await fetch(location.href.split('#')[0],{method:'POST',body:JSON.stringify(p)});return r.json();}
function count(){const n=($('a').value.match(/\b[\w']+\b/g)||[]).length;$('wc').textContent=n+' words (aim for 60 to 180)';}
async function newQ(){
 $('q').textContent='Finding a good one... 🎲';
 try{const d=await post({action:'question',track:$('track').value,seen:seen});
  if(d.question){$('q').textContent=d.question;seen.push(d.question);if(seen.length>10)seen.shift();$('a').value='';count();$('res').style.display='none';}
  else{$('q').textContent=d.error||'Tell me about a time you learned something quickly.';}
 }catch(e){$('q').textContent='Tell me about a time you learned something quickly.';}
}
async function score(){
 const ans=$('a').value.trim(),q=$('q').textContent;
 if(busy)return;
 if(!ans){alert('Your answer box is empty. Even two sentences is a great start!');return;}
 busy=true;$('go').disabled=true;$('go').textContent='Reading your answer... 🧐';
 try{const d=await post({action:'score',question:q,answer:ans,lang:$('lang').value});
  if(!d.card){alert(d.error||'Something went wrong, please try again.');}
  else{
   const c=d.card;$('res').style.display='block';$('sc').textContent=c.score+' / 100';$('lv').textContent=c.level;
   $('bar').style.width=c.score+'%';
   $('star').innerHTML='';
   for(const k of ['situation','task','action','result']){const s=document.createElement('span');s.textContent=(c.star[k]?'✅ ':'⬜ ')+k;if(c.star[k])s.className='on';$('star').appendChild(s);}
   const list=attempts[q]=attempts[q]||[];list.push(c.score);
   $('glow').textContent=list.length>1?('Glow-up: '+(c.score-list[0]>=0?'+':'')+(c.score-list[0])+' points since your first try ✨'):'This is your baseline. Tweak your answer and try again to see your glow-up!';
   $('fb').textContent=d.feedback;$('src').textContent='feedback by: '+d.source;
   $('histc').style.display='block';
   $('hist').textContent=Object.keys(attempts).map(k=>k.slice(0,40)+'... : '+attempts[k].join(' → ')).join('\n');
   $('hist').style.whiteSpace='pre-wrap';
  }
 }catch(e){alert('Oops, the network tripped. Please try again.');}
 busy=false;$('go').disabled=false;$('go').textContent='Score my answer';
}
newQ();
</script></body></html>"""


def resp(d):
    return {"statusCode": 200,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(d, ensure_ascii=False)}


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    if method == "GET":
        return {"statusCode": 200, "headers": {"Content-Type": "text/html; charset=utf-8"}, "body": PAGE}
    try:
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        data = json.loads(raw)
        action = data.get("action")

        if action == "question":
            seen = [str(s)[:300] for s in (data.get("seen") or [])][:10]
            return resp({"question": sw.pick_question(str(data.get("track", "general")), seen)})

        if action == "score":
            question = str(data.get("question", "")).strip()[:300] or "Tell me about yourself."
            answer = str(data.get("answer", "")).strip()[:2500]
            if len(answer) < 5:
                return resp({"error": "Your answer box looks empty. Even two sentences is a great start! 🎤"})
            lang = data.get("lang", "en")
            card = sw.score_answer(answer)
            feedback, source = sw.coach(question, answer, card, lang)
            return resp({"card": card, "feedback": feedback, "source": source})

        if action == "selfcheck":
            return resp(sw.selfcheck())

        return resp({"error": "I did not understand that request."})
    except Exception as e:
        print("ERROR:", repr(e))
        return resp({"error": "That one is on me, not you! Please try again in a moment. 🙏"})
