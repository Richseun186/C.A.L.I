// CALI Schools Performance & Celebration Controller
function registerPerfStore() {
  if (window.Alpine && typeof Alpine.store === 'function') {
    try {
      if (!Alpine.store('perf')) {
        Alpine.store('perf', {
          lowData: localStorage.getItem('cali_low_data') === 'true',
          toggle() {
            this.lowData = !this.lowData;
            localStorage.setItem('cali_low_data', this.lowData);
            if (this.lowData) {
              document.documentElement.classList.add('low-data-mode');
            } else {
              document.documentElement.classList.remove('low-data-mode');
            }
          }
        });
      }
    } catch (e) {
      console.warn('Perf store registration handled:', e);
    }
  }

  if (localStorage.getItem('cali_low_data') === 'true') {
    document.documentElement.classList.add('low-data-mode');
  }
}

document.addEventListener('alpine:init', registerPerfStore);
document.addEventListener('DOMContentLoaded', registerPerfStore);
if (window.Alpine) registerPerfStore();

// Lazy-Loaded Confetti Burst (Only ~4KB injected on demand for high-achieving results)
window.triggerCelebration = function() {
  if (window.Alpine && Alpine.store('perf').lowData) return;

  const scriptId = 'canvas-confetti-script';
  if (!document.getElementById(scriptId)) {
    const script = document.createElement('script');
    script.id = scriptId;
    script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js';
    script.onload = () => {
      runBurst();
    };
    document.body.appendChild(script);
  } else if (window.confetti) {
    runBurst();
  }

  function runBurst() {
    window.confetti({
      particleCount: 70,
      spread: 60,
      origin: { y: 0.65 },
      colors: ['#0284c7', '#10b981', '#f59e0b', '#f43f5e']
    });
  }
};
