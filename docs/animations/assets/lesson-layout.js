// Fullscreen gives a narrow manual iframe the same layout as a standalone lesson.
// No content is scaled down or removed to fit a viewport.
(() => {
  const main = document.querySelector('main');
  const controls = document.querySelector('.controls');
  if (!main || !controls || !document.fullscreenEnabled) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'lesson-expand';
  button.textContent = 'Expand lesson';
  button.setAttribute('aria-pressed', 'false');
  const feedback = document.createElement('p');
  feedback.className = 'layout-feedback';
  feedback.setAttribute('role', 'status');
  feedback.hidden = true;
  controls.append(button);
  document.querySelector('.lesson').append(feedback);
  button.addEventListener('click', async () => {
    feedback.hidden = true;
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await main.requestFullscreen();
    } catch (_) {
      feedback.textContent = 'Fullscreen is unavailable. Open this lesson on its own using the manual’s link.';
      feedback.hidden = false;
    }
  });
  document.addEventListener('fullscreenchange', () => {
    const expanded = document.fullscreenElement === main;
    button.textContent = expanded ? 'Exit expanded lesson' : 'Expand lesson';
    button.setAttribute('aria-pressed', String(expanded));
  });
})();
