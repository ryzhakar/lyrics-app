(function(){
  'use strict';

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  class SongTextDisintegration {
    constructor(){
      this.items = [];
      this.zonePx = 56;
      this.maxActive = 12;
      this.activated = false;
      this.grainStart = 0.35;
      this.displacementStart = 0.85;
      this.svgDefs = this.ensureSvgDefs();
      this.filterPool = this.createFilterPool(this.maxActive);
      this.elementToFilterIndex = new Map();
      this.filterOwnerByIndex = new Array(this.maxActive).fill(null);
      this.registerTargets();
      this.bind();
      if (this.activated) this.update();
    }

    ensureSvgDefs(){
      let svg = document.getElementById('disintegration-svg-root');
      if (!svg){
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('id', 'disintegration-svg-root');
        svg.setAttribute('style', 'position:absolute;width:0;height:0;');
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        svg.appendChild(defs);
        document.body.appendChild(svg);
      }
      return svg.querySelector('defs');
    }

    registerTargets(){
      const nodes = document.querySelectorAll('.song-container .song-section pre.lyrics, .song-container .song-section pre.chords, .song-container .song-section .section-header');
      let idx = 0;
      nodes.forEach(node => this.register(node, idx++));
    }

    register(element, seed){
      this.items.push({ element, seed, lastProgress: -1 });
    }

    createFilterPool(n){
      const pool = [];
      for (let i = 0; i < n; i++){
        const id = `grain-scatter-${i}`;
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.setAttribute('id', id);
        filter.setAttribute('x', '-25%');
        filter.setAttribute('y', '-15%');
        filter.setAttribute('width', '150%');
        filter.setAttribute('height', '130%');
        filter.setAttribute('color-interpolation-filters', 'sRGB');
        filter.innerHTML = `
          <feTurbulence id="grain-turb-${i}" type="fractalNoise" baseFrequency="0.6 0.6" numOctaves="1" seed="${i * 911}" result="grainNoise${i}"/>
          <feComponentTransfer in="grainNoise${i}" result="grainMask${i}">
            <feFuncA id="grain-thresh-${i}" type="discrete" tableValues="1 1 1 1 1 1 1 1 1 1"/>
          </feComponentTransfer>
          <feComposite in="SourceGraphic" in2="grainMask${i}" operator="in" result="grained${i}"/>
          <feTurbulence id="scatter-turb-${i}" type="turbulence" baseFrequency="0.06 0.06" numOctaves="2" seed="${i * 131}" result="scatterNoise${i}"/>
          <feDisplacementMap id="scatter-disp-${i}" in="grained${i}" in2="scatterNoise${i}" scale="0" xChannelSelector="R" yChannelSelector="G" result="final${i}"/>
          <feMerge><feMergeNode in="final${i}"/></feMerge>
        `;
        this.svgDefs.appendChild(filter);
        pool.push({
          id,
          grainTurbulence: filter.querySelector(`#grain-turb-${i}`),
          grainThreshold: filter.querySelector(`#grain-thresh-${i}`),
          scatterTurbulence: filter.querySelector(`#scatter-turb-${i}`),
          scatterDisplace: filter.querySelector(`#scatter-disp-${i}`),
          owner: null
        });
      }
      return pool;
    }

    computeZone(){
      const header = document.querySelector('.song-header');
      const topbarGap = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--topbar-gap') || '56');
      const boundary = header ? header.getBoundingClientRect().bottom : topbarGap;
      const thickness = Math.min(72, Math.max(24, this.zonePx));
      const half = thickness / 2;
      const start = boundary - half;
      const end = boundary + half;
      return { start, end };
    }

    progressFor(element, zone){
      const rect = element.getBoundingClientRect();
      if (rect.bottom <= zone.start) return 1;
      if (rect.top >= zone.end) return 0;
      const h = zone.end - zone.start;
      const d = zone.end - rect.top;
      return Math.max(0, Math.min(1, d / h));
    }

    easeInOutQuad(t){
      return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    prng01(seed, n){
      const v = Math.sin(seed * 104729 + n * 13007) * 43758.5453;
      return v - Math.floor(v);
    }

    grainThreshold(progress, seed){
      const steps = 24;
      if (progress <= this.grainStart) return Array(steps).fill('1').join(' ');
      if (progress >= 0.99) return Array(steps).fill('0').join(' ');
      const values = [];
      const t = Math.max(0, Math.min(1, (progress - this.grainStart) / (1 - this.grainStart)));
      const density = Math.pow(1 - t, 2.6);
      for (let i = 0; i < steps; i++){
        const threshold = i / steps;
        if (threshold < density * 0.5) values.push('1');
        else if (threshold < density) values.push(this.prng01(seed, i) < density ? '1' : '0');
        else values.push('0');
      }
      return values.join(' ');
    }

    updateActiveItem(filter, item, progress){
      const p = Math.max(0, Math.min(1, progress));
      const eased = this.easeInOutQuad(p);
      const grainPhase = p <= this.grainStart ? 0 : (p - this.grainStart) / (1 - this.grainStart);
      const grainFreq = Math.min(1.3, 0.45 + (Math.max(0, Math.min(1, grainPhase)) * 0.95));
      const thresh = this.grainThreshold(progress, item.seed);
      let scatterScale = 0;
      let scatterBase = '0.010';
      if (p > this.displacementStart){
        const dispPhase = (p - this.displacementStart) / (1 - this.displacementStart);
        scatterScale = Math.min(64, Math.max(0, dispPhase) * 64);
        scatterBase = (0.02 + (1 - dispPhase) * 0.04 + this.prng01(item.seed, 999) * 0.02).toFixed(3);
      }
      if (filter.grainTurbulence) filter.grainTurbulence.setAttribute('baseFrequency', `${grainFreq} ${grainFreq}`);
      if (filter.grainThreshold) filter.grainThreshold.setAttribute('tableValues', thresh);
      if (filter.scatterTurbulence) filter.scatterTurbulence.setAttribute('baseFrequency', `${scatterBase} ${scatterBase}`);
      if (filter.scatterDisplace) filter.scatterDisplace.setAttribute('scale', String(scatterScale));
    }

    update(){
      if (!this.activated) return;
      const zone = this.computeZone();
      const margin = this.zonePx * 1.5;
      const near = [];
      for (let i = 0; i < this.items.length; i++){
        const it = this.items[i];
        const rect = it.element.getBoundingClientRect();
        const dist = (rect.top > zone.end) ? (rect.top - zone.end) : (zone.start - rect.bottom);
        if (dist < margin){ near.push({ idx: i, dist: Math.abs(dist) }); }
      }
      near.sort((a,b)=>a.dist-b.dist);
      const selected = near.slice(0, this.maxActive).map(v=>v.idx);
      const selectedSet = new Set(selected);
      for (let fi = 0; fi < this.filterPool.length; fi++){
        const owner = this.filterOwnerByIndex[fi];
        if (owner !== null && !selectedSet.has(owner)){
          const el = this.items[owner].element;
          el.style.filter = 'none';
          el.style.willChange = 'auto';
          this.elementToFilterIndex.delete(el);
          this.filterOwnerByIndex[fi] = null;
          this.filterPool[fi].owner = null;
        }
      }
      for (const idx of selected){
        const el = this.items[idx].element;
        if (!this.elementToFilterIndex.has(el)){
          const freeIndex = this.filterOwnerByIndex.indexOf(null);
          if (freeIndex === -1) continue;
          this.elementToFilterIndex.set(el, freeIndex);
          this.filterOwnerByIndex[freeIndex] = idx;
          this.filterPool[freeIndex].owner = idx;
          el.style.filter = `url(#${this.filterPool[freeIndex].id})`;
          el.style.willChange = 'filter';
        }
      }
      for (let fi = 0; fi < this.filterPool.length; fi++){
        const ownerIdx = this.filterOwnerByIndex[fi];
        if (ownerIdx === null) continue;
        const item = this.items[ownerIdx];
        const progress = this.progressFor(item.element, zone);
        if (Math.abs(progress - item.lastProgress) < 0.01 && progress !== 0) continue;
        this.updateActiveItem(this.filterPool[fi], item, progress);
        item.lastProgress = progress;
      }
    }

    bind(){
      let ticking = false;
      window.addEventListener('scroll', () => {
        this.activated = true;
        if (!ticking){
          requestAnimationFrame(() => { this.update(); ticking = false; });
          ticking = true;
        }
      }, { passive: true });
      window.addEventListener('resize', () => this.update(), { passive: true });
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    new SongTextDisintegration();
  });
})();
