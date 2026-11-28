"""
Reusable Streamlit UI components for GYMSENSE.
"""

import time
from datetime import datetime
import streamlit as st

from gymsense.constants import COLOR_BAD, COLOR_GOOD, COLOR_WARN
from gymsense.export_service import build_session_entry, serialize_sessions


def render_header():
    st.markdown(
        """
        <div style="text-align:center;padding:1.5rem 0 2rem;">
            <div class="logo-text">AI Virtual Gym Trainer</div>
            <div class="logo-sub">Real-time Pose Detection • Form Analysis • Performance Tracking</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_exercise_grid(exercises, current_exercise, on_select):
    st.markdown("### Choose Your Exercise")
    cols = st.columns(4)
    for idx, (name, cfg) in enumerate(exercises.items()):
        with cols[idx % 4]:
            selected = current_exercise == name
            cls = "exercise-card selected" if selected else "exercise-card"
            tcls = "type-reps" if cfg["type"] == "reps" else "type-hold"
            tlabel = "REPS" if cfg["type"] == "reps" else "HOLD"
            st.markdown(
                f"""
                <div class="{cls}">
                    <div class="exercise-icon">{cfg['icon']}</div>
                    <div class="exercise-name">{name}</div>
                    <span class="exercise-type {tcls}">{tlabel}</span>
                    <div class="exercise-hint">📷 {cfg['camera_hint']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Select {name}", key=f"sel_{name}", use_container_width=True):
                on_select(name)
                st.rerun()


def render_feedback(state, cfg, fb, fc, placeholder=None):
    target = placeholder.container() if placeholder is not None else st.container()
    with target:
        st.markdown("### 💡 Form Feedback")
        if fc == COLOR_GOOD:
            cls, icon = "feedback-good", "✅"
        elif fc == COLOR_WARN:
            cls, icon = "feedback-warning", "⚠️"
        elif fc == COLOR_BAD:
            cls, icon = "feedback-bad", "❌"
        else:
            cls, icon = "feedback-neutral", "ℹ️"

        st.markdown(
            f'<div class="feedback-banner {cls}"><span>{icon}</span><span>{fb}</span></div>',
            unsafe_allow_html=True,
        )

        if cfg["type"] == "reps":
            st.markdown(
                f'<div style="text-align:center;margin:1.5rem 0;">'
                f'<div style="font-size:4rem;font-weight:800;color:var(--primary);font-variant-numeric:tabular-nums;">{state["reps"]}</div>'
                f'<div style="color:var(--text-dim);text-transform:uppercase;letter-spacing:.1em;font-size:.8rem;">REPS COMPLETED</div></div>',
                unsafe_allow_html=True,
            )
        else:
            mins, secs = divmod(int(state["hold_seconds"]), 60)
            st.markdown(
                f'<div style="text-align:center;margin:1.5rem 0;">'
                f'<div style="font-size:4rem;font-weight:800;color:var(--success);font-variant-numeric:tabular-nums;">{mins:02d}:{secs:02d}</div>'
                f'<div style="color:var(--text-dim);text-transform:uppercase;letter-spacing:.1em;font-size:.8rem;">HOLD TIME</div></div>',
                unsafe_allow_html=True,
            )

        if cfg["type"] == "reps" and state.get("min_angle", 180) < 180:
            prog = max(0, min(1, (180 - state["min_angle"]) / 80))
            st.markdown(
                f"""
                <div style="margin-top:1rem;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:.5rem;">
                        <span style="color:var(--text-dim);font-size:.85rem;">Depth</span>
                        <span style="color:var(--primary);font-weight:600;">{state["min_angle"]:.0f}°</span>
                    </div>
                    <div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;">
                        <div style="width:{prog*100}%;height:100%;background:linear-gradient(90deg,var(--primary),var(--secondary));border-radius:4px;transition:width .2s;"></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;margin-top:.5rem;font-size:.7rem;color:var(--text-dim);">
                        <span>Stand (180°)</span><span>Parallel (90°)</span><span>Deep (&lt;90°)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_instructions(cfg):
    st.markdown("### 📋 How to Perform")
    steps_html = "".join(
        f'<div class="instruction-step"><div class="step-num">{i}</div><div class="step-text">{step}</div></div>'
        for i, step in enumerate(cfg["steps"], 1)
    )
    st.markdown(f'<div class="instruction-panel">{steps_html}</div>', unsafe_allow_html=True)


def render_history(history):
    st.markdown("### 📜 Session History")
    if not history:
        st.info("No sessions yet. Complete a workout to see history.")
        return
    t_sess = len(history)
    t_reps = sum(h.get("reps", 0) for h in history)
    t_hold = sum(h.get("hold_seconds", 0) for h in history)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sessions", t_sess)
    c2.metric("Total Reps", t_reps)
    c3.metric("Total Hold", f"{int(t_hold)}s")

    for h in history:
        with st.expander(f"{h['exercise']} • {h['timestamp']} • {h.get('reps', 0)} reps / {h.get('hold_seconds', 0)}s"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Exercise:** {h['exercise']}")
                st.write(f"**Date:** {h['timestamp']}")
                st.write(f"**Duration:** {h.get('duration', 0)//60}:{h.get('duration', 0)%60:02d}")
            with col2:
                st.write(f"**Reps:** {h.get('reps', 0)}")
                st.write(f"**Hold:** {h.get('hold_seconds', 0)}s")
                st.write(f"**Min Angle:** {h.get('min_angle', 180)}°")
                st.write(f"**Max Angle:** {h.get('max_angle', 0)}°")
            st.write(f"**Feedback:** {h.get('feedback', 'N/A')}")


def render_sidebar(state, exercises, history, on_select_exercise, on_release_camera):
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        if not state["exercise"]:
            st.info("Select an exercise card on the main screen to start.")
            return

        names = list(exercises.keys())
        cur = names.index(state["exercise"]) if state["exercise"] in names else 0
        sel = st.selectbox("Quick Switch", names, index=cur, key="ex_sel")
        if sel != state["exercise"]:
            on_select_exercise(sel)
            st.rerun()

        cam_modes = ["Browser (WebRTC)", "Local Webcam (OpenCV)"]
        cur_mode = state.get("camera_mode", "Browser (WebRTC)")
        mode_idx = cam_modes.index(cur_mode) if cur_mode in cam_modes else 0
        chosen_mode = st.radio("Camera Source", cam_modes, index=mode_idx, key="cam_mode_radio")
        if chosen_mode != cur_mode:
            on_release_camera()
            state["camera_mode"] = chosen_mode
            state["running"] = False
            state["camera_initialized"] = False
            state["camera_error"] = None
            st.rerun()

        if st.button("← All Exercises", use_container_width=True, key="sb_home"):
            on_release_camera()
            state["exercise"] = None
            state["running"] = False
            state["camera_initialized"] = False
            st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Live Stats")
        cfg = exercises[state["exercise"]]
        c1, c2 = st.columns(2)
        with c1:
            if cfg["type"] == "reps":
                st.markdown(f'<div class="metric-card"><div class="metric-label">Reps</div><div class="metric-value" style="color:var(--primary)">{state["reps"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Hold</div><div class="metric-value" style="color:var(--success)">{int(state["hold_seconds"])}<span class="metric-unit">s</span></div></div>', unsafe_allow_html=True)
        with c2:
            if cfg["type"] == "reps":
                prog = max(0, min(1, (180 - state.get("min_angle", 180)) / 80))
                st.markdown(f'<div class="metric-card"><div class="metric-label">Progress</div><div class="metric-value" style="color:var(--secondary)">{int(prog*100)}<span class="metric-unit">%</span></div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Max Angle</div><div class="metric-value" style="color:var(--secondary)">{state.get("max_angle", 0)}<span class="metric-unit">°</span></div></div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Min Angle</div><div class="metric-value" style="color:var(--warning)">{state.get("min_angle", 180)}<span class="metric-unit">°</span></div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Max Angle</div><div class="metric-value" style="color:var(--warning)">{state.get("max_angle", 0)}<span class="metric-unit">°</span></div></div>', unsafe_allow_html=True)

        if state.get("start_time"):
            dur = int(time.time() - state["start_time"])
            st.markdown(f'<div class="metric-card" style="margin-top:.5rem"><div class="metric-label">Session</div><div class="metric-value" style="color:var(--secondary)">{dur//60}:{dur%60:02d}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📥 Export Data")
        fmt = st.radio("Format", ["CSV", "JSON"], horizontal=True, key="exp_fmt")
        col1, col2 = st.columns(2)
        with col1:
            out, mime, ext = serialize_sessions([build_session_entry(state)], fmt)
            st.download_button(
                f"📥 Current",
                out,
                f"gym_{state['exercise'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}",
                mime=mime,
                use_container_width=True,
                key="dl_cur",
            )
        with col2:
            out_h, mime_h, ext_h = serialize_sessions(history, fmt)
            st.download_button(
                f"📊 History",
                out_h,
                f"gym_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext_h}",
                mime=mime_h,
                use_container_width=True,
                key="dl_hist",
            )

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info(cfg["description"])
        with st.expander("📋 How to Perform"):
            for idx, step in enumerate(cfg["steps"], 1):
                st.markdown(f"**{idx}.** {step}")
        st.markdown("---")
        st.markdown(
            '<div style="text-align:center;color:var(--text-dim);font-size:.75rem;padding:1rem;">AI Virtual Gym Trainer v2.0<br>MediaPipe + WebRTC + Streamlit</div>',
            unsafe_allow_html=True,
        )
