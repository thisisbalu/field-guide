// ── Theme (localStorage persistence) ─────────────────────────────────────
function toggleTheme() {
  const h = document.documentElement;
  const isDark = h.getAttribute('data-theme') === 'dark';
  const next = isDark ? 'light' : 'dark';
  h.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  document.getElementById('toggle-label').textContent = isDark ? 'DARK MODE' : 'LIGHT MODE';
}

// ── Tabs (with URL hash sync) ─────────────────────────────────────────────
function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(name).classList.add('active');
  history.replaceState(null, '', '#' + name);
}

// ── Accordion (JS-driven scrollHeight animation) ───────────────────────────
function setAccOpen(item, open) {
  const body = item.querySelector('.acc-body');
  if (open) {
    item.classList.add('open');
    const h = body.scrollHeight;
    body.style.maxHeight = h + 'px';
    function onEnd(e) {
      if (e.propertyName !== 'max-height') return;
      body.removeEventListener('transitionend', onEnd);
      if (item.classList.contains('open')) body.style.maxHeight = 'none';
    }
    body.addEventListener('transitionend', onEnd);
  } else {
    if (!body.style.maxHeight || body.style.maxHeight === 'none') {
      body.style.maxHeight = body.scrollHeight + 'px';
    }
    requestAnimationFrame(() => requestAnimationFrame(() => {
      item.classList.remove('open');
      body.style.maxHeight = '0';
    }));
  }
}

function toggleAcc(header) {
  setAccOpen(header.parentElement, !header.parentElement.classList.contains('open'));
}

// ── Expand / collapse all Q&A ─────────────────────────────────────────────
function toggleAllAcc(btn) {
  const items = [...document.querySelectorAll('#qa .acc-item')].filter(i => i.style.display !== 'none');
  const allOpen = items.every(i => i.classList.contains('open'));
  items.forEach(i => setAccOpen(i, !allOpen));
  btn.textContent = allOpen ? 'Expand All' : 'Collapse All';
}

// ── Q&A keyword filter ────────────────────────────────────────────────────
function filterQA(query) {
  const q = query.toLowerCase().trim();
  document.querySelectorAll('.acc-item').forEach(item => {
    const text = item.querySelector('.acc-question').textContent.toLowerCase();
    item.style.display = (!q || text.includes(q)) ? '' : 'none';
  });
  // Reset expand-all label whenever filter changes
  const btn = document.querySelector('.expand-all-btn');
  if (btn) btn.textContent = 'Expand All';
}

// ── Q&A review progress (localStorage) ───────────────────────────────────
function toggleReviewed(topicId, qId, btn) {
  const key = 'reviewed:' + topicId + ':' + qId;
  const item = btn.closest('.acc-item');
  if (localStorage.getItem(key) === '1') {
    localStorage.removeItem(key);
    item.classList.remove('reviewed');
    btn.textContent = 'Mark reviewed';
  } else {
    localStorage.setItem(key, '1');
    item.classList.add('reviewed');
    btn.textContent = '✓ Reviewed';
  }
  updateQAProgress(topicId);
}

function updateQAProgress(topicId) {
  const allItems = document.querySelectorAll('.acc-item[data-qid]');
  const total = allItems.length;
  const done = [...allItems].filter(i => i.classList.contains('reviewed')).length;
  const fill = document.getElementById('qa-progress-bar');
  const label = document.getElementById('qa-progress-label');
  if (fill) fill.style.width = (total ? (done / total * 100) : 0) + '%';
  if (label) label.textContent = done + ' / ' + total + ' reviewed';
}

function initReviewedState(topicId) {
  document.querySelectorAll('.acc-item[data-qid]').forEach(item => {
    const qId = item.dataset.qid;
    if (localStorage.getItem('reviewed:' + topicId + ':' + qId) === '1') {
      item.classList.add('reviewed');
      const btn = item.querySelector('.mark-reviewed-btn');
      if (btn) btn.textContent = '✓ Reviewed';
    }
  });
  updateQAProgress(topicId);
}

// ── DOMContentLoaded: tab restore, toggle label, copy-to-clipboard ────────
document.addEventListener('DOMContentLoaded', function () {
  // Sync toggle label with the actual current theme
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const label = document.getElementById('toggle-label');
  if (label) label.textContent = isDark ? 'LIGHT MODE' : 'DARK MODE';

  // Restore active tab from URL hash
  const hash = location.hash.slice(1);
  const validTabs = ['overview', 'deepdive', 'qa', 'scenarios'];
  if (hash && validTabs.includes(hash)) {
    const tab = document.querySelector(`.tab[data-tab="${hash}"]`);
    if (tab) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(hash).classList.add('active');
    }
  }

  // Restore reviewed state for topic pages
  const topicId = document.body.dataset.topicId;
  if (topicId) initReviewedState(topicId);

  // Copy-to-clipboard on CLI command blocks
  document.querySelectorAll('.cmd').forEach(cmd => {
    cmd.title = 'Click to copy';
    cmd.addEventListener('click', function () {
      navigator.clipboard.writeText(this.textContent.trim()).then(() => {
        const orig = this.style.opacity;
        this.style.opacity = '0.4';
        setTimeout(() => { this.style.opacity = orig; }, 600);
      }).catch(() => {});
    });
  });
});
