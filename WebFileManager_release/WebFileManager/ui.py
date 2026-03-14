"""
ui.py — HTML template renderer for WebFileManager
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz

Aesthetic: industrial terminal meets refined dark OS — monospaced grid,
amber/cyan accent palette, smooth micro-animations, glassmorphism panels.
"""

from .utils import quote, fmt_size, list_dir, disk_stats


# ─── breadcrumb builder ───────────────────────────────────────────────────────

def _breadcrumb(path):
    parts = [p for p in path.split('/') if p]
    crumbs = ['<a href="/?path=/" class="bc-seg">~</a>']
    cur = ''
    for p in parts:
        cur += '/' + p
        crumbs.append('<a href="/?path={}" class="bc-seg">{}</a>'.format(
            quote(cur), p))
    return '<span class="bc-sep">/</span>'.join(crumbs)


# ─── single CSS + JS blob (inlined for MicroPython single-file serving) ───────

_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;700;800&display=swap');

:root {
  --bg:       #0d0f12;
  --surface:  #13161b;
  --panel:    #181c23;
  --border:   #242830;
  --border2:  #2e3440;
  --text:     #c9d1d9;
  --muted:    #586069;
  --amber:    #f0a830;
  --amber2:   #ffc96b;
  --cyan:     #3ddbd9;
  --cyan2:    #79ffe1;
  --red:      #ff6b6b;
  --green:    #56d364;
  --blue:     #58a6ff;
  --dir-col:  #f0a830;
  --radius:   6px;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-ui:   'Syne', sans-serif;
  --trans:     150ms ease;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { height: 100%; }

body {
  min-height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  padding: 0;
}

/* ── scanline overlay ── */
body::before {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,0,0,.06) 2px, rgba(0,0,0,.06) 4px
  );
}

/* ── layout ── */
.shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}

/* ── header ── */
.header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.logo {
  font-family: var(--font-ui);
  font-weight: 800;
  font-size: 18px;
  letter-spacing: -.5px;
  color: var(--amber);
  text-shadow: 0 0 20px rgba(240,168,48,.4);
}
.logo span { color: var(--cyan); }
.header-meta {
  margin-left: auto;
  display: flex;
  gap: 20px;
  color: var(--muted);
  font-size: 11px;
}
.header-meta b { color: var(--text); }
.disk-bar-wrap { display: flex; align-items: center; gap: 8px; }
.disk-bar {
  width: 80px; height: 4px;
  background: var(--border2);
  border-radius: 2px;
  overflow: hidden;
}
.disk-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--amber));
  border-radius: 2px;
  transition: width .4s ease;
}

/* ── breadcrumb ── */
.bc {
  display: flex;
  align-items: center;
  gap: 0;
  flex-wrap: wrap;
  margin-bottom: 20px;
  font-size: 12px;
}
.bc-seg {
  color: var(--cyan);
  text-decoration: none;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background var(--trans), color var(--trans);
}
.bc-seg:hover { background: rgba(61,219,217,.1); color: var(--cyan2); }
.bc-sep { color: var(--border2); padding: 0 2px; }

/* ── toolbar row ── */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
}

/* ── buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--panel);
  color: var(--text);
  border: 1px solid var(--border2);
  padding: 6px 12px;
  border-radius: var(--radius);
  font-family: var(--font-mono);
  font-size: 12px;
  cursor: pointer;
  transition: background var(--trans), border-color var(--trans), color var(--trans), transform 60ms;
  text-decoration: none;
  white-space: nowrap;
}
.btn:hover { background: var(--border2); border-color: var(--muted); }
.btn:active { transform: scale(.97); }

.btn-amber { border-color: rgba(240,168,48,.4); color: var(--amber); }
.btn-amber:hover { background: rgba(240,168,48,.08); border-color: var(--amber); }

.btn-cyan { border-color: rgba(61,219,217,.4); color: var(--cyan); }
.btn-cyan:hover { background: rgba(61,219,217,.08); border-color: var(--cyan); }

.btn-red { border-color: rgba(255,107,107,.3); color: var(--red); }
.btn-red:hover { background: rgba(255,107,107,.08); border-color: var(--red); }

.btn-green { border-color: rgba(86,211,100,.3); color: var(--green); }
.btn-green:hover { background: rgba(86,211,100,.08); border-color: var(--green); }

/* ── inputs ── */
.inp {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border2);
  padding: 6px 10px;
  border-radius: var(--radius);
  font-family: var(--font-mono);
  font-size: 12px;
  outline: none;
  transition: border-color var(--trans);
}
.inp:focus { border-color: var(--cyan); box-shadow: 0 0 0 2px rgba(61,219,217,.12); }

/* ── upload zone ── */
.upload-zone {
  border: 2px dashed var(--border2);
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 16px;
  transition: border-color var(--trans), background var(--trans);
  position: relative;
  overflow: hidden;
}
.upload-zone.drag-over {
  border-color: var(--amber);
  background: rgba(240,168,48,.04);
}
.upload-zone-inner {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}
.upload-icon { font-size: 24px; flex-shrink: 0; }
.upload-text { flex: 1; min-width: 160px; }
.upload-text strong { color: var(--amber); display: block; margin-bottom: 2px; }
.upload-text small { color: var(--muted); font-size: 11px; }
.file-input-wrap { position: relative; }
.file-input-wrap input[type=file] {
  position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%;
}
.file-label {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--panel);
  color: var(--amber);
  border: 1px solid rgba(240,168,48,.4);
  padding: 6px 14px;
  border-radius: var(--radius);
  font-size: 12px;
  cursor: pointer;
  transition: background var(--trans);
}
.file-label:hover { background: rgba(240,168,48,.08); }

/* ── progress bar ── */
.progress-wrap {
  display: none;
  margin-top: 12px;
}
.progress-wrap.active { display: block; }
.progress-info {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--muted);
  margin-bottom: 5px;
}
.progress-info .pct { color: var(--amber); font-weight: 500; }
.progress-track {
  width: 100%; height: 6px;
  background: var(--border);
  border-radius: 3px; overflow: hidden;
}
.progress-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--amber), var(--amber2));
  border-radius: 3px;
  transition: width .2s ease;
  box-shadow: 0 0 8px rgba(240,168,48,.5);
}
.progress-speed { font-size: 11px; color: var(--muted); margin-top: 4px; }
.selected-files {
  font-size: 11px; color: var(--cyan);
  margin-top: 8px; display: none;
}

/* ── mkdir row ── */
.mkdir-row {
  display: flex; gap: 8px; align-items: center;
  margin-bottom: 20px; flex-wrap: wrap;
}

/* ── file table ── */
.file-table-wrap {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}
table { width: 100%; border-collapse: collapse; }
thead { background: var(--surface); }
th {
  padding: 10px 14px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: .8px;
  text-transform: uppercase;
  color: var(--muted);
  text-align: left;
  border-bottom: 1px solid var(--border);
}
th:last-child { text-align: right; }
td {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr { transition: background var(--trans); }
tbody tr:hover td { background: var(--surface); }
tbody tr.selected td { background: rgba(61,219,217,.05); }

/* name cell */
.cell-name { display: flex; align-items: center; gap: 8px; max-width: 400px; }
.cell-name a { color: var(--text); text-decoration: none; transition: color var(--trans); }
.cell-name a:hover { color: var(--cyan2); }
.icon { font-size: 14px; flex-shrink: 0; }
.badge-dir { color: var(--dir-col); }
.cell-size { color: var(--muted); text-align: right; white-space: nowrap; }
.cell-actions {
  text-align: right;
  white-space: nowrap;
}
.cell-actions .btn { padding: 4px 9px; font-size: 11px; }
.cell-actions .btn + .btn { margin-left: 4px; }

.parent-row td { opacity: .6; }
.parent-row:hover td { opacity: 1; }

/* ── modal ── */
.modal-backdrop {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,.7);
  backdrop-filter: blur(4px);
  z-index: 100;
  align-items: center; justify-content: center;
}
.modal-backdrop.open { display: flex; }
.modal {
  background: var(--panel);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 28px;
  min-width: 340px; max-width: 92vw;
  box-shadow: 0 24px 64px rgba(0,0,0,.6);
  animation: modal-in .15s ease;
}
@keyframes modal-in {
  from { transform: scale(.95) translateY(8px); opacity: 0; }
  to   { transform: scale(1) translateY(0);     opacity: 1; }
}
.modal h3 {
  font-family: var(--font-ui);
  font-size: 16px; font-weight: 700;
  color: var(--text);
  margin-bottom: 16px;
  display: flex; align-items: center; gap: 8px;
}
.modal .field { margin-bottom: 14px; }
.modal .field label { display: block; font-size: 11px; color: var(--muted); margin-bottom: 5px; }
.modal .field .inp { width: 100%; }
.modal .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px; }

/* ── toast ── */
#toast {
  position: fixed; bottom: 24px; right: 24px; z-index: 9000;
  display: flex; flex-direction: column; gap: 8px; pointer-events: none;
}
.toast-item {
  background: var(--panel);
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,.4);
  animation: toast-in .2s ease;
  pointer-events: all;
}
.toast-item.ok  { border-left: 3px solid var(--green); }
.toast-item.err { border-left: 3px solid var(--red);   }
@keyframes toast-in {
  from { transform: translateX(20px); opacity: 0; }
  to   { transform: translateX(0);    opacity: 1; }
}

/* ── empty state ── */
.empty {
  text-align: center; padding: 48px 20px; color: var(--muted);
}
.empty .empty-icon { font-size: 36px; margin-bottom: 12px; }

/* ── text editor ── */
.editor-wrap { display: none; }
.editor-wrap.open { display: block; }
#editor-ta {
  width: 100%; min-height: 320px;
  background: var(--surface);
  color: var(--cyan2);
  border: 1px solid var(--border2);
  border-radius: var(--radius);
  padding: 14px;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.7;
  resize: vertical;
  outline: none;
  tab-size: 4;
}
#editor-ta:focus { border-color: var(--cyan); }

/* ── checkbox col ── */
.check-col { width: 32px; }
input[type=checkbox] {
  accent-color: var(--cyan);
  width: 13px; height: 13px;
  cursor: pointer;
}

/* ── credits footer ── */
.credits {
  margin-top: 40px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 11px;
  color: var(--muted);
}
.credits-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.credits-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 4px 10px 4px 8px;
  font-size: 11px;
  color: var(--text);
  text-decoration: none;
  transition: border-color var(--trans), background var(--trans);
}
.credits-badge:hover {
  border-color: var(--cyan);
  background: rgba(61,219,217,.06);
  color: var(--cyan2);
}
.credits-badge .gh-icon {
  font-size: 14px;
  line-height: 1;
}
.credits-version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--border2);
  letter-spacing: .5px;
}
"""

# ─── JavaScript ───────────────────────────────────────────────────────────────

_SCRIPT = """
// ── toast ─────────────────────────────────────────────────────────────────
function toast(msg, type='ok') {
  const t = document.createElement('div');
  t.className = 'toast-item ' + type;
  t.textContent = msg;
  document.getElementById('toast').appendChild(t);
  setTimeout(() => t.remove(), 3400);
}

// ── drag-and-drop upload zone ─────────────────────────────────────────────
const zone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const selInfo  = document.getElementById('sel-info');

zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
zone.addEventListener('drop', e => {
  e.preventDefault();
  zone.classList.remove('drag-over');
  fileInput.files = e.dataTransfer.files;
  updateFileList();
});
fileInput.addEventListener('change', updateFileList);

function updateFileList() {
  const n = fileInput.files.length;
  if (n) {
    selInfo.style.display = 'block';
    selInfo.textContent = n === 1
      ? fileInput.files[0].name + ' (' + fmtBytes(fileInput.files[0].size) + ')'
      : n + ' files selected';
  } else {
    selInfo.style.display = 'none';
  }
}

function fmtBytes(n) {
  if (n < 1024) return n + ' B';
  if (n < 1048576) return (n/1024).toFixed(1) + ' kB';
  return (n/1048576).toFixed(2) + ' MB';
}

// ── upload with progress ──────────────────────────────────────────────────
document.getElementById('upload-form').addEventListener('submit', function(e) {
  e.preventDefault();
  if (!fileInput.files.length) { toast('No files selected', 'err'); return; }

  const fd   = new FormData(this);
  const xhr  = new XMLHttpRequest();
  const prog = document.getElementById('progress-wrap');
  const bar  = document.getElementById('progress-bar');
  const pct  = document.getElementById('progress-pct');
  const spd  = document.getElementById('progress-speed');
  const fname = document.getElementById('progress-fname');

  let startTime = Date.now();
  let lastLoaded = 0;

  prog.classList.add('active');
  bar.style.width = '0%';

  xhr.upload.addEventListener('progress', function(ev) {
    if (!ev.lengthComputable) return;
    const p = Math.round(ev.loaded / ev.total * 100);
    bar.style.width = p + '%';
    pct.textContent = p + '%';

    const now = Date.now();
    const dt  = (now - startTime) / 1000;
    if (dt > 0.2) {
      const speed = (ev.loaded - lastLoaded) / ((now - startTime) / 1000);
      spd.textContent = fmtBytes(speed) + '/s  —  ' + fmtBytes(ev.loaded) + ' / ' + fmtBytes(ev.total);
      lastLoaded = ev.loaded;
      startTime  = now;
    }
  });

  xhr.addEventListener('load', function() {
    prog.classList.remove('active');
    if (xhr.status === 200 || xhr.status === 302) {
      toast('Upload complete ✓');
      setTimeout(() => location.reload(), 600);
    } else {
      toast('Upload failed (' + xhr.status + ')', 'err');
    }
  });

  xhr.addEventListener('error', () => { prog.classList.remove('active'); toast('Network error', 'err'); });

  xhr.open('POST', this.action);
  xhr.send(fd);
});

// ── modal helpers ─────────────────────────────────────────────────────────
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

document.querySelectorAll('.modal-backdrop').forEach(m => {
  m.addEventListener('click', e => { if (e.target === m) m.classList.remove('open'); });
});

// ── rename modal ──────────────────────────────────────────────────────────
function showRename(path, name) {
  document.getElementById('rename-old').value  = path;
  document.getElementById('rename-new').value  = name;
  document.getElementById('rename-title').textContent = 'Rename: ' + name;
  openModal('rename-modal');
  setTimeout(() => document.getElementById('rename-new').select(), 50);
}

// ── copy/move modal ────────────────────────────────────────────────────────
function showCopyMove(path, name) {
  document.getElementById('cm-src').value  = path;
  document.getElementById('cm-dest').value = path;
  document.getElementById('cm-title').textContent = name;
  openModal('cm-modal');
  setTimeout(() => document.getElementById('cm-dest').focus(), 50);
}

// ── text editor modal ─────────────────────────────────────────────────────
function showEditor(path, name) {
  document.getElementById('ed-title').textContent = 'Edit: ' + name;
  document.getElementById('ed-path').value = path;
  const ta = document.getElementById('editor-ta');
  ta.value = 'Loading…';
  openModal('editor-modal');
  fetch('/raw?path=' + encodeURIComponent(path))
    .then(r => r.text())
    .then(t => { ta.value = t; })
    .catch(() => { ta.value = '(error loading file)'; });
}

function saveEditor() {
  const path = document.getElementById('ed-path').value;
  const body = document.getElementById('editor-ta').value;
  fetch('/save?path=' + encodeURIComponent(path), {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain' },
    body: body
  }).then(r => {
    if (r.ok) { toast('Saved ✓'); closeModal('editor-modal'); }
    else r.text().then(t => toast('Save failed: ' + t, 'err'));
  }).catch(e => toast('Error: ' + e, 'err'));
}

// ── confirm delete ────────────────────────────────────────────────────────
function confirmDelete(path, name, back) {
  if (confirm('Delete "' + name + '"?')) {
    window.location = '/delete?path=' + encodeURIComponent(path) + '&back=' + encodeURIComponent(back);
  }
}

// ── select all ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const sa = document.getElementById('select-all');
  if (sa) {
    sa.addEventListener('change', () => {
      document.querySelectorAll('.row-check').forEach(c => {
        c.checked = sa.checked;
        c.closest('tr').classList.toggle('selected', sa.checked);
      });
    });
    document.querySelectorAll('.row-check').forEach(c => {
      c.addEventListener('change', () => {
        c.closest('tr').classList.toggle('selected', c.checked);
      });
    });
  }
});
"""


# ─── page template ─────────────────────────────────────────────────────────────

_PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WebFileManager — {path}</title>
<style>{style}</style>
</head>
<body>
<div class="shell">

  <!-- header -->
  <div class="header">
    <div class="logo">Web<span>FM</span></div>
    <div style="color:var(--muted);font-size:12px;margin-left:4px">WebFileManager</div>
    <div class="header-meta">
      <div class="disk-bar-wrap">
        <span>used {used}</span>
        <div class="disk-bar"><div class="disk-bar-fill" style="width:{used_pct}%"></div></div>
        <span>free {free}</span>
      </div>
      <span>total {total}</span>
    </div>
  </div>

  <!-- breadcrumb -->
  <div class="bc">{breadcrumb}</div>

  <!-- upload zone -->
  <form id="upload-form" action="/?path={path_enc}" method="post" enctype="multipart/form-data">
    <div class="upload-zone" id="upload-zone">
      <div class="upload-zone-inner">
        <div class="upload-icon">📁</div>
        <div class="upload-text">
          <strong>Upload files</strong>
          <small>Drag &amp; drop or click to browse — multiple files supported</small>
        </div>
        <div class="file-input-wrap">
          <label class="file-label">📂 Choose files</label>
          <input type="file" id="file-input" name="file" multiple>
        </div>
        <button class="btn btn-amber" type="submit">⬆ Upload</button>
      </div>
      <div class="selected-files" id="sel-info"></div>
      <div class="progress-wrap" id="progress-wrap">
        <div class="progress-info">
          <span id="progress-fname"></span>
          <span class="pct" id="progress-pct">0%</span>
        </div>
        <div class="progress-track">
          <div class="progress-bar" id="progress-bar"></div>
        </div>
        <div class="progress-speed" id="progress-speed"></div>
      </div>
    </div>
  </form>

  <!-- toolbar: mkdir + actions -->
  <div class="toolbar">
    <input class="inp" id="mkdir-inp" type="text" placeholder="New folder name" style="width:180px">
    <button class="btn btn-cyan" onclick="doMkdir()">+ Folder</button>
    <div style="margin-left:auto;color:var(--muted);font-size:11px">{entry_count} items</div>
  </div>

  <!-- file table -->
  <div class="file-table-wrap">
    <table>
      <thead>
        <tr>
          <th class="check-col"><input type="checkbox" id="select-all" title="Select all"></th>
          <th>Name</th>
          <th>Size</th>
          <th style="text-align:right">Actions</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    {empty_state}
  </div>

  <!-- credits footer -->
  <div class="credits">
    <div class="credits-left">
      <a class="credits-badge" href="https://github.com/thezerohz" target="_blank" rel="noopener">
        <span class="gh-icon">⌨</span>
        <span>Rakib Hasan</span>
        <span style="color:var(--muted)">·</span>
        <span style="color:var(--cyan)">@thezerohz</span>
      </a>
      <span>WebFileManager for MicroPython</span>
    </div>
    <span class="credits-version">v1.0.0 · github.com/thezerohz</span>
  </div>

</div><!-- /shell -->

<!-- ── Rename modal ── -->
<div class="modal-backdrop" id="rename-modal">
  <div class="modal">
    <h3>✏️ <span id="rename-title">Rename</span></h3>
    <div class="field">
      <label>New name</label>
      <input class="inp" id="rename-new" type="text">
      <input type="hidden" id="rename-old">
    </div>
    <div class="modal-actions">
      <button class="btn" onclick="closeModal('rename-modal')">Cancel</button>
      <button class="btn btn-amber" onclick="doRename()">Rename</button>
    </div>
  </div>
</div>

<!-- ── Copy / Move modal ── -->
<div class="modal-backdrop" id="cm-modal">
  <div class="modal">
    <h3>📋 <span id="cm-title"></span></h3>
    <input type="hidden" id="cm-src">
    <div class="field">
      <label>Destination path</label>
      <input class="inp" id="cm-dest" type="text" style="width:100%">
    </div>
    <div class="modal-actions">
      <button class="btn" onclick="closeModal('cm-modal')">Cancel</button>
      <button class="btn btn-cyan" onclick="doOp('copy')">Copy</button>
      <button class="btn btn-amber" onclick="doOp('move')">Move</button>
    </div>
  </div>
</div>

<!-- ── Text editor modal ── -->
<div class="modal-backdrop" id="editor-modal">
  <div class="modal" style="width:700px;max-width:95vw">
    <h3>📝 <span id="ed-title">Edit</span></h3>
    <input type="hidden" id="ed-path">
    <textarea id="editor-ta"></textarea>
    <div class="modal-actions">
      <button class="btn" onclick="closeModal('editor-modal')">Cancel</button>
      <button class="btn btn-green" onclick="saveEditor()">💾 Save</button>
    </div>
  </div>
</div>

<!-- toast container -->
<div id="toast"></div>

<script>
{script}

function doMkdir() {{
  const name = document.getElementById('mkdir-inp').value.trim();
  if (!name) return;
  window.location = '/mkdir?path={path_enc}&name=' + encodeURIComponent(name);
}}

function doRename() {{
  const oldP = document.getElementById('rename-old').value;
  const newN = document.getElementById('rename-new').value.trim();
  if (!newN) return;
  fetch('/rename?src=' + encodeURIComponent(oldP) + '&name=' + encodeURIComponent(newN))
    .then(r => {{ if (r.ok) {{ toast('Renamed ✓'); closeModal('rename-modal'); setTimeout(() => location.reload(), 500); }} else toast('Rename failed', 'err'); }})
    .catch(() => toast('Error', 'err'));
}}

function doOp(op) {{
  const src  = document.getElementById('cm-src').value;
  const dest = document.getElementById('cm-dest').value.trim();
  if (!dest) return;
  fetch('/fileop?op=' + op + '&src=' + encodeURIComponent(src) + '&dest=' + encodeURIComponent(dest))
    .then(r => r.json())
    .then(d => {{
      if (d.ok) {{ toast(op === 'move' ? 'Moved ✓' : 'Copied ✓'); closeModal('cm-modal'); setTimeout(() => location.reload(), 500); }}
      else toast(d.error || 'Failed', 'err');
    }})
    .catch(() => toast('Error', 'err'));
}}
</script>
</body>
</html>"""

_ROW_DIR = """\
<tr>
  <td><input type="checkbox" class="row-check"></td>
  <td><div class="cell-name"><span class="icon badge-dir">📁</span><a href="/?path={enc_path}">{name}</a></div></td>
  <td class="cell-size">—</td>
  <td class="cell-actions">
    <button class="btn btn-amber" onclick="showRename('{enc_full_js}','{name_js}')">✏</button>
    <button class="btn btn-cyan"  onclick="showCopyMove('{enc_full_js}','{name_js}')">⧉</button>
    <button class="btn btn-red"   onclick="confirmDelete('{enc_full_js}','{name_js}','{enc_back_js}')">✕</button>
  </td>
</tr>"""

_ROW_FILE = """\
<tr>
  <td><input type="checkbox" class="row-check"></td>
  <td><div class="cell-name"><span class="icon">{file_icon}</span><a href="/download?path={enc_full}">{name}</a></div></td>
  <td class="cell-size">{size}</td>
  <td class="cell-actions">
    <a href="/download?path={enc_full}"><button class="btn btn-cyan">⬇</button></a>
    {edit_btn}
    <button class="btn btn-amber" onclick="showRename('{enc_full_js}','{name_js}')">✏</button>
    <button class="btn btn-cyan"  onclick="showCopyMove('{enc_full_js}','{name_js}')">⧉</button>
    <button class="btn btn-red"   onclick="confirmDelete('{enc_full_js}','{name_js}','{enc_back_js}')">✕</button>
  </td>
</tr>"""

_EDIT_BTN = """<button class="btn btn-green" onclick="showEditor('{enc_full_js}','{name_js}')">📝</button>"""

_EDITABLE_EXT = ('.py', '.txt', '.json', '.html', '.css', '.js', '.md',
                 '.cfg', '.conf', '.ini', '.yaml', '.yml', '.csv', '.sh',
                 '.toml', '.xml')

_FILE_ICONS = {
    '.py': '🐍', '.js': '📜', '.json': '{}', '.html': '🌐',
    '.css': '🎨', '.md': '📋', '.txt': '📄', '.sh': '⚡',
    '.jpg': '🖼', '.jpeg': '🖼', '.png': '🖼', '.gif': '🖼',
    '.zip': '📦', '.gz': '📦', '.tar': '📦',
    '.bin': '💾', '.hex': '💾', '.uf2': '💾',
    '.mp3': '🎵', '.wav': '🎵',
    '.csv': '📊', '.yaml': '⚙', '.yml': '⚙',
    '.toml': '⚙', '.cfg': '⚙', '.conf': '⚙', '.ini': '⚙',
}


def _js_escape(s):
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')


def _file_icon(name):
    dot = name.rfind('.')
    if dot == -1:
        return '📄'
    return _FILE_ICONS.get(name[dot:].lower(), '📄')


def _used_pct(free_str, total_str):
    """Rough percentage from formatted strings — best effort."""
    try:
        def _parse(s):
            n, u = s.split()
            n = float(n)
            u = u.upper()
            mult = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}.get(u, 1)
            return int(n * mult)
        free  = _parse(free_str)
        total = _parse(total_str)
        if total == 0:
            return 0
        return max(2, min(98, int((total - free) / total * 100)))
    except Exception:
        return 50


def build_page(root, path):
    entries = list_dir(root, path)
    free_s, used_s, total_s = disk_stats(root)
    rows = []

    # parent link
    if path != '/':
        parent = '/'.join(path.rstrip('/').split('/')[:-1]) or '/'
        rows.append(
            '<tr class="parent-row">'
            '<td></td>'
            '<td colspan="3"><div class="cell-name">'
            '<span class="icon">⬆</span>'
            '<a href="/?path={}">.. (parent)</a>'
            '</div></td></tr>'.format(quote(parent))
        )

    for name, sz, is_d in entries:
        full      = (path.rstrip('/') + '/' + name) if path != '/' else '/' + name
        enc_full  = quote(full)
        enc_back  = quote(path)
        name_js   = _js_escape(name)
        enc_full_js = _js_escape(full)
        enc_back_js = _js_escape(path)

        if is_d:
            enc_path = quote(full)
            rows.append(_ROW_DIR.format(
                enc_path=enc_path, name=name,
                enc_full_js=enc_full_js, name_js=name_js,
                enc_back_js=enc_back_js,
                enc_full=enc_full,
            ))
        else:
            dot = name.rfind('.')
            ext = name[dot:].lower() if dot != -1 else ''
            is_editable = ext in _EDITABLE_EXT
            edit_btn = _EDIT_BTN.format(
                enc_full_js=enc_full_js, name_js=name_js
            ) if is_editable else ''
            rows.append(_ROW_FILE.format(
                file_icon=_file_icon(name),
                enc_full=enc_full,
                name=name,
                size=fmt_size(sz),
                enc_full_js=enc_full_js,
                name_js=name_js,
                enc_back_js=enc_back_js,
                edit_btn=edit_btn,
            ))

    count = len(entries)
    empty_state = (
        '<div class="empty"><div class="empty-icon">📭</div>'
        '<div>This folder is empty</div></div>'
        if not entries and path == '/' else ''
    )

    return _PAGE_TMPL.format(
        style=_STYLE,
        script=_SCRIPT,
        path=path,
        path_enc=quote(path),
        breadcrumb=_breadcrumb(path),
        rows='\n'.join(rows),
        free=free_s,
        used=used_s,
        total=total_s,
        used_pct=_used_pct(free_s, total_s),
        entry_count=count,
        empty_state=empty_state,
    )
