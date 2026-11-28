"""
Dark-theme CSS styles for the GYMSENSE Streamlit application.
"""

import streamlit as st

DARK_THEME_CSS = """
<style>
:root {
    --bg: #0a0a0f;
    --bg-elevated: #12121a;
    --card: #1a1a24;
    --card-hover: #222230;
    --border: #2a2a3e;
    --primary: #e94560;
    --primary-glow: rgba(233, 69, 96, 0.3);
    --secondary: #f47c6f;
    --success: #07b38c;
    --warning: #f6ae2d;
    --text: #f0f0f5;
    --text-dim: #888899;
    --radius: 14px;
    --radius-sm: 8px;
    --shadow: 0 8px 32px rgba(0,0,0,0.4);
    --shadow-lg: 0 16px 48px rgba(0,0,0,0.5);
    --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

html, body, [class*="css"] { background: var(--bg) !important; color: var(--text) !important; }
.main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1500px; }
h1, h2, h3, h4, h5, h6 { color: var(--text) !important; font-weight: 600; }

.logo-text {
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    letter-spacing: -0.02em;
}
.logo-sub { color: var(--text-dim); font-size: 0.95rem; margin-top: 0.25rem; }

.metric-card {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.25rem; text-align: center; transition: var(--transition); box-shadow: var(--shadow);
}
.metric-card:hover { border-color: var(--primary); box-shadow: var(--shadow-lg); transform: translateY(-2px); }
.metric-value { font-size: 2.5rem; font-weight: 800; line-height: 1; margin: 0.5rem 0; }
.metric-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim); font-weight: 600; }
.metric-unit { font-size: 1rem; font-weight: 400; opacity: 0.7; }

.exercise-card {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.5rem; transition: var(--transition); text-align: center;
}
.exercise-card:hover { border-color: var(--primary); box-shadow: var(--shadow-lg); transform: translateY(-4px); }
.exercise-card.selected { border-color: var(--primary); box-shadow: 0 0 0 2px var(--primary-glow), var(--shadow); }
.exercise-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.exercise-name { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem; }
.exercise-type {
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em;
    padding: 0.2rem 0.6rem; border-radius: 100px; display: inline-block; font-weight: 600;
}
.type-reps { background: rgba(233, 69, 96, 0.15); color: var(--secondary); }
.type-hold { background: rgba(7, 179, 140, 0.15); color: var(--success); }
.exercise-hint { font-size: 0.75rem; color: var(--text-dim); margin-top: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 0.35rem; }

.feedback-banner {
    padding: 1rem 1.5rem; border-radius: var(--radius);
    font-weight: 600; font-size: 1.05rem; text-align: center;
    transition: var(--transition); display: flex; align-items: center; justify-content: center; gap: 0.75rem;
    min-height: 70px; border: 1px solid transparent;
}
.feedback-good { background: linear-gradient(135deg, rgba(7,179,140,0.12), rgba(7,179,140,0.06)); border-color: var(--success); color: var(--success); }
.feedback-warning { background: linear-gradient(135deg, rgba(246,174,45,0.12), rgba(246,174,45,0.06)); border-color: var(--warning); color: var(--warning); }
.feedback-bad { background: linear-gradient(135deg, rgba(233,69,96,0.12), rgba(233,69,96,0.06)); border-color: var(--primary); color: var(--primary); }
.feedback-neutral { background: var(--card); border-color: var(--border); color: var(--text-dim); }

.camera-wrap {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    overflow: hidden; box-shadow: var(--shadow); position: relative;
}

.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white; border: none; border-radius: var(--radius-sm);
    padding: 0.65rem 1.25rem; font-weight: 600; font-size: 0.9rem;
    transition: var(--transition); box-shadow: 0 4px 16px var(--primary-glow);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px var(--primary-glow); }
.stButton > button[kind="secondary"] { background: var(--card); border: 1px solid var(--border); box-shadow: none; color: var(--text); }

section[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
video { border-radius: var(--radius); }

.instruction-panel {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem; margin-top: 1rem;
}
.instruction-step { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem 0; border-bottom: 1px solid var(--border); }
.instruction-step:last-child { border-bottom: none; }
.step-num {
    background: var(--primary); color: white; width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
}
.step-text { color: var(--text); font-size: 0.9rem; line-height: 1.4; }

.camera-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(233,69,96,0.15); color: var(--secondary);
    padding: 0.5rem 1rem; border-radius: 100px; font-size: 0.85rem; font-weight: 500; margin-bottom: 1rem;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }
</style>
"""


def inject_styles():
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
