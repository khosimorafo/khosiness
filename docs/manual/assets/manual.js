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

const animationFrame = document.querySelector('.stage-animation iframe');
if (animationFrame) {
  window.addEventListener('message', event => {
    if (event.source !== animationFrame.contentWindow ||
        event.data?.type !== 'khosiness-animation-height') return;
    const height = event.data.height;
    if (typeof height === 'number' && Number.isFinite(height) && height >= 200 && height <= 4000) {
      const measuredHeight = `${Math.ceil(height)}px`;
      if (animationFrame.style.height !== measuredHeight) animationFrame.style.height = measuredHeight;
    }
  });
  animationFrame.addEventListener('load', () => {
    animationFrame.contentWindow.postMessage({type: 'khosiness-measure-animation'}, '*');
  });
}
