(async () => {
  const a = await api('/analytics').catch(() => null); if (!a) return;
  $('dTot').textContent = a.total; $('dAvg').textContent = a.avg_confidence + '%'; $('dLinks').textContent = a.suspicious_links;
  $('dDist').innerHTML = ['safe','spam','phishing'].map(k => { const n = a.by_label[k] || 0, p = a.total ? Math.round(100*n/a.total) : 0;
    return `<div class="pr"><span>${NAMES[k]}</span><div class="meter"><div class="fill ${k}" style="width:${p}%"></div></div><b>${n}</b></div>`; }).join('');
  const max = Math.max(1, ...a.per_day.map(d => d.n));
  $('dDays').innerHTML = a.per_day.length ? '<div class="cols">' + a.per_day.map(d => `<div>${d.n}<i style="height:${Math.round(100*d.n/max)}px"></i>${esc(d.day.slice(5))}</div>`).join('') + '</div>' : '<p class="note">No saved analyses in the last 7 days.</p>';
  const m = a.model;
  $('dModel').innerHTML = `<p>Dataset: <strong>${esc(m.dataset)}</strong> · ${m.train_size} training emails · ${m.test_size} held-out test emails</p><p>Held-out test accuracy: <strong>${(m.accuracy*100).toFixed(1)}%</strong></p>` +
    (m.dataset === 'seed_emails.csv' ? '<p class="alert">This is the small synthetic demo dataset, so this accuracy is not a real-world measure. Train on a real dataset (see README).</p>' : '');
})();
