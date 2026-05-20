function toggleTheme(){
  const h = document.documentElement;
  const isDark = h.getAttribute('data-theme') === 'dark';
  h.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.getElementById('toggle-label').textContent = isDark ? 'DARK MODE' : 'LIGHT MODE';
}

function switchTab(name, el){
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(name).classList.add('active');
}

function toggleAcc(header){
  const item = header.parentElement;
  item.classList.toggle('open', !item.classList.contains('open'));
}
