(function () {
  const DEFAULT_DURATION = 5000; // ms

  function removeAlert(alert) {
    if (!alert) return;
    alert.classList.remove('show');
    setTimeout(() => {
      if (alert.parentNode) alert.parentNode.removeChild(alert);
    }, 300);
  }

  function attachFlashTimers() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
      if (alert.dataset.flashAttached) return;
      alert.dataset.flashAttached = '1';

      const duration = parseInt(alert.dataset.duration, 10) || DEFAULT_DURATION;
      const progress = alert.querySelector('.flash-progress .bar');
      if (progress) {
        // initialize transform-based animation and start it
        progress.style.transformOrigin = 'left';
        progress.style.transform = 'scaleX(1)';
        progress.style.transition = `transform ${duration}ms linear`;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          progress.style.transform = 'scaleX(0)';
        }));
      }

      // remove the alert after the specified duration (no pause-on-hover)
      setTimeout(() => removeAlert(alert), duration);
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    attachFlashTimers();
  });

  // Observe container for dynamically-inserted flashes
  const container = document.querySelector('.container');
  if (container && window.MutationObserver) {
    const obs = new MutationObserver(() => attachFlashTimers());
    obs.observe(container, { childList: true, subtree: true });
  }
})();
