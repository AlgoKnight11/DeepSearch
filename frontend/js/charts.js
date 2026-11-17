/**
 * DeepSearch Forensics - Chart.js Telemetry Configurations
 * Multi-trace rPPG Waves & FFT Power Spectral Density
 */

let rppgChart = null;
let fftChart = null;

// Color Palette Constants
const COLOR_FOREHEAD = '#00F0FF'; // Primary Cyan
const COLOR_LCHEEK   = '#6366F1'; // Neon Indigo
const COLOR_RCHEEK   = '#10B981'; // Vibrant Emerald
const COLOR_CHIN     = '#F59E0B'; // Warning Amber
const COLOR_GRID     = 'rgba(45, 55, 72, 0.45)';
const COLOR_TEXT     = '#64748B';

/**
 * Initializes the Multi-Trace rPPG Pulse Waveform Chart with flat zero data
 */
function initRppgChart() {
  const canvasElem = document.getElementById('rppg-chart-canvas');
  if (!canvasElem || typeof Chart === 'undefined') return;
  const ctx = canvasElem.getContext('2d');
  
  // 60 sample points across ~4 seconds
  const sampleCount = 60;
  const labels = [];
  for (let i = sampleCount; i >= 0; i--) {
    if (i % 10 === 0) {
      labels.push(`-${(i * 0.067).toFixed(1)}s`);
    } else {
      labels.push('');
    }
  }

  // Baseline zero data
  const flatLine = new Array(sampleCount + 1).fill(0);

  rppgChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Forehead',
          borderColor: COLOR_FOREHEAD,
          borderWidth: 2,
          data: [...flatLine],
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: 'L-Cheek',
          borderColor: COLOR_LCHEEK,
          borderWidth: 1.8,
          data: [...flatLine],
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: 'R-Cheek',
          borderColor: COLOR_RCHEEK,
          borderWidth: 1.8,
          data: [...flatLine],
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: 'Chin',
          borderColor: COLOR_CHIN,
          borderWidth: 1.8,
          data: [...flatLine],
          tension: 0.4,
          pointRadius: 0,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(10, 14, 23, 0.9)',
          borderColor: '#2D3748',
          borderWidth: 1,
          titleFont: { family: 'Inter', size: 10 },
          bodyFont: { family: 'JetBrains Mono', size: 10 }
        }
      },
      scales: {
        x: {
          grid: { color: COLOR_GRID, drawTicks: false },
          ticks: { color: COLOR_TEXT, font: { family: 'JetBrains Mono', size: 8.5 }, autoSkip: false }
        },
        y: {
          min: -1.6,
          max: 1.6,
          grid: { color: COLOR_GRID, drawTicks: false },
          ticks: {
            stepSize: 0.8,
            color: COLOR_TEXT,
            font: { family: 'JetBrains Mono', size: 8.5 }
          }
        }
      }
    }
  });
}

/**
 * Initializes the FFT Frequency Domain Spectral Power Chart with zero bars
 */
function initFftChart() {
  const canvasElem = document.getElementById('fft-chart-canvas');
  if (!canvasElem || typeof Chart === 'undefined') return;
  const ctx = canvasElem.getContext('2d');
  
  // 36 frequency bins from 0.5 Hz to 3.5 Hz
  const bins = 36;
  const labels = [];
  const data = new Array(bins).fill(0);

  for (let i = 0; i < bins; i++) {
    const freq = 0.5 + (i * (3.0 / bins));
    if (i % 5 === 0) {
      labels.push(`${freq.toFixed(2)}Hz`);
    } else {
      labels.push('');
    }
  }

  fftChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Spectral Energy',
        data: data,
        backgroundColor: 'rgba(45, 55, 72, 0.35)',
        borderRadius: 2,
        barPercentage: 0.75
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(10, 14, 23, 0.9)',
          borderColor: '#2D3748',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `Power: ${ctx.raw.toFixed(3)}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: COLOR_TEXT, font: { family: 'JetBrains Mono', size: 8 }, autoSkip: false }
        },
        y: {
          min: 0,
          max: 1.1,
          grid: { color: COLOR_GRID, drawTicks: false },
          ticks: {
            stepSize: 0.2,
            color: COLOR_TEXT,
            font: { family: 'JetBrains Mono', size: 8 }
          }
        }
      }
    }
  });
}

/**
 * Clears and resets charts to zero/idle state
 */
function resetChartsToZero() {
  if (rppgChart) {
    const flat = new Array(61).fill(0);
    rppgChart.data.datasets.forEach(ds => ds.data = [...flat]);
    rppgChart.update('none');
  }

  if (fftChart) {
    fftChart.data.datasets[0].data = new Array(36).fill(0);
    fftChart.data.datasets[0].backgroundColor = 'rgba(45, 55, 72, 0.35)';
    fftChart.update('none');
  }

  const bpmElem = document.getElementById('detected-bpm-text');
  if (bpmElem) bpmElem.innerText = '-- BPM (-- Hz)';

  const snrElem = document.getElementById('snr-val-text');
  const snrBar = document.getElementById('snr-fill-bar');
  if (snrElem) snrElem.innerText = '-- dB';
  if (snrBar) snrBar.style.width = '0%';

  const sampleTag = document.getElementById('fft-sample-rate-tag');
  if (sampleTag) sampleTag.innerText = 'Sampling: -- Hz';

  const waveTag = document.getElementById('wave-sync-tag');
  if (waveTag) {
    waveTag.className = 'card-tag standby';
    waveTag.innerText = 'Awaiting Input';
  }
}

/**
 * Updates rPPG waveform traces smoothly in real time
 */
let timeTick = 0;
function updateRppgWaveforms(isAuthentic = true) {
  if (!rppgChart) return;
  timeTick += 0.15;

  if (isAuthentic) {
    // In authentic faces, all patches rise and fall in biological harmony
    rppgChart.data.datasets[0].data = generateWaveSlice(timeTick, 0, 0.03);      // Forehead
    rppgChart.data.datasets[1].data = generateWaveSlice(timeTick, 0.08, 0.04);   // L-Cheek
    rppgChart.data.datasets[2].data = generateWaveSlice(timeTick, 0.06, 0.04);   // R-Cheek
    rppgChart.data.datasets[3].data = generateWaveSlice(timeTick, 0.12, 0.05);   // Chin
  } else {
    // In deepfakes, phases are scattered or frequencies clash
    rppgChart.data.datasets[0].data = generateWaveSlice(timeTick * 1.3, 0, 0.2);
    rppgChart.data.datasets[1].data = generateWaveSlice(timeTick * 0.7, 2.1, 0.25);
    rppgChart.data.datasets[2].data = generateWaveSlice(timeTick * 1.5, 4.2, 0.22);
    rppgChart.data.datasets[3].data = generateWaveSlice(timeTick * 0.9, 1.1, 0.3);
  }
  
  rppgChart.update('none');
}

function generateWaveSlice(timeOffset, phase, noise) {
  return Array.from({ length: 61 }, (_, i) => {
    const t = timeOffset + (i / 60) * Math.PI * 8;
    return Math.sin(t + phase) * 1.05 + (Math.random() - 0.5) * noise;
  });
}

/**
 * Updates the FFT power spectrum based on analysis results
 */
function updateFftSpectrum(peakFreq = 1.21, snr = 18.4, isAuthentic = true, fps = 30) {
  if (!fftChart) return;
  
  const bins = 36;
  const newData = [];
  
  for (let i = 0; i < bins; i++) {
    const freq = 0.5 + (i * (3.0 / bins));
    if (isAuthentic) {
      const dist = Math.abs(freq - peakFreq);
      let val = Math.exp(-Math.pow(dist / 0.16, 2)) * 0.95;
      val += Math.random() * 0.06;
      newData.push(val);
    } else {
      let val = (Math.random() * 0.32) + 0.05;
      if (Math.abs(freq - 1.1) < 0.2) val += 0.25;
      if (Math.abs(freq - 2.4) < 0.2) val += 0.3;
      newData.push(val);
    }
  }

  fftChart.data.datasets[0].data = newData;
  fftChart.data.datasets[0].backgroundColor = newData.map(v => 
    v > 0.4 ? 'rgba(0, 240, 255, 0.85)' : 'rgba(59, 130, 246, 0.35)'
  );
  fftChart.update('none');

  // Update DOM badges
  const bpmValue = (peakFreq * 60).toFixed(1);
  const bpmElem = document.getElementById('detected-bpm-text');
  if (bpmElem) bpmElem.innerText = `${bpmValue} BPM (${peakFreq.toFixed(2)} Hz)`;
  
  const snrElem = document.getElementById('snr-val-text');
  const snrBar = document.getElementById('snr-fill-bar');
  if (snrElem) snrElem.innerText = `${snr > 0 ? '+' : ''}${snr.toFixed(1)} dB`;
  if (snrBar) {
    const pct = Math.min(Math.max((snr + 10) / 30 * 100, 10), 100);
    snrBar.style.width = `${pct}%`;
  }

  const sampleTag = document.getElementById('fft-sample-rate-tag');
  if (sampleTag) sampleTag.innerText = `Sampling: ${fps} Hz`;

  const waveTag = document.getElementById('wave-sync-tag');
  if (waveTag) {
    waveTag.className = 'card-tag';
    waveTag.innerText = 'Real-time Synced';
  }
}
