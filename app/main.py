from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_db_and_tables
from app.api.monitors import router as monitors_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print(f"🚀 {settings.app_name} arrancado")
    yield
    print("👋 Cerrando...")


app = FastAPI(
    title=settings.app_name,
    description="Intelligent website monitoring and change detection",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitors_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(content="""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Web Monitor</title>
  <style>
    :root { color-scheme: dark; --bg:#0f172a; --panel:#172033; --line:#26324a; --text:#e5e7eb; --muted:#94a3b8; --brand:#7c3aed; --green:#22c55e; --red:#ef4444; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,system-ui,sans-serif; background:var(--bg); color:var(--text); }
    header { height:68px; display:flex; align-items:center; justify-content:space-between; padding:0 28px; border-bottom:1px solid var(--line); }
    header h1 { font-size:20px; margin:0; }
    header a { color:var(--muted); text-decoration:none; font-size:14px; }
    main { max-width:1180px; margin:auto; padding:28px; }
    .stats { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-bottom:24px; }
    .card { border:1px solid var(--line); background:var(--panel); border-radius:12px; padding:18px; }
    .stat strong { display:block; font-size:28px; margin-top:5px; }
    .stat span { color:var(--muted); font-size:13px; }
    .toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
    button { border:0; border-radius:8px; padding:10px 14px; cursor:pointer; color:white; background:var(--brand); font-weight:700; }
    button.secondary { background:#334155; }
    button.danger { background:#991b1b; }
    button:disabled { opacity:.55; cursor:wait; }
    table { width:100%; border-collapse:collapse; }
    th,td { text-align:left; padding:12px; border-bottom:1px solid var(--line); font-size:14px; }
    th { color:var(--muted); font-weight:600; }
    td a { color:#c4b5fd; }
    .status { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:7px; background:var(--green); }
    .status.error { background:var(--red); }
    .status.paused { background:#64748b; }
    dialog { border:1px solid var(--line); border-radius:12px; background:var(--panel); color:var(--text); width:min(520px,calc(100vw - 32px)); }
    dialog::backdrop { background:rgba(0,0,0,.7); }
    form { display:grid; gap:12px; }
    label { color:var(--muted); font-size:13px; }
    input,select { width:100%; margin-top:6px; border:1px solid var(--line); border-radius:8px; padding:10px; background:#0f172a; color:white; }
    .actions { display:flex; gap:8px; justify-content:flex-end; }
    .empty { text-align:center; color:var(--muted); padding:30px; }
    dialog#loginDialog { width:min(380px,calc(100vw - 32px)); }
    .login-logo { text-align:center; margin-bottom:4px; font-size:28px; }
    .brand { display:flex; align-items:center; gap:10px; }
    .brand img { height:44px; width:auto; object-fit:contain; }
    @media(max-width:760px){ .stats { grid-template-columns:1fr; } main { padding:16px; } th:nth-child(3),td:nth-child(3){display:none;} header {padding:0 16px;} }
  </style>
</head>
<body>
  <dialog id="loginDialog">
    <form onsubmit="login(event)">
      <div class="login-logo">Web Monitor</div>
      <label>Username<input name="username" required autocomplete="username"></label>
      <label>Password<input name="password" type="password" required autocomplete="current-password"></label>
      <div class="actions"><button>Sign in</button></div>
    </form>
  </dialog>
  <header><div class="brand"><img src="/static/web-monitor-pro.png" alt="Web Monitor Pro"><h1>Web Monitor Pro</h1></div><a href="/docs" target="_blank">API Documentation</a></header>
  <main>
    <section class="stats">
      <div class="card stat"><span>Monitors</span><strong id="total">0</strong></div>
      <div class="card stat"><span>Active</span><strong id="active">0</strong></div>
      <div class="card stat"><span>Errors</span><strong id="errors">0</strong></div>
    </section>
    <div class="toolbar"><h2>Monitors</h2><button onclick="openCreate()">New monitor</button></div>
    <div class="card">
      <table>
        <thead><tr><th>Name</th><th>Status</th><th>URL</th><th>Last checked</th><th>Actions</th></tr></thead>
        <tbody id="rows"><tr><td class="empty" colspan="5">Loading...</td></tr></tbody>
      </table>
    </div>
  </main>
  <dialog id="createDialog">
    <form onsubmit="createMonitor(event)">
      <h2>New monitor</h2>
      <label>Name<input name="name" required maxlength="200" placeholder="Python price"></label>
      <label>URL<input name="url" type="url" required placeholder="https://example.com"></label>
      <label>Type<select name="monitor_type"><option value="selector">Selector</option><option value="text">Text</option><option value="price">Price</option><option value="availability">Availability</option></select></label>
      <label>CSS Selector<input name="css_selector" placeholder="h1, .price"></label>
      <label>Interval (minutes)<input name="check_interval_minutes" type="number" value="60" min="5" max="1440"></label>
      <div class="actions"><button type="button" class="secondary" onclick="createDialog.close()">Cancel</button><button>Save</button></div>
    </form>
  </dialog>
  <script>
    const rows = document.querySelector('#rows');
    const createDialog = document.querySelector('#createDialog');
    const loginDialog = document.querySelector('#loginDialog');
    let authorization='';
    function escapeHtml(value){ const div=document.createElement('div'); div.textContent=value ?? ''; return div.innerHTML; }
    async function api(path, options={}) {
      const response=await fetch(path,{...options,headers:{'Content-Type':'application/json',...(authorization?{'Authorization':authorization}:{}) ,...(options.headers||{})}});
      if(response.status===401) loginDialog.showModal();
      if(!response.ok){ throw new Error((await response.text()) || `Error HTTP ${response.status}`); }
      return response.status===204 ? null : response.json();
    }
    async function login(event){
      event.preventDefault();
      const form=new FormData(event.target);
      authorization='Basic '+btoa(unescape(encodeURIComponent(form.get('username')+':'+form.get('password'))));
      try {
        const response=await fetch('/api/monitors/',{headers:{'Authorization':authorization}});
        if(!response.ok){ authorization=''; throw new Error('Incorrect username or password'); }
        loginDialog.close();
        event.target.reset();
        await load();
      } catch(error){ alert(error.message); }
    }
    async function load() {
      try {
        const monitors=await api('/api/monitors/');
        document.querySelector('#total').textContent=monitors.length;
        document.querySelector('#active').textContent=monitors.filter(m=>m.is_active).length;
        document.querySelector('#errors').textContent=monitors.filter(m=>m.status==='error').length;
        rows.innerHTML=monitors.length ? monitors.map(m=>`<tr>
          <td><strong>${escapeHtml(m.name)}</strong><br><small>${escapeHtml(m.last_value||'No value yet')}</small></td>
          <td><span class="status ${m.status==='error'?'error':m.status==='paused'?'paused':''}"></span>${escapeHtml(m.status)}</td>
          <td><a href="${escapeHtml(m.url)}" target="_blank" rel="noopener">${escapeHtml(m.url)}</a></td>
          <td>${m.last_checked_at ? new Date(m.last_checked_at).toLocaleString() : 'Never'}</td>
          <td><button onclick="checkMonitor(${m.id},this)" class="secondary">Check</button> <button onclick="deleteMonitor(${m.id})" class="danger">Delete</button></td>
        </tr>`).join('') : '<tr><td class="empty" colspan="5">No monitors registered</td></tr>';
      } catch(error) { rows.innerHTML=`<tr><td class="empty" colspan="5">${escapeHtml(error.message)}</td></tr>`; }
    }
    function openCreate(){ createDialog.showModal(); }
    async function createMonitor(event){
      event.preventDefault();
      const form=new FormData(event.target);
      const payload={name:form.get('name'),url:form.get('url'),monitor_type:form.get('monitor_type'),check_interval_minutes:Number(form.get('check_interval_minutes'))};
      if(form.get('css_selector')) payload.css_selector=form.get('css_selector');
      try { await api('/api/monitors/',{method:'POST',body:JSON.stringify(payload)}); createDialog.close(); event.target.reset(); await load(); }
      catch(error){ alert(error.message); }
    }
    async function checkMonitor(id,button){
      button.disabled=true;
      try { await api(`/api/monitors/${id}/check`,{method:'POST'}); await load(); } catch(error){ alert(error.message); button.disabled=false; }
    }
    async function deleteMonitor(id){
      if(!confirm('Delete this monitor?')) return;
      try { await api(`/api/monitors/${id}`,{method:'DELETE'}); await load(); } catch(error){ alert(error.message); }
    }
    loginDialog.showModal();
  </script>
</body>
</html>""")


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}