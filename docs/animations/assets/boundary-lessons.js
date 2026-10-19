// Self-paced conceptual scenes only: no tools, approvals, or persistence run here.
(() => {
  const $ = id => document.getElementById(id);
  const embedded = new URLSearchParams(location.search).get('embedded') === '1';
  if (embedded) document.body.classList.add('embedded');
  document.documentElement.classList.add('enhanced');
  const scenes = [...document.querySelectorAll('.scene')];
  const records = [...document.querySelectorAll('.record')];
  let index = 0, playing = false, timer = null;
  const buttons = scenes.map((scene, i) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'dot';
    button.textContent = i + 1;
    button.setAttribute('aria-label', 'Scene ' + scene.querySelector('h3').textContent);
    button.addEventListener('click', () => { stop(); show(i); });
    $('dots').append(button);
    return button;
  });
  function stop() {
    playing = false;
    clearTimeout(timer);
    timer = null;
    document.body.classList.remove('playing');
    $('play').textContent = index === scenes.length - 1 ? 'Replay' : 'Play';
    $('play').setAttribute('aria-pressed', 'false');
  }
  function schedule() {
    clearTimeout(timer);
    if (playing) timer = setTimeout(() => { show(index + 1); schedule(); }, 11000);
  }
  function show(next) {
    index = Math.max(0, Math.min(scenes.length - 1, next));
    const scene = scenes[index];
    const failed = scene.dataset.error === 'true';
    scenes.forEach((item, i) => { item.hidden = i !== index; });
    buttons.forEach((button, i) => {
      if (i === index) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    $('count').textContent = 'Scene ' + (index + 1) + ' / ' + scenes.length;
    $('previous').disabled = index === 0;
    $('next').disabled = index === scenes.length - 1;
    $('progress').style.width = ((index + 1) / scenes.length * 100) + '%';
    records.forEach(record => {
      const active = record.dataset.node === scene.dataset.focus;
      record.classList.toggle('selected', active);
      record.classList.toggle('rejected', active && failed);
      record.querySelector('.badge').textContent = active ? 'In focus for this scene' : 'Separate responsibility';
    });
    $('query').textContent = scene.querySelector('.request').textContent;
    $('view').textContent = scene.querySelector('.result').textContent;
    $('trace').textContent = scene.querySelector('.boundary').textContent;
    $('status').textContent = scene.querySelector('.scene-status').textContent;
    $('status').classList.toggle('error', failed);
    if (index === scenes.length - 1) stop();
    if (!playing) $('play').textContent = index === scenes.length - 1 ? 'Replay' : 'Play';
  }
  $('previous').addEventListener('click', () => { stop(); show(index - 1); });
  $('next').addEventListener('click', () => { stop(); show(index + 1); });
  $('play').addEventListener('click', () => {
    if (playing) { stop(); return; }
    if (index === scenes.length - 1) show(0);
    playing = true;
    document.body.classList.add('playing');
    $('play').textContent = 'Pause';
    $('play').setAttribute('aria-pressed', 'true');
    schedule();
  });
  document.addEventListener('keydown', event => {
    if (event.target.closest?.('textarea,input,select,button,a,[contenteditable],.manual-qa-panel')) return;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault(); stop(); show(index + (event.key === 'ArrowRight' ? 1 : -1));
    } else if (event.code === 'Space') { event.preventDefault(); $('play').click(); }
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  window.manualTutorContext = document.title + '\nConceptual simulation only; no runtime or stage credit.\n'
    + document.querySelector('.notice').textContent + '\n'
    + document.querySelector('.primer').textContent + '\n\n'
    + scenes.map(scene => scene.textContent).join('\n\n');
  show(0); stop();
  if (embedded) {
    const shell = document.querySelector('.shell');
    const report = () => parent.postMessage({type: 'khosiness-animation-height', height: Math.ceil(shell.getBoundingClientRect().bottom) + 2}, '*');
    new ResizeObserver(report).observe(shell);
    window.addEventListener('message', event => {
      if (event.source === parent && event.data?.type === 'khosiness-measure-animation') report();
    });
    window.addEventListener('load', report);
  }
})();
