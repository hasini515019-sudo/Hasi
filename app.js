const codeInput  = document.getElementById('codeInput');
const lineNums   = document.getElementById('lineNums');
const charCount  = document.getElementById('charCount');
const langSelect = document.getElementById('langSelect');

// Line numbers
function updateLineNums() {
  const lines = codeInput.value.split('\n').length;
  lineNums.textContent = Array.from({ length: lines }, (_, i) => i + 1).join('\n');
}

// Char count + update lines
codeInput.addEventListener('input', () => {
  charCount.textContent = codeInput.value.length.toLocaleString() + ' chars';
  updateLineNums();
});

// Sync scroll
codeInput.addEventListener('scroll', () => {
  lineNums.scrollTop = codeInput.scrollTop;
});

// Tab key support
codeInput.addEventListener('keydown', e => {
  if (e.key === 'Tab') {
    e.preventDefault();
    const s = codeInput.selectionStart;
    codeInput.value = codeInput.value.substring(0, s) + '  ' + codeInput.value.substring(s);
    codeInput.selectionStart = codeInput.selectionEnd = s + 2;
    updateLineNums();
  }
});

// File upload
document.getElementById('fileInput').addEventListener('change', function () {
  const file = this.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    codeInput.value = ev.target.result;
    charCount.textContent = ev.target.result.length.toLocaleString() + ' chars';
    updateLineNums();
    showToast(`📁 ${file.name} loaded`, 'success');
  };
  reader.readAsText(file);
  this.value = '';
});

// GitHub fetch
async function fetchGithub() {
  const url = document.getElementById('githubUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  closeModal('githubModal');
  showToast('Fetching…', 'info');
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const text = await res.text();
    codeInput.value = text;
    charCount.textContent = text.length.toLocaleString() + ' chars';
    updateLineNums();
    showToast('✓ Code fetched from GitHub', 'success');
  } catch (err) {
    showToast('Could not fetch — use a raw GitHub URL', 'error');
  }
}

// Clear editor
function clearEditor() {
  codeInput.value = '';
  charCount.textContent = '0 chars';
  updateLineNums();
}

// Refactor API call
async function runRefactor() {
  const code = codeInput.value.trim();
  if (!code) { showToast('⚠ Paste some code first', 'error'); return; }
  const lang = langSelect.value;
  showLoader();
  try {
    const result = await callRefactorAPI(code, lang); // Implement this separately
    hideLoader();
    sessionStorage.setItem('cf_result', JSON.stringify(result));
    sessionStorage.setItem('cf_original', code);
    window.location.href = 'result.html';
  } catch (err) {
    hideLoader();
    showToast('API error: ' + err.message, 'error');
  }
}

// Initialize
updateLineNums();