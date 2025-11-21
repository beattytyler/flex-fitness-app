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
      if (!progress) {
        // still schedule removal even without visual bar
        setTimeout(() => removeAlert(alert), duration);
        return;
      }

      // initialize transform-based animation
      progress.style.transformOrigin = 'left';
      progress.style.transform = 'scaleX(1)';
      // set a transition; we'll adjust durations on pause/resume
      progress.style.transition = `transform ${duration}ms linear`;

      // start animation on next frame
      requestAnimationFrame(() => requestAnimationFrame(() => {
        progress.style.transform = 'scaleX(0)';
      }));

      let start = Date.now();
      let timeoutId = setTimeout(() => removeAlert(alert), duration);
      let remaining = duration;

      // Pause / resume on hover
      alert.addEventListener('mouseenter', () => {
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        const elapsed = Date.now() - start;
        remaining = Math.max(0, duration - elapsed);
        // freeze animation
        progress.style.transition = 'none';
        // compute current scale and set it explicitly
        const currentScale = Math.max(0, 1 - (elapsed / duration));
        progress.style.transform = `scaleX(${currentScale})`;
      });

      alert.addEventListener('mouseleave', () => {
        // resume animation
        start = Date.now();
        // force reflow then set transition for the remaining time
        requestAnimationFrame(() => {
          progress.style.transition = `transform ${remaining}ms linear`;
          progress.style.transform = 'scaleX(0)';
          timeoutId = setTimeout(() => removeAlert(alert), remaining);
        });
      });
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
