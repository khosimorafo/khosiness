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
