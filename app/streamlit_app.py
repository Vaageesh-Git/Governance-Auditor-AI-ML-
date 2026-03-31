import sys
import os
import html
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PATH (Preserved from original) ------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

# Mocking the Orchestrator for standalone UI testing (Replace with your actual import)
try:
    from core.orchestrator import Orchestrator
except ImportError:
    class MockMemory:
        def update(self, log): pass
    class MockTarget:
        def run(self, p): return "<p>Simulated AI Response containing some potentially unsafe text...</p>"
    class MockRed:
        def generate(self): return "Simulated adversarial prompt injected here."
    class MockJudge:
        def evaluate(self, p, r): return {"risk_score": 0.85, "flags": ["jailbreak_attempt"]}
    class MockPolicy:
        def decide(self, e, v): return "REVIEW" # Forces human review for demonstration
    class Orchestrator:
        def __init__(self):
            self.memory = MockMemory()
            self.target = MockTarget()
            self.red = MockRed()
            self.judge = MockJudge()
            self.policy = MockPolicy()

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="AI Governance Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ SESSION STATE ------------------
if "system" not in st.session_state:
    st.session_state.system = Orchestrator()
if "logs" not in st.session_state:
    st.session_state.logs = []
if "pending_review" not in st.session_state:
    st.session_state.pending_review = False
if "current_log" not in st.session_state:
    st.session_state.current_log = None
if "remaining_cycles" not in st.session_state:
    st.session_state.remaining_cycles = 0
if "violation_count" not in st.session_state:
    st.session_state.violation_count = 0  # Explicitly tracking violations per your logic

# ------------------ SAFE RENDER ------------------
def is_safe_html(content):
    dangerous = ["<script", "javascript:", "onerror=", "onclick="]
    return not any(x in content.lower() for x in dangerous)

def render_response(content: str):
    if "<" in content and is_safe_html(content):
        components.html(content, height=250, scrolling=True)
    else:
        safe = html.escape(content)
        st.markdown(f'<div class="response-box">{safe}</div>', unsafe_allow_html=True)

# ------------------ CSS STYLING ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at top, #0f172a, #020617);
        color: #f8fafc;
    }
    .main-header {
        display:flex; justify-content:space-between; align-items:center;
        padding:25px 30px; border-radius:16px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(12px);
        margin-bottom: 25px;
    }
    .badge {
        background: linear-gradient(135deg, #10b981, #059669);
        padding:8px 16px; border-radius:50px;
        font-weight:600; font-size: 14px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }
    .card {
        background: rgba(30, 41, 59, 0.5);
        padding:20px; border-radius:14px;
        text-align:center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .card h2 { margin: 0; font-size: 36px; font-weight: 800; color: #38bdf8; }
    .card p { margin: 5px 0 0 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    
    .response-box {
        background: #020617; padding:16px; border-radius:10px;
        border:1px solid #1e293b; font-family:monospace; color:#22d3ee;
        white-space:pre-wrap; max-height: 250px; overflow-y: auto;
    }
    .section-title {
        font-size:22px; font-weight:700; margin-top:30px; margin-bottom: 15px;
        border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 10px;
    }
    .review-box {
        background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 20px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR & RUN CONTROLS ------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8103/8103126.png", width=60)
    st.markdown("### Control Panel")
    st.markdown("Run automated safety audits against the target model.")
    
    cycles = st.slider("Audit Cycles to Run", min_value=1, max_value=10, value=3)
    
    if st.button("🚀 Execute Audit Sequence", use_container_width=True, type="primary"):
        st.session_state.remaining_cycles = cycles
        
    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.logs = []
        st.session_state.violation_count = 0
        st.session_state.pending_review = False
        st.rerun()

# ------------------ HEADER ------------------
st.markdown("""
<div class="main-header">
    <div>
        <div style="font-size:32px;font-weight:800;letter-spacing:-0.5px;">🛡️ AI Governance Auditor</div>
        <div style="opacity:0.7; font-size: 15px; margin-top: 4px;">Safety · Alignment · Policy Compliance Dashboard</div>
    </div>
    <div class="badge">🟢 GROQ · llama-3.3-70b · LIVE</div>
</div>
""", unsafe_allow_html=True)

# ------------------ METRICS DASHBOARD ------------------
total_logs = len(st.session_state.logs)
violations = st.session_state.violation_count
safe_count = total_logs - violations
safe_rate = round((safe_count / total_logs * 100), 1) if total_logs > 0 else 100.0

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="card"><h2>{total_logs}</h2><p>Total Audits</p></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h2>{safe_count}</h2><p>Safe Outputs</p></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h2 style="color:#f87171;">{violations}</h2><p>Violations</p></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card"><h2 style="color:#10b981;">{safe_rate}%</h2><p>Safety Score</p></div>', unsafe_allow_html=True)

# ------------------ GRAPHS & VISUALIZATIONS ------------------
if total_logs > 0:
    st.markdown('<div class="section-title">📊 Analytics Overview</div>', unsafe_allow_html=True)
    g_col1, g_col2 = st.columns([1, 2])
    
    with g_col1:
        # Donut Chart for Safe vs Violations
        labels = ['Safe', 'Violations']
        values = [safe_count, violations]
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, 
                                           marker_colors=['#10b981', '#ef4444'])])
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), 
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='white'), showlegend=False)
        fig_donut.add_annotation(text=f"{safe_rate}%<br>Safe", x=0.5, y=0.5, font_size=20, showarrow=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    with g_col2:
        # Line chart for cumulative audits over time
        decisions = [log.get("decision", "SAFE") for log in st.session_state.logs]
        df = pd.DataFrame({
            "Run": range(1, total_logs + 1),
            "Cumulative Violations": [decisions[:i+1].count("REJECTED") for i in range(total_logs)]
        })
        fig_line = px.line(df, x="Run", y="Cumulative Violations", markers=True, 
                           color_discrete_sequence=['#ef4444'])
        fig_line.update_layout(margin=dict(t=20, b=20, l=20, r=20),
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(color='white'), xaxis_title="Audit Cycle", yaxis_title="Violations Detected")
        st.plotly_chart(fig_line, use_container_width=True)

# ------------------ ENGINE (BACKGROUND PROCESSING) ------------------
if st.session_state.remaining_cycles > 0 and not st.session_state.pending_review:
    with st.spinner(f"Running audit cycle... ({st.session_state.remaining_cycles} remaining)"):
        system = st.session_state.system

        prompt = system.red.generate()
        response = system.target.run(prompt)
        evaluation = system.judge.evaluate(prompt, response)
        decision = system.policy.decide(evaluation, st.session_state.violation_count)

        log = {
            "prompt": prompt,
            "response": response,
            "evaluation": evaluation,
            "decision": decision,
        }

        if decision in ["ESCALATE", "CRITICAL", "REVIEW"]:
            st.session_state.pending_review = True
            st.session_state.current_log = log
            st.rerun() # Stop engine to allow human review
        else:
            # Auto-processed
            if decision == "REJECTED":
                st.session_state.violation_count += 1
                
            if hasattr(system, 'memory') and hasattr(system.memory, 'update'):
                system.memory.update(log)
            st.session_state.logs.append(log)
            st.session_state.remaining_cycles -= 1
            st.rerun()

# ------------------ HUMAN REVIEW (CRITICAL ACTION REQUIRED) ------------------
if st.session_state.pending_review:
    log = st.session_state.current_log

    st.markdown('<div class="review-box">', unsafe_allow_html=True)
    st.markdown('<h3>⚠️ Critical Alert: Human Review Required</h3><p>The system flagged the following interaction for manual oversight.</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Adversarial Prompt", "🤖 Model Response", "⚖️ System Evaluation"])
    with tab1: st.info(log["prompt"])
    with tab2: render_response(log["response"])
    with tab3: st.json(log["evaluation"])

    col1, col2, col3 = st.columns([1, 1, 2])

    if col1.button("✅ Approve (Mark Safe)", use_container_width=True, type="primary"):
        log["decision"] = "APPROVED"
        # Logic rule applied: Violations NOT added if approved.
        if hasattr(st.session_state.system, 'memory') and hasattr(st.session_state.system.memory, 'update'):
            st.session_state.system.memory.update(log)
        st.session_state.logs.append(log)
        st.session_state.pending_review = False
        st.session_state.remaining_cycles -= 1
        st.rerun()

    if col2.button("❌ Reject (Log Violation)", use_container_width=True):
        log["decision"] = "REJECTED"
        # Logic rule applied: Violations added if human rejects.
        st.session_state.violation_count += 1 
        
        if hasattr(st.session_state.system, 'memory') and hasattr(st.session_state.system.memory, 'update'):
            st.session_state.system.memory.update(log)
        st.session_state.logs.append(log)
        st.session_state.pending_review = False
        st.session_state.remaining_cycles -= 1
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ HISTORY LOGS ------------------
if st.session_state.logs:
    st.markdown('<div class="section-title">📋 Audit Trail</div>', unsafe_allow_html=True)

    for i, log in enumerate(reversed(st.session_state.logs)):
        run_num = len(st.session_state.logs) - i
        decision_color = "#10b981" if log["decision"] in ["APPROVED", "SAFE"] else "#ef4444"
        
        with st.expander(f"Audit Run #{run_num} — Status: {log['decision']}"):
            st.markdown(f"**Decision:** <span style='color:{decision_color}; font-weight:bold;'>{log['decision']}</span>", unsafe_allow_html=True)
            
            c_hist1, c_hist2 = st.columns(2)
            with c_hist1:
                st.markdown("**Prompt Issued:**")
                st.code(log["prompt"], language="text")
            with c_hist2:
                st.markdown("**Evaluation:**")
                st.json(log["evaluation"])
                
            st.markdown("**Target Response Snippet:**")
            # Show the first 500 chars to save space in history
            render_response(log["response"][:500] + ("..." if len(log["response"]) > 500 else ""))