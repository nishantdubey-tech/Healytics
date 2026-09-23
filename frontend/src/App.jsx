import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Activity, BarChart3, Brain, Database, FileText, HeartPulse,
  LogIn, Upload, UserRound, AlertTriangle, CheckCircle2
} from "lucide-react";

const api = axios.create({ baseURL: "/api" });

const initialForm = {
  patient_name: "Demo Patient",
  age: 52, sex: 1, cp: 0, trestbps: 125, chol: 212, fbs: 0,
  restecg: 1, thalach: 168, exang: 0, oldpeak: 1.0, slope: 2, ca: 0, thal: 3
};

function Card({ children, className="" }) {
  return <div className={`card ${className}`}>{children}</div>;
}

function App() {
  const [loggedIn, setLoggedIn] = useState(localStorage.getItem("healytics_token") === "demo");
  const [login, setLogin] = useState({username:"demo", password:"healytics123"});
  const [tab, setTab] = useState("dashboard");
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState({total_analyzed:0, high_risk_cases:0, low_risk_cases:0, average_risk_probability:0});
  const [history, setHistory] = useState([]);
  const [uploadResult, setUploadResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    try {
      const [s,h] = await Promise.all([
        api.get("/analytics/summary"),
        api.get("/history")
      ]);
      setStats(s.data); setHistory(h.data);
    } catch {}
  };

  useEffect(() => { refresh(); }, []);

  const doLogin = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post("/auth/login", login);
      localStorage.setItem("healytics_token","demo");
      setLoggedIn(true);
    } catch {
      alert("Invalid login. Default: demo / healytics123");
    } finally { setBusy(false); }
  };

  const predict = async (e) => {
    e.preventDefault();
    setBusy(true); setResult(null);
    try {
      const payload = Object.fromEntries(Object.entries(form).map(([k,v]) =>
        ["patient_name"].includes(k) ? [k,v] : [k, Number(v)]
      ));
      const r = await api.post("/predict", payload);
      setResult(r.data);
      await refresh();
      setTab("predict");
    } catch (err) {
      alert(err?.response?.data?.detail || "Prediction failed.");
    } finally { setBusy(false); }
  };

  const upload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const r = await api.post("/upload", fd, {headers: {"Content-Type":"multipart/form-data"}});
      setUploadResult(r.data);
    } catch (err) {
      alert(err?.response?.data?.detail || "CSV analysis failed.");
    } finally { setBusy(false); }
  };

  const downloadReport = async () => {
    if (!result) return;
    const r = await api.post("/report", {
      patient: form.patient_name,
      risk_level: result.risk_level,
      probability: `${(result.probability*100).toFixed(2)}%`,
      prediction: result.prediction,
      explanation: result.explanation
    }, {responseType:"blob"});
    const url = URL.createObjectURL(r.data);
    const a = document.createElement("a");
    a.href = url; a.download = "healytics-report.pdf"; a.click();
    URL.revokeObjectURL(url);
  };

  if (!loggedIn) {
    return (
      <div className="login-page">
        <Card className="login-card">
          <div className="brand large"><HeartPulse size={30}/> Healytics</div>
          <p className="muted">AI/ML Clinical Data Insights & Risk Prediction</p>
          <form onSubmit={doLogin} className="stack">
            <label>Username<input value={login.username} onChange={e=>setLogin({...login,username:e.target.value})}/></label>
            <label>Password<input type="password" value={login.password} onChange={e=>setLogin({...login,password:e.target.value})}/></label>
            <button className="primary" disabled={busy}><LogIn size={18}/> Sign in</button>
          </form>
          <div className="demo-note">Demo credentials: <b>demo</b> / <b>healytics123</b></div>
        </Card>
      </div>
    );
  }

  const nav = [
    ["dashboard","Dashboard",BarChart3],
    ["predict","Risk Prediction",Activity],
    ["dataset","Dataset Analysis",Database],
    ["history","Prediction History",FileText]
  ];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand"><HeartPulse/> Healytics</div>
        <div className="small">AI-ML Clinical Insights</div>
        <nav>
          {nav.map(([id,label,Icon]) => <button key={id} className={tab===id?"active":""} onClick={()=>setTab(id)}><Icon size={18}/>{label}</button>)}
        </nav>
        <div className="side-bottom">
          <div className="demo-note">Academic project • Decision support demo</div>
          <button onClick={()=>{localStorage.removeItem("healytics_token");setLoggedIn(false)}}>Sign out</button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><h1>{nav.find(x=>x[0]===tab)?.[1] || "Healytics"}</h1><span className="muted">Clinical analytics workspace</span></div>
          <div className="status"><span className="dot"></span> API Online</div>
        </header>

        {tab==="dashboard" && <Dashboard stats={stats} history={history}/>}
        {tab==="predict" && <Prediction form={form} setForm={setForm} predict={predict} result={result} busy={busy} downloadReport={downloadReport}/>}
        {tab==="dataset" && <Dataset upload={upload} result={uploadResult} busy={busy}/>}
        {tab==="history" && <History history={history}/>}
      </main>
    </div>
  );
}

function Dashboard({stats,history}) {
  return <div className="content">
    <div className="hero">
      <div><span className="eyebrow">HEALTH ANALYTICS</span><h2>Turn clinical data into explainable insights.</h2><p>Upload structured data, run ML analysis, inspect risk factors, and keep a prediction history.</p></div>
      <div className="hero-icon"><Brain size={54}/></div>
    </div>
    <div className="grid4">
      <Card><div className="metric-label">Analyzed</div><div className="metric">{stats.total_analyzed}</div><div className="metric-sub">patient records</div></Card>
      <Card><div className="metric-label">High Risk</div><div className="metric danger">{stats.high_risk_cases}</div><div className="metric-sub">model predictions</div></Card>
      <Card><div className="metric-label">Low Risk</div><div className="metric">{stats.low_risk_cases}</div><div className="metric-sub">model predictions</div></Card>
      <Card><div className="metric-label">Average Risk</div><div className="metric">{(stats.average_risk_probability*100).toFixed(1)}%</div><div className="metric-sub">probability score</div></Card>
    </div>
    <div className="grid2">
      <Card><h3>Risk distribution</h3>
        <div className="bar-chart">
          <div className="bar-wrap"><div className="bar high" style={{height:`${Math.max(8,stats.high_risk_cases/(stats.total_analyzed||1)*100)}%`}}></div><span>High</span></div>
          <div className="bar-wrap"><div className="bar low" style={{height:`${Math.max(8,stats.low_risk_cases/(stats.total_analyzed||1)*100)}%`}}></div><span>Low</span></div>
        </div>
      </Card>
      <Card><h3>Recent analyses</h3>
        {history.slice(0,5).map(r=><div className="history-row" key={r.id}><span>{r.patient_name}</span><b className={r.prediction_result?"danger-text":"success-text"}>{r.risk_level}</b><span>{(r.probability_score*100).toFixed(1)}%</span></div>)}
        {!history.length && <p className="muted">No predictions yet. Run the first analysis.</p>}
      </Card>
    </div>
  </div>
}

function Prediction({form,setForm,predict,result,busy,downloadReport}) {
  const fields = [
    ["age","Age"],["trestbps","Resting BP"],["chol","Cholesterol"],["thalach","Max Heart Rate"],["oldpeak","Oldpeak"],["ca","Major Vessels"]
  ];
  return <div className="content">
    <div className="grid2">
      <Card><h3><Activity size={20}/> Patient Risk Prediction</h3><p className="muted">Cleveland/UCI-style 13-feature input used by the project.</p>
        <form onSubmit={predict} className="form-grid">
          <label className="full">Patient Name<input value={form.patient_name} onChange={e=>setForm({...form,patient_name:e.target.value})}/></label>
          {fields.map(([k,l])=><label key={k}>{l}<input type="number" step={k==="oldpeak"?"0.1":"1"} value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})} required/></label>)}
          <Select label="Sex" value={form.sex} set={v=>setForm({...form,sex:v})} options={[[1,"Male"],[0,"Female"]]}/>
          <Select label="Chest Pain" value={form.cp} set={v=>setForm({...form,cp:v})} options={[[0,"Type 0"],[1,"Type 1"],[2,"Type 2"],[3,"Type 3"]]}/>
          <Select label="Fasting Sugar >120" value={form.fbs} set={v=>setForm({...form,fbs:v})} options={[[0,"No"],[1,"Yes"]]}/>
          <Select label="Rest ECG" value={form.restecg} set={v=>setForm({...form,restecg:v})} options={[[0,"0"],[1,"1"],[2,"2"]]}/>
          <Select label="Exercise Angina" value={form.exang} set={v=>setForm({...form,exang:v})} options={[[0,"No"],[1,"Yes"]]}/>
          <Select label="Slope" value={form.slope} set={v=>setForm({...form,slope:v})} options={[[0,"0"],[1,"1"],[2,"2"],[3,"3"]]}/>
          <Select label="Thal" value={form.thal} set={v=>setForm({...form,thal:v})} options={[[0,"0"],[1,"1"],[2,"2"],[3,"3"]]}/>
          <button className="primary full" disabled={busy}>{busy?"Analyzing…":"Run Risk Analysis"}</button>
        </form>
      </Card>
      <Card className="result-card">
        {!result ? <div className="empty"><Brain size={44}/><h3>Analysis result</h3><p>Submit the patient inputs to generate a risk score and explanation.</p></div> :
          <div>
            <div className="result-top"><div><span className="muted">Risk level</span><h2 className={result.prediction?"danger-text":"success-text"}>{result.risk_level}</h2></div><div className="score">{(result.probability*100).toFixed(1)}%</div></div>
            <div className="progress"><div style={{width:`${result.probability*100}%`}}></div></div>
            <div className="notice"><AlertTriangle size={18}/><span>Research/demo output — not a diagnosis.</span></div>
            <h3>Explainable factors</h3>
            {result.explanation.map((x,i)=><div className="factor" key={i}><span>{x.feature}</span><b>{x.impact}</b></div>)}
            <button className="secondary" onClick={downloadReport}><FileText size={17}/> Download PDF Report</button>
          </div>}
      </Card>
    </div>
  </div>
}

function Select({label,value,set,options}) {
  return <label>{label}<select value={value} onChange={e=>set(Number(e.target.value))}>{options.map(([v,l])=><option value={v} key={v}>{l}</option>)}</select></label>
}

function Dataset({upload,result,busy}) {
  return <div className="content">
    <Card className="upload-card"><Upload size={36}/><h2>Upload a clinical CSV</h2><p className="muted">The strategy engine checks the target column and chooses classification or regression.</p>
      <label className="upload-btn"><Upload size={17}/> Choose CSV<input type="file" accept=".csv" onChange={upload}/></label>
      {busy && <p>Analyzing dataset…</p>}
    </Card>
    {result && <div className="grid2">
      <Card><h3>Dataset summary</h3><div className="summary-list"><span>Rows<b>{result.rows}</b></span><span>Columns<b>{result.columns}</b></span><span>Target<b>{result.target}</b></span><span>Missing values<b>{result.missing_values}</b></span></div><div className="strategy"><Brain/> {result.strategy}</div></Card>
      <Card><h3>Evaluation</h3>{Object.entries(result.metrics).map(([k,v])=><div className="history-row" key={k}><span>{k}</span><b>{v}</b></div>)}</Card>
      <Card className="full-card"><h3>Preview</h3><div className="table-wrap"><table><thead><tr>{Object.keys(result.preview[0]||{}).map(k=><th key={k}>{k}</th>)}</tr></thead><tbody>{result.preview.map((row,i)=><tr key={i}>{Object.values(row).map((v,j)=><td key={j}>{String(v)}</td>)}</tr>)}</tbody></table></div></Card>
    </div>}
  </div>
}

function History({history}) {
  return <div className="content"><Card><h3><FileText size={20}/> Prediction History</h3><div className="table-wrap"><table><thead><tr><th>Patient</th><th>Risk</th><th>Probability</th><th>Date</th></tr></thead><tbody>{history.map(r=><tr key={r.id}><td>{r.patient_name}</td><td className={r.prediction_result?"danger-text":"success-text"}>{r.risk_level}</td><td>{(r.probability_score*100).toFixed(2)}%</td><td>{new Date(r.timestamp).toLocaleString()}</td></tr>)}</tbody></table></div>{!history.length&&<p className="muted">No records yet.</p>}</Card></div>
}

export default App;
