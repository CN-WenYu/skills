// Verify offline playback and collect visual evidence, never grant user approval.
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

const [directory, packagePath, channel = 'chromium', referencePath] = process.argv.slice(2);
const hash = value => createHash('sha256').update(value).digest('hex');
const root = resolve(directory);
const readJSON = async name => JSON.parse(await readFile(join(root, name), 'utf8'));
const manifest = await readJSON('manifest.json');
for (const [name, sha] of Object.entries(manifest.files)) {
  if (hash(await readFile(join(root, name))) !== sha) throw Error(`Draft changed: ${name}`);
}
const animation = await readJSON('animation.json');
const config = await readJSON('config.json');
const report = await readJSON('validation.json');
const rounded = config.optimization?.coordinate_precision !== undefined;
if (rounded && !manifest.unrounded_animation_sha256) throw Error('Rounded draft is missing its unrounded reference hash');
let reference, comparison = {status: 'not_run'};
if (referencePath) {
  const bytes = await readFile(resolve(referencePath));
  reference = JSON.parse(bytes.toString('utf8'));
  if (rounded && hash(bytes) !== manifest.unrounded_animation_sha256) throw Error('Reference must be the matching unrounded draft JSON');
  if (['w','h','fr','ip','op'].some(key => reference[key] !== animation[key])) throw Error('Comparison requires matching canvas and timeline');
  comparison = {status:'measured', reference_sha256:hash(bytes), max_channel_error:0, max_changed_pixels:0, samples:[]};
}
const {chromium} = await import(pathToFileURL(join(resolve(packagePath), 'index.mjs')).href);
const browser = await chromium.launch({headless: true, ...(channel === 'chromium' ? {} : {channel})});
const errors = [], requests = [];
try {
  const page = await browser.newPage({viewport: {width: Math.max(640, animation.w + 80), height: Math.max(760, animation.h + 260)}, deviceScaleFactor: 1});
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
  page.on('request', request => {if (/^https?:/.test(request.url())) requests.push(request.url());});
  await page.route(/^https?:/, route => route.abort());
  await page.goto(pathToFileURL(join(root, 'preview.html')).href);
  await page.waitForFunction(() => window.logoAnimation?.isLoaded);
  const initialized = await page.evaluate(() => window.logoAnimation.renderer.elements.filter(Boolean).length);
  if (initialized !== animation.layers.length) throw Error('Player did not initialize every layer; inspect shape group transforms and player config errors');
  const embedded = await page.locator('#animation-data').textContent();
  if (hash(embedded) !== manifest.files['animation.json']) throw Error('Preview animation differs from delivery JSON');
  if (reference) {
    await page.evaluate(data => {
      const container = document.createElement('div');
      container.style.cssText = `position:absolute;left:-10000px;width:${data.w}px;height:${data.h}px`;
      document.body.appendChild(container);
      window.referenceAnimation = lottie.loadAnimation({container,renderer:'svg',loop:false,autoplay:false,animationData:data});
      window.referenceContainer = container;
    }, reference);
    await page.waitForFunction(() => window.referenceAnimation?.isLoaded);
  }
  const screenshots = join(root, 'frames');
  await mkdir(screenshots, {recursive: true});
  const samples = [], pathsPerFrame = [];
  for (const frame of report.sample_frames) {
    await page.evaluate(frame => window.logoAnimation.goToAndStop(frame, true), frame);
    if (reference) {
      const difference = await page.evaluate(async frame => {
        window.referenceAnimation.goToAndStop(frame,true);
        async function pixels(svg) {
          const canvas = document.createElement('canvas');
          canvas.width = window.logoAnimation.animationData.w; canvas.height = window.logoAnimation.animationData.h;
          const clone = svg.cloneNode(true);
          clone.setAttribute('width',canvas.width); clone.setAttribute('height',canvas.height);
          const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(clone)],{type:'image/svg+xml'}));
          try {
            const image = new Image(); image.src = url; await image.decode();
            const ctx = canvas.getContext('2d'); ctx.drawImage(image,0,0,canvas.width,canvas.height);
            return ctx.getImageData(0,0,canvas.width,canvas.height).data;
          } finally { URL.revokeObjectURL(url); }
        }
        const actual = await pixels(document.querySelector('#animation svg'));
        const original = await pixels(window.referenceContainer.querySelector('svg'));
        let max = 0, changed = 0, squared = 0;
        for (let i=0;i<actual.length;i+=4) {
          let pixelMax = Math.abs(actual[i+3]-original[i+3]);
          for (const matte of [0,255]) for (let c=0;c<3;c++) {
            const a = (actual[i+c]*actual[i+3]+matte*(255-actual[i+3]))/255;
            const b = (original[i+c]*original[i+3]+matte*(255-original[i+3]))/255;
            const delta = Math.abs(a-b); pixelMax = Math.max(pixelMax,delta); squared += delta*delta;
          }
          max = Math.max(max,pixelMax); if (pixelMax>0) changed++;
        }
        return {frame,max_channel_error:max,changed_pixels:changed,black_white_rmse:Math.sqrt(squared/(actual.length/4*6))};
      }, frame);
      comparison.samples.push(difference);
      comparison.max_channel_error = Math.max(comparison.max_channel_error,difference.max_channel_error);
      comparison.max_changed_pixels = Math.max(comparison.max_changed_pixels,difference.changed_pixels);
    }
    const state = await page.evaluate(composition => {
      const svg = document.querySelector('#animation svg');
      const stage = svg.getBoundingClientRect();
      const visible = [...svg.querySelectorAll('path')].filter(path => {
        if (path.closest('defs,mask,clipPath')) return false;
        if (!path.getAttribute('d')) return false;
        const paint = getComputedStyle(path);
        if ((paint.fill === 'none' || Number(paint.fillOpacity) === 0) &&
            (paint.stroke === 'none' || Number(paint.strokeOpacity) === 0 || Number.parseFloat(paint.strokeWidth) === 0)) return false;
        for (let el = path; el && el !== svg; el = el.parentElement) {
          const style = getComputedStyle(el);
          if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) < .001) return false;
        }
        return true;
      });
      const clipped = visible.some(path => {
        const r = path.getBoundingClientRect();
        return r.left < stage.left - 1 || r.top < stage.top - 1 || r.right > stage.right + 1 || r.bottom > stage.bottom + 1;
      });
      const roleBounds = {}, roleOpacity = {}, roleStrokeLengths = {}, roleAnchorY = {}, roleAnchorX = {}, roleRotation = {};
      const names = [...(composition?.icon_layers ?? []), ...(composition?.wordmark_layers ?? []),
                     ...(composition?.export_background !== 'transparent' ? ['Background'] : [])];
      for (const name of names) {
        const item = window.logoAnimation.renderer.elements.find(item => item?.data?.nm === name);
        const element = item?.layerElement;
        if (!element) continue;
        let effectiveOpacity = 1;
        for (let current = element; current && current !== svg; current = current.parentElement) {
          const style = getComputedStyle(current);
          if (style.display === 'none' || style.visibility === 'hidden') { effectiveOpacity = 0; break; }
          effectiveOpacity *= Number(style.opacity);
        }
        roleOpacity[name] = effectiveOpacity;
        const matrix = element.getCTM();
        const anchor = item.data.ks.a.k;
        if (matrix && Array.isArray(anchor)) roleAnchorY[name] = (matrix.b*anchor[0] + matrix.d*anchor[1] + matrix.f) * window.logoAnimation.animationData.h/stage.height;
        if (matrix && Array.isArray(anchor)) {
          roleAnchorX[name] = (matrix.a*anchor[0] + matrix.c*anchor[1] + matrix.e) * window.logoAnimation.animationData.w/stage.width;
          roleRotation[name] = Math.atan2(matrix.b,matrix.a)*180/Math.PI;
        }
        roleStrokeLengths[name] = [...element.querySelectorAll('path')].reduce((length, path) => {
          if (!path.getAttribute('d') || getComputedStyle(path).stroke === 'none') return length;
          return length + path.getTotalLength();
        }, 0);
        const rects = visible.filter(path => element.contains(path)).map(path => path.getBoundingClientRect());
        if (rects.length) roleBounds[name] = [Math.min(...rects.map(r => r.left)), Math.min(...rects.map(r => r.top)),
                                             Math.max(...rects.map(r => r.right)), Math.max(...rects.map(r => r.bottom))];
      }
      return {visiblePaths: visible.length, clipped, roleBounds, roleOpacity, roleStrokeLengths, roleAnchorY, roleAnchorX, roleRotation,
              canvasScale: window.logoAnimation.animationData.h/stage.height};
    }, report.composition);
    if (state.clipped) errors.push(`Visible geometry clips at frame ${frame}`);
    if (report.composition) {
      const c = report.composition;
      for (const entrance of c.entrances) {
        const opacity = state.roleOpacity[entrance.layer];
        if (opacity === undefined) errors.push(`Missing rendered role ${entrance.layer}`);
        else if (entrance.opaque_frame > entrance.start_frame && frame <= entrance.start_frame && opacity > .001)
          errors.push(`${entrance.layer} appeared before its entrance at frame ${frame}`);
        else if (frame >= entrance.opaque_frame && opacity < .999)
          errors.push(`${entrance.layer} did not finish its entrance at frame ${frame}`);
      }
      const icons = c.icon_layers.map(name => state.roleBounds[name]).filter(Boolean);
      const names = c.wordmark_layers.map(name => state.roleBounds[name]).filter(Boolean);
      if (icons.length && names.some(b => b[1] < Math.max(...icons.map(b => b[3])) - 1))
        errors.push(`External application name overlaps the complete icon at frame ${frame}`);
    }
    pathsPerFrame.push(state.visiblePaths);
    const filename = `frame-${String(frame).replace('.', '-')}.png`;
    await page.locator('#stage').screenshot({path: join(screenshots, filename)});
    samples.push({frame, ...state, screenshot: `frames/${filename}`});
  }
  for (const unit of report.composition?.wordmark_motion?.beats ?? []) {
    const baseline = samples.at(-1).roleAnchorY[unit.layer];
    for (const beat of unit.frames) {
      const sample = samples.find(s => Math.abs(s.frame-beat.frame) < .002);
      const actual = sample?.roleAnchorY[unit.layer];
      // Hidden layers need not have their transform updated by Lottie until visible.
      if (sample?.roleOpacity[unit.layer] < .001) continue;
      if (!Number.isFinite(actual) || Math.abs(actual-baseline-beat.offset_y) > 1)
        errors.push(`Name unit ${unit.layer} missed its vertical beat at frame ${beat.frame}`);
    }
  }
  if (!pathsPerFrame.at(-1)) errors.push('Settled frame is blank');
  if (report.composition?.wordmark_layers.length) {
    const final = samples.at(-1), c = report.composition;
    const icons = c.icon_layers.map(name => final.roleBounds[name]).filter(Boolean);
    const names = c.wordmark_layers.map(name => final.roleBounds[name]).filter(Boolean);
    if (!icons.length || !names.length) errors.push('Missing settled icon/name geometry');
    else {
      const gap = (Math.min(...names.map(b => b[1]))-Math.max(...icons.map(b => b[3]))) * final.canvasScale;
      if (Math.abs(gap-c.wordmark_gap) > 1) errors.push('Rendered settled name gap differs from configured gap');
    }
  }
  for (const drawing of report.composition?.drawings ?? []) {
    const full = samples.at(-1).roleStrokeLengths[drawing.layer];
    if (!(full > 0)) { errors.push(`Drawn path ${drawing.layer} is empty at the final frame`); continue; }
    for (const key of drawing.keyframes) {
      const sample = samples.find(item => Math.abs(item.frame-key.frame) < .002);
      if (!sample || Math.abs(sample.roleStrokeLengths[drawing.layer] / full - key.percent / 100) > .06)
        errors.push(`Path ${drawing.layer} did not draw the planned length at frame ${key.frame}`);
    }
  }
  const pixels = await page.evaluate(async report => {
    const svg = document.querySelector('#animation svg');
    const canvas = document.createElement('canvas');
    canvas.width = window.logoAnimation.animationData.w;
    canvas.height = window.logoAnimation.animationData.h;
    const context = canvas.getContext('2d');
    const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)], {type: 'image/svg+xml'}));
    try {
      const image = new Image();
      image.src = url;
      await image.decode();
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      const rgba = context.getImageData(0, 0, canvas.width, canvas.height).data;
      let count = 0, outside = 0, cornerPixels = 0;
      for (let i = 3; i < rgba.length; i += 4) if (rgba[i] > 0) {
        count++;
        const pixel = (i-3)/4, x = pixel % canvas.width, y = Math.floor(pixel/canvas.width);
        if (!report.animated_bounds.some(b => x >= b[0]-1 && x <= b[2]+1 && y >= b[1]-1 && y <= b[3]+1)) outside++;
      }
      const outline = report.composition?.backplate_outline;
      if (outline?.probe_corners !== false && outline?.rx >= 4 && outline?.ry >= 4) {
        const [x0,y0,x1,y1] = outline.bounds;
        for (const x of [x0+outline.rx*.15, x1-outline.rx*.15])
          for (const y of [y0+outline.ry*.15, y1-outline.ry*.15]) {
            const alpha = rgba[(Math.floor(y)*canvas.width + Math.floor(x))*4+3];
            if (alpha > 0) cornerPixels++;
          }
      }
      return {count, outside, cornerPixels};
    } finally { URL.revokeObjectURL(url); }
  }, report);
  if (pixels.count === 0) errors.push('Settled frame has no visible pixels');
  if (report.composition?.export_background === 'transparent') {
    if (pixels.outside) errors.push('Transparent export contains pixels outside the declared icon/name bounds');
    if (pixels.cornerPixels) errors.push('Rounded icon corners contain unexpected opaque pixels');
  }
  await page.locator('#matte').selectOption('#181818');
  await page.locator('#stage').screenshot({path: join(screenshots, 'settled-dark.png')});
  await page.locator('#matte').selectOption('#ffffff');
  await page.locator('#stage').screenshot({path: join(screenshots, 'settled-light.png')});
  if (hash(await page.locator('#animation-data').textContent()) !== manifest.files['animation.json']) errors.push('Matte switch mutated animation data');
  const [download] = await Promise.all([
    page.waitForEvent('download', {timeout: 10000}), page.locator('#download-json').click(),
  ]);
  if (await download.failure()) throw Error('JSON download failed');
  const downloaded = await readFile(await download.path());
  JSON.parse(downloaded.toString('utf8'));
  const downloadPassed = typeof manifest.download_filename === 'string' &&
    download.suggestedFilename() === manifest.download_filename && hash(downloaded) === manifest.files['animation.json'];
  if (!downloadPassed) errors.push('Downloaded JSON differs from delivery JSON or has the wrong filename');
  await page.locator('#replay').click();
  const restarted = await page.evaluate(() => !window.logoAnimation.isPaused && window.logoAnimation.currentFrame < 10);
  if (!restarted) errors.push('Replay failed');
  await page.waitForFunction(() => window.logoAnimation.isPaused && window.logoAnimation.currentFrame > window.logoAnimation.totalFrames - 2,
                             null, {timeout: Math.ceil(animation.op / animation.fr * 1000) + 5000});
  if (requests.length) errors.push('Preview attempted network requests');
  const result = {...report, web: errors.length ? 'failed' : 'passed', visual_review: 'pending',
    comparison,
    download: downloadPassed ? 'passed' : 'failed',
    download_filename: download.suggestedFilename(),
    renderer: 'lottie-web 5.12.2 / Chromium SVG', browser: browser.version(), samples,
    animation_sha256: manifest.files['animation.json'], preview_sha256: manifest.files['preview.html'],
    network_requests: requests, settled_visible_pixels: pixels.count,
    outside_content_pixels: pixels.outside, rounded_corner_opaque_probes: pixels.cornerPixels,
    errors, native_platforms: 'not_verified'};
  await writeFile(join(root, 'validation.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify({status: errors.length ? 'needs_decision' : 'ready', web: result.web,
    sampled_frames: samples.length, errors, visual_review: 'pending', report: join(root, 'validation.json')}));
  process.exitCode = errors.length ? 2 : 0;
} finally {
  await browser.close();
}
