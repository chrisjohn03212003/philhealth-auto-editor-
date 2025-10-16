// static/script.js
async function submit(category){
  const fileInput = document.getElementById('file');
  const status = document.getElementById('status');
  if(!fileInput.files.length){ status.innerText = 'Please choose a .docx file first.'; return; }
  const file = fileInput.files[0];
  const form = new FormData();
  form.append('file', file);
  form.append('category', category);
  status.innerText = 'Uploading & processing...';

  const resp = await fetch('/process', { method: 'POST', body: form });
  const data = await resp.json();
  if(data.error){ status.innerText = 'Error: ' + data.error; return; }
  status.innerHTML = `Done. <a href="${data.download}">Download edited file</a>`;
}
