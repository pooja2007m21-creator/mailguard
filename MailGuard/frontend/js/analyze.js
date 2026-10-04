$('save').checked = get('save', false);
$('go').onclick = async () => {
  const message = $('message').value.trim();
  if (message.length < 10) return toast('Enter the email message (at least 10 characters).', 'err');
  $('go').disabled = true;
  try {
    const r = await api('/analyze', {method:'POST', body:JSON.stringify({subject:$('subject').value.trim(), message, save:$('save').checked})});
    renderResult(r, $('result')); $('result').scrollIntoView({behavior:'smooth'});
    if (r.id) toast('Analysis saved to history');
  } catch {} finally { $('go').disabled = false; }
};
$('clear').onclick = () => { if (($('message').value || $('subject').value) && !confirm('Clear the email and result?')) return; $('subject').value = ''; $('message').value = ''; $('result').hidden = true; };
