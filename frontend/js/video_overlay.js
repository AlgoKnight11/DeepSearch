/**
 * DeepSearch Forensics - Video & Canvas Overlay Engine
 * Renders 3D Face Mesh wireframes, labeled ROI boxes, and pulsing pulse heatmaps
 */

class VideoOverlayEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    // Active State: only draws face tracking & pulse heatmaps when input is active
    this.isActive = false;

    // Overlay Visibility Flags
    this.showMesh = true;
    this.showForehead = true;
    this.showLCheek = true;
    this.showRCheek = true;
    this.showChin = true;
    this.showHeatmap = true;

    // Simulation & Animation State
    this.animFrame = null;
    this.pulsePhase = 0;
    this.subtleMotion = 0;

    // Standardized Face Landmarks & ROI Centers (Normalized 0.0 - 1.0)
    this.faceAnchor = { x: 0.5, y: 0.52 };
    this.rois = {
      forehead: { name: 'ROI 1: FOREHEAD', color: '#00F0FF', dx: 0, dy: -0.22, w: 0.22, h: 0.12 },
      lcheek:   { name: 'ROI 2: L-CHEEK',  color: '#6366F1', dx: -0.16, dy: 0.04, w: 0.14, h: 0.13 },
      rcheek:   { name: 'ROI 3: R-CHEEK',  color: '#10B981', dx: 0.16, dy: 0.04, w: 0.14, h: 0.13 },
      chin:     { name: 'ROI 4: CHIN',     color: '#F59E0B', dx: 0, dy: 0.25, w: 0.16, h: 0.11 }
    };

    // 3D Mesh Topology Nodes
    this.meshNodes = [
      { x: 0, y: -0.36 }, { x: -0.14, y: -0.32 }, { x: 0.14, y: -0.32 },
      { x: -0.24, y: -0.2 }, { x: 0.24, y: -0.2 }, { x: 0, y: -0.22 },
      { x: -0.09, y: -0.1 }, { x: 0.09, y: -0.1 }, { x: 0, y: -0.04 },
      { x: -0.22, y: 0.02 }, { x: -0.14, y: 0.06 }, { x: 0.14, y: 0.06 }, { x: 0.22, y: 0.02 },
      { x: 0, y: 0.1 }, { x: -0.09, y: 0.16 }, { x: 0.09, y: 0.16 },
      { x: 0, y: 0.24 }, { x: -0.08, y: 0.32 }, { x: 0.08, y: 0.32 }, { x: 0, y: 0.38 }
    ];

    this.meshConnections = [
      [0,1], [0,2], [1,3], [2,4], [1,5], [2,5], [5,8],
      [3,9], [4,12], [9,10], [12,11], [10,13], [11,13],
      [8,13], [10,14], [11,15], [14,16], [15,16], [16,17], [16,18], [17,19], [18,19]
    ];

    window.addEventListener('resize', () => this.resizeCanvas());
    this.resizeCanvas();
    this.startRenderLoop();
  }

  resizeCanvas() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  startRenderLoop() {
    const loop = () => {
      this.render();
      this.animFrame = requestAnimationFrame(loop);
    };
    loop();
  }

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    if (!w || !h) return;

    ctx.clearRect(0, 0, w, h);

    // If no video or webcam has been provided, draw the standby target HUD
    if (!this.isActive) {
      this.drawStandbyHUD(ctx, w, h);
      return;
    }

    this.pulsePhase += 0.08;
    this.subtleMotion += 0.015;
    
    // Natural slight head drift
    const driftX = Math.sin(this.subtleMotion) * (w * 0.008);
    const driftY = Math.cos(this.subtleMotion * 0.8) * (h * 0.006);
    const centerX = w * this.faceAnchor.x + driftX;
    const centerY = h * this.faceAnchor.y + driftY;
    const faceScale = Math.min(w, h) * 0.82;

    // 1. Draw Blood Volume Pulse Heatmaps
    if (this.showHeatmap) {
      const pulseOpacity = 0.18 + Math.sin(this.pulsePhase) * 0.12;
      this.drawPulseHeatmaps(ctx, centerX, centerY, faceScale, pulseOpacity);
    }

    // 2. Draw 3D Face Mesh Wireframe
    if (this.showMesh) {
      this.drawFaceMesh(ctx, centerX, centerY, faceScale);
    }

    // 3. Draw Labeled ROI Polygons
    this.drawRois(ctx, centerX, centerY, faceScale);
  }

  drawStandbyHUD(ctx, w, h) {
    ctx.save();
    const cx = w / 2;
    const cy = h / 2;

    // Subtle dark grid
    ctx.strokeStyle = 'rgba(45, 55, 72, 0.25)';
    ctx.lineWidth = 1;

    ctx.beginPath();
    ctx.moveTo(cx - 60, cy); ctx.lineTo(cx + 60, cy);
    ctx.moveTo(cx, cy - 60); ctx.lineTo(cx, cy + 60);
    ctx.stroke();

    // Center circular reticle
    ctx.beginPath();
    ctx.arc(cx, cy, 40, 0, Math.PI * 2);
    ctx.setLineDash([4, 6]);
    ctx.strokeStyle = 'rgba(100, 116, 139, 0.4)';
    ctx.stroke();

    // Corner brackets for video frame
    const pad = 16;
    const blen = 12;
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgba(100, 116, 139, 0.35)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    // TL
    ctx.moveTo(pad, pad + blen); ctx.lineTo(pad, pad); ctx.lineTo(pad + blen, pad);
    // TR
    ctx.moveTo(w - pad - blen, pad); ctx.lineTo(w - pad, pad); ctx.lineTo(w - pad, pad + blen);
    // BL
    ctx.moveTo(pad, h - pad - blen); ctx.lineTo(pad, h - pad); ctx.lineTo(pad + blen, h - pad);
    // BR
    ctx.moveTo(w - pad - blen, h - pad); ctx.lineTo(w - pad, h - pad); ctx.lineTo(w - pad, h - pad - blen);
    ctx.stroke();

    // Status label
    ctx.fillStyle = '#64748B';
    ctx.font = 'bold 9px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('OPTICAL SENSOR IDLE', cx, cy + 65);

    ctx.restore();
  }

  drawPulseHeatmaps(ctx, cx, cy, scale, opacity) {
    ctx.save();
    const spots = [
      { x: cx, y: cy + (this.rois.forehead.dy * scale), r: scale * 0.13, color: '0, 240, 255' },
      { x: cx + (this.rois.lcheek.dx * scale), y: cy + (this.rois.lcheek.dy * scale), r: scale * 0.11, color: '99, 102, 241' },
      { x: cx + (this.rois.rcheek.dx * scale), y: cy + (this.rois.rcheek.dy * scale), r: scale * 0.11, color: '16, 185, 129' },
      { x: cx, y: cy + (this.rois.chin.dy * scale), r: scale * 0.09, color: '245, 158, 11' }
    ];

    spots.forEach(s => {
      const grad = ctx.createRadialGradient(s.x, s.y, 2, s.x, s.y, s.r);
      grad.addColorStop(0, `rgba(${s.color}, ${opacity})`);
      grad.addColorStop(1, `rgba(${s.color}, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.restore();
  }

  drawFaceMesh(ctx, cx, cy, scale) {
    ctx.save();
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.45)';
    ctx.fillStyle = '#6366F1';
    ctx.lineWidth = 1;

    const transformed = this.meshNodes.map(n => ({
      x: cx + n.x * scale,
      y: cy + n.y * scale
    }));

    ctx.beginPath();
    this.meshConnections.forEach(([i1, i2]) => {
      ctx.moveTo(transformed[i1].x, transformed[i1].y);
      ctx.lineTo(transformed[i2].x, transformed[i2].y);
    });
    ctx.stroke();

    transformed.forEach(pt => {
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 1.8, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.restore();
  }

  drawRois(ctx, cx, cy, scale) {
    ctx.save();

    const roiConfigs = [
      { key: 'forehead', visible: this.showForehead },
      { key: 'lcheek',   visible: this.showLCheek },
      { key: 'rcheek',   visible: this.showRCheek },
      { key: 'chin',     visible: this.showChin }
    ];

    roiConfigs.forEach(({ key, visible }) => {
      if (!visible) return;
      const r = this.rois[key];
      const rx = cx + (r.dx * scale) - (r.w * scale) / 2;
      const ry = cy + (r.dy * scale) - (r.h * scale) / 2;
      const rw = r.w * scale;
      const rh = r.h * scale;

      ctx.strokeStyle = r.color;
      ctx.lineWidth = 1.6;
      ctx.strokeRect(rx, ry, rw, rh);

      ctx.fillStyle = r.color;
      ctx.globalAlpha = 0.08;
      ctx.fillRect(rx, ry, rw, rh);
      ctx.globalAlpha = 1.0;

      this.drawCornerBrackets(ctx, rx, ry, rw, rh, r.color);

      ctx.fillStyle = r.color;
      ctx.font = 'bold 9px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(r.name, rx + rw / 2, ry - 5);
    });

    ctx.restore();
  }

  drawCornerBrackets(ctx, x, y, w, h, color) {
    const len = 6;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    ctx.moveTo(x, y + len); ctx.lineTo(x, y); ctx.lineTo(x + len, y);
    ctx.moveTo(x + w - len, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + len);
    ctx.moveTo(x, y + h - len); ctx.lineTo(x, y + h); ctx.lineTo(x + len, y + h);
    ctx.moveTo(x + w - len, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - len);
    ctx.stroke();
  }
}
