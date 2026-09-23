document.addEventListener('click', async (event) => {
  const button = event.target.closest('.copy-code');
  if (!button) return;
  const code = button.parentElement.querySelector('pre code');
  if (!code) return;
  try {
    await navigator.clipboard.writeText(code.textContent);
    const original = button.textContent;
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = original; }, 1200);
  } catch (error) {
    button.textContent = 'Select manually';
  }
});

function manualPageContext() {
  const source = document.querySelector('.detail-main') || document.querySelector('main.content');
  if (!source) return '';
  const copy = source.cloneNode(true);
  copy.querySelectorAll('.snapshot-files, .project-tree-panel, .manual-qa-panel, nav, script').forEach(node => node.remove());
  return (copy.innerText || copy.textContent || '').replace(/\n{3,}/g, '\n\n').trim().slice(0, 30000);
}

function manualPagePath() {
  const path = decodeURIComponent(location.pathname);
  const marker = '/docs/manual/';
  if (location.protocol === 'file:') return path.split(marker)[1] || 'index.html';
  return path.replace(/^\//, '') || 'index.html';
}

function createManualTutor() {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'manual-qa-launcher';
  button.textContent = 'Ask about this page';
  button.setAttribute('aria-haspopup', 'dialog');
  button.setAttribute('aria-expanded', 'false');

  const panel = document.createElement('section');
  panel.className = 'manual-qa-panel';
  panel.id = 'manual-qa-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Ask the manual tutor');
  panel.hidden = true;
  panel.innerHTML = `
    <div class="manual-qa-head">
      <div><strong>Ask the manual tutor</strong><small>Current page: ${document.title.replace(/</g, '&lt;')}</small></div>
      <button class="manual-qa-close" type="button" aria-label="Close questions">×</button>
    </div>
    <div class="manual-qa-setup" hidden></div>
    <div class="manual-qa-messages" role="log" aria-live="polite" aria-relevant="additions text"></div>
    <div class="manual-qa-suggestions">
      <button type="button">What failure does this stage prevent?</button>
      <button type="button">Quiz me on this stage.</button>
      <button type="button">What should I validate before moving on?</button>
    </div>
    <form class="manual-qa-form">
      <label for="manual-qa-question">Your question</label>
      <textarea id="manual-qa-question" rows="3" maxlength="2000" placeholder="Ask about a boundary, code example, or validation gate…" required></textarea>
      <div class="manual-qa-actions"><span class="manual-qa-status">Questions stay in this tab.</span><button type="submit">Ask</button></div>
    </form>`;

  const messages = panel.querySelector('.manual-qa-messages');
  const textarea = panel.querySelector('textarea');
  const submit = panel.querySelector('[type="submit"]');
  const status = panel.querySelector('.manual-qa-status');
  const history = [];
  const servedHere = location.protocol === 'http:' &&
    ['127.0.0.1', 'localhost'].includes(location.hostname);

  function addMessage(role, content) {
    const message = document.createElement('div');
    message.className = `manual-qa-message manual-qa-${role}`;
    const label = document.createElement('strong');
    label.textContent = role === 'user' ? 'You' : 'Tutor';
    const body = document.createElement('p');
    body.textContent = content;
    message.append(label, body);
    messages.append(message);
    messages.scrollTop = messages.scrollHeight;
  }

  if (!servedHere) {
    const setup = panel.querySelector('.manual-qa-setup');
    const target = `http://127.0.0.1:8765/${manualPagePath()}`;
    setup.hidden = false;
    setup.innerHTML = '<strong>Start the local tutor first</strong><p>From the repository root, run:</p><code>python docs/manual/manual_qa_server.py</code><p>Then open this page through the local server:</p>';
    const link = document.createElement('a');
    link.href = target;
    link.textContent = target;
    setup.append(link);
    panel.querySelector('.manual-qa-form').hidden = true;
    panel.querySelector('.manual-qa-suggestions').hidden = true;
  } else {
    addMessage('tutor', 'Ask about this stage. I will use the visible manual page as context and say when it does not answer your question.');
  }

  function openPanel() {
    panel.hidden = false;
    button.setAttribute('aria-expanded', 'true');
    if (servedHere) textarea.focus();
    else panel.querySelector('.manual-qa-close').focus();
  }
  function closePanel() {
    panel.hidden = true;
    button.setAttribute('aria-expanded', 'false');
    button.focus();
  }
  button.addEventListener('click', () => panel.hidden ? openPanel() : closePanel());
  panel.querySelector('.manual-qa-close').addEventListener('click', closePanel);
  panel.addEventListener('keydown', event => {
    if (event.key === 'Escape') closePanel();
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      panel.querySelector('form').requestSubmit();
    }
  });
  panel.querySelectorAll('.manual-qa-suggestions button').forEach(suggestion => {
    suggestion.addEventListener('click', () => {
      textarea.value = suggestion.textContent;
      panel.querySelector('form').requestSubmit();
    });
  });
  panel.querySelector('form').addEventListener('submit', async event => {
    event.preventDefault();
    const question = textarea.value.trim();
    if (!question || submit.disabled) return;
    textarea.value = '';
    addMessage('user', question);
    submit.disabled = true;
    status.textContent = 'Thinking…';
    try {
      const selectedText = String(window.getSelection() || '').slice(0, 4000);
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          page: manualPagePath(),
          context: manualPageContext(),
          selected_text: selectedText,
          history: history.slice(-6),
          question
        })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
      addMessage('tutor', result.answer);
      history.push({role: 'user', content: question}, {role: 'assistant', content: result.answer});
      status.textContent = 'Questions stay in this tab.';
    } catch (error) {
      addMessage('tutor', `I could not answer: ${error.message}`);
      status.textContent = 'Check the local tutor server.';
      textarea.value = question;
    } finally {
      submit.disabled = false;
      textarea.focus();
    }
  });

  document.body.append(button, panel);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createManualTutor);
} else {
  createManualTutor();
}
