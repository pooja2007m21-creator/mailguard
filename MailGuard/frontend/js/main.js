const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const get = (k,d) => { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } };
const put = (k,v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
const NAMES = {safe:'Safe', spam:'Spam', phishing:'Phishing'};
function toast(msg, type='ok') { const t = document.createElement('div'); t.className = 'toast ' + type; t.textContent = msg; $('toasts').appendChild(t); setTimeout(() => t.remove(), 4000); }
async function api(path, opt={}) {
  try {
    const r = await fetch('/api' + path, {headers:{'Content-Type':'application/json'}, ...opt});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || 'Request failed.');
    return d;
  } catch (e) { toast(e.message === 'Failed to fetch' ? 'Cannot reach the server. Is Flask running?' : e.message, 'err'); throw e; }
}
function applyTheme() { document.documentElement.dataset.theme = get('dark', false) ? 'dark' : 'light'; if ($('themeBtn')) $('themeBtn').textContent = get('dark', false) ? '☀️ Light' : '🌙 Dark'; }
function renderResult(r, el) {
  const probs = Object.entries(r.probabilities).sort((a,b) => b[1]-a[1]).map(([k,v]) => `<div class="pr"><span>${NAMES[k]||esc(k)}</span><div class="meter"><div class="fill ${esc(k)}" style="width:${v}%"></div></div><b>${v}%</b></div>`).join('');
  const kw = r.keywords.length ? r.keywords.map(k => `<span class="tag" title="Pushes toward ${esc(k.signal)}">${esc(k.word)}</span>`).join('') : '<span class="note">No suspicious keywords found.</span>';
  const links = r.links.length ? '<ul>' + r.links.map(l => `<li class="link"><span class="${l.suspicious?'bad-t':''}">${esc(l.url)}</span>${l.suspicious ? '<br><small>' + l.reasons.map(esc).join('; ') + '</small>' : ' <small>No warning signs found</small>'}</li>`).join('') + '</ul>' : '<p class="note">No links found in this email.</p>';
  const s = r.stats;
  el.innerHTML = `<div class="verdict ${esc(r.label)}"><h2>${NAMES[r.label]||esc(r.label)}</h2><p style="margin:.3rem 0 0">Model confidence: <strong>${r.confidence}%</strong>${r.low_confidence ? ' (low: treat with caution)' : ''}</p></div>
  <div class="card">${probs}</div>
  <div class="card"><h2>Suspicious keywords</h2>${kw}<p class="note">Words that contributed most toward a spam or phishing prediction.</p></div>
  <div class="card"><h2>Links</h2>${links}</div>
  <div class="card"><h2>Text statistics</h2><div class="kv"><div><small>Words</small><b>${s.words}</b></div><div><small>Characters</small><b>${s.characters}</b></div><div><small>Sentences</small><b>${s.sentences}</b></div><div><small>Links</small><b>${s.links}</b></div><div><small>Exclamation marks</small><b>${s.exclamation_marks}</b></div><div><small>Uppercase letters</small><b>${s.uppercase_percent}%</b></div></div></div>
  <p class="note">A machine-learning estimate, not a guarantee. Never click links or share credentials based on this result alone.</p>`;
  el.hidden = false;
}
const page = location.pathname.split('/').pop() || 'index.html';
const nl = (h, t) => `<a href="${h}"${page === h ? ' class="cur" aria-current="page"' : ''}>${t}</a>`;
$('hdr').innerHTML = `<header class="top"><a class="logo" href="index.html">🛡️ MailGuard</a>
<button id="menuBtn" class="icon" aria-label="Toggle menu" aria-expanded="false">☰</button>
<nav id="nav" aria-label="Main">${nl('index.html','Analyze')}${nl('dashboard.html','Dashboard')}${nl('history.html','History')}${nl('about.html','About')}
<button id="setBtn" class="link">Settings</button><button id="themeBtn" class="icon" aria-label="Switch between light and dark mode"></button></nav></header>
<dialog id="dlg" aria-labelledby="dt"><h2 id="dt">Settings</h2>
<label><input type="checkbox" id="sSave"> Save analyses to history by default</label>
<label><input type="checkbox" id="sDark"> Dark mode</label>
<div class="row"><button id="sClear" class="btn danger">Clear history</button><button id="sClose" class="btn primary">Close</button></div></dialog>
<div id="toasts" aria-live="polite"></div>`;
$('sSave').checked = get('save', false); $('sDark').checked = get('dark', false); applyTheme();
$('menuBtn').onclick = () => { const o = $('nav').classList.toggle('open'); $('menuBtn').setAttribute('aria-expanded', o); };
$('themeBtn').onclick = () => { put('dark', !get('dark', false)); $('sDark').checked = get('dark', false); applyTheme(); };
$('setBtn').onclick = () => $('dlg').showModal(); $('sClose').onclick = () => $('dlg').close();
$('sSave').onchange = e => { put('save', e.target.checked); if ($('save')) $('save').checked = e.target.checked; };
$('sDark').onchange = e => { put('dark', e.target.checked); applyTheme(); };
$('sClear').onclick = async () => {
  if (!confirm('Delete all saved analyses? This cannot be undone.')) return;
  await api('/history', {method:'DELETE'}); toast('History cleared'); window.dispatchEvent(new Event('historychanged'));
};
