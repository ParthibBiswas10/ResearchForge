"""
ResearchForge - Streamlit UI
Frontend for the agentic research pipeline defined in agents.py

Run with:
    streamlit run app.py
"""

import time
import streamlit as st

from agents import search_agent, scrape_agent, writer_chain, critic_chain


def invoke_with_retry(runnable, payload, max_retries=4, base_delay=8):
    """Invoke a chain/agent, retrying on Groq 429 rate-limit errors with backoff."""
    last_exc = None
    for attempt in range(max_retries):
        try:
            return runnable.invoke(payload)
        except Exception as exc:
            msg = str(exc)
            last_exc = exc
            if "rate_limit" in msg or "429" in msg:
                time.sleep(base_delay * (attempt + 1))
                continue
            raise
    raise last_exc


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchForge",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,500;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --ink: #1B1712;
    --ink-2: #241F19;
    --paper: #EDE6D6;
    --muted: #9C9385;
    --brass: #0096c7;
    --brass-soft: rgba(0,150,199,0.35);
    --sage: #7FA588;
    --rust: #B85C4A;
    --rule: rgba(237,230,214,0.12);
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--paper);
}

.stApp {
    background: var(--ink);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 3.5rem 5rem; max-width: 1180px; }

/* ── Hero ── */
.hero {
    padding: 1rem 0 2.5rem;
    border-bottom: 1px solid var(--rule);
    margin-bottom: 2.5rem;
}
.hero-caption {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 400;
    font-size: 1.05rem;
    color: var(--muted);
    margin-bottom: 0.6rem;
}
.hero h1 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(2.4rem, 4.4vw, 3.4rem);
    letter-spacing: -0.01em;
    color: var(--paper);
    margin: 0 0 0.9rem;
}
.hero-sub {
    font-size: 1rem;
    font-weight: 400;
    color: var(--muted);
    max-width: 620px;
    line-height: 1.7;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 1rem;
    color: var(--muted);
    margin: 0 0 1.1rem;
}

/* ── Input panel ── */
.brief-panel {
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}

.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid var(--rule) !important;
    border-radius: 0 !important;
    color: var(--paper) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.5rem 0.1rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-bottom-color: var(--brass) !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus-visible {
    outline: 1px solid var(--brass) !important;
    outline-offset: 3px;
}
.stTextInput > label {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.02em !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
}

.stButton > button {
    background: var(--brass) !important;
    color: var(--ink) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.65rem 1.6rem !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    width: 100%;
    margin-top: 0.5rem;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}
.stButton > button:focus-visible {
    outline: 1px solid var(--paper) !important;
    outline-offset: 2px;
}
.stDownloadButton > button {
    background: var(--brass) !important;
    color: var(--ink) !important;
    border: none !important;
}
.stDownloadButton > button:hover {
    opacity: 0.88 !important;
}

.try-line {
    font-size: 0.85rem;
    color: var(--muted);
    margin: 1.1rem 0 2rem;
    line-height: 1.9;
}
.try-line em { font-style: italic; color: var(--muted); margin-right: 0.5rem; }
.try-chip {
    display: inline-block;
    border-bottom: 1px dotted var(--rule);
    color: var(--paper);
    padding: 0 0.1rem 0.1rem;
    margin-right: 1rem;
}

/* ── Timeline ── */
.timeline { position: relative; padding-left: 0.1rem; }
.timeline-item {
    display: flex;
    gap: 1.1rem;
    position: relative;
    padding-bottom: 1.9rem;
}
.timeline-item:last-child { padding-bottom: 0; }
.timeline-item::before {
    content: '';
    position: absolute;
    left: 0.72rem;
    top: 1.7rem;
    bottom: -0.3rem;
    width: 1px;
    background: var(--rule);
}
.timeline-item:last-child::before { display: none; }

.marker {
    width: 1.45rem;
    height: 1.45rem;
    border-radius: 50%;
    border: 1.5px solid var(--rule);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted);
    background: var(--ink);
    position: relative;
    z-index: 1;
}
.marker.running {
    border-color: var(--brass);
    color: var(--brass);
    box-shadow: 0 0 0 3px var(--brass-soft);
    animation: pulse 1.6s ease-in-out infinite;
}
.marker.done {
    border-color: var(--sage);
    background: var(--sage);
    color: var(--ink);
}
.marker.error {
    border-color: var(--rust);
    background: var(--rust);
    color: var(--ink);
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 3px var(--brass-soft); }
    50% { box-shadow: 0 0 0 5px transparent; }
}
@media (prefers-reduced-motion: reduce) {
    .marker.running { animation: none; }
}

.step-body { flex: 1; padding-top: 0.05rem; }
.step-row { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; }
.step-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 0.98rem;
    color: var(--paper);
}
.step-status {
    font-size: 0.8rem;
    color: var(--muted);
    white-space: nowrap;
}
.step-status.running { color: var(--brass); }
.step-status.done { color: var(--sage); }
.step-status.error { color: var(--rust); }
.step-desc {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.2rem;
    line-height: 1.5;
}

/* ── Divider ── */
.rule { height: 1px; background: var(--rule); margin: 2.8rem 0; border: none; }

/* ── Results ── */
.report-panel {
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 2.4rem 2.8rem;
    margin-top: 0.5rem;
}
.report-panel, .report-panel p, .report-panel li {
    font-family: 'Fraunces', serif;
    font-weight: 300;
    font-size: 1.08rem;
    line-height: 1.75;
    color: var(--paper);
}
.report-panel h1, .report-panel h2, .report-panel h3 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    color: var(--paper);
}

.feedback-panel {
    border-left: 2px solid var(--brass);
    padding: 0.3rem 0 0.3rem 1.6rem;
    margin-top: 0.5rem;
}
.feedback-panel, .feedback-panel p, .feedback-panel li {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 400;
    font-size: 1rem;
    line-height: 1.7;
    color: var(--paper);
}

.raw-output {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    color: var(--muted);
    white-space: pre-wrap;
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 1.4rem 1.6rem;
}

details summary {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.82rem !important;
    color: var(--muted) !important;
    cursor: pointer;
}

.stSpinner > div { color: var(--brass) !important; }

.error-banner {
    border: 1px solid var(--rust);
    border-radius: 3px;
    padding: 1.4rem 1.8rem;
    color: var(--paper);
    font-size: 0.88rem;
    line-height: 1.6;
}
.error-banner strong { color: var(--rust); font-weight: 600; }

.footer-note {
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 3.5rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a timeline step ────────────────────────────────────────────
def timeline_step(num: str, title: str, state: str, desc: str = "", is_last: bool = False):
    marker_content = {"waiting": num, "running": num, "done": "✓", "error": "✕"}.get(state, num)
    status_text = {
        "waiting": "Waiting",
        "running": "In progress",
        "done": "Complete",
        "error": "Failed",
    }.get(state, "Waiting")
    marker_cls = state if state in ("running", "done", "error") else ""
    status_cls = state if state in ("running", "done", "error") else ""

    st.markdown(f"""
    <div class="timeline-item">
        <div class="marker {marker_cls}">{marker_content}</div>
        <div class="step-body">
            <div class="step-row">
                <span class="step-title">{title}</span>
                <span class="step-status {status_cls}">{status_text}</span>
            </div>
            {"<div class='step-desc'>"+desc+"</div>" if desc else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key, default in (
    ("results", {}),
    ("running", False),
    ("done", False),
    ("error", None),
    ("topic_run", ""),
):
    if key not in st.session_state:
        st.session_state[key] = default


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-caption">A multi-agent research pipeline</div>
    <h1>ResearchForge</h1>
    <p class="hero-sub">
        Four agents work in sequence — searching, scraping, writing, and reviewing —
        to turn a topic into a researched, critiqued report.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Layout: brief on the left, ledger on the right ────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="section-label">The brief</div>', unsafe_allow_html=True)
    st.markdown('<div class="brief-panel">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research topic",
        placeholder="Enter your Topic",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("Run pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    examples = ["LLM agents in 2025", "CRISPR gene editing", "Fusion energy progress"]
    chips = "".join(f'<span class="try-chip">{ex}</span>' for ex in examples)
    st.markdown(f'<div class="try-line"><em>Try</em>{chips}</div>', unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-label">The ledger</div>', unsafe_allow_html=True)

    r = st.session_state.results
    steps = ["search", "reader", "writer", "critic"]

    def step_state(step):
        if step in r:
            return "done"
        if st.session_state.error and st.session_state.error.get("step") == step:
            return "error"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    timeline_step("1", "Search agent", step_state("search"), "Gathers recent sources from the web")
    timeline_step("2", "Scrape agent", step_state("reader"), "Reads the most relevant source in depth")
    timeline_step("3", "Writer chain", step_state("writer"), "Drafts the report from the research gathered")
    timeline_step("4", "Critic chain", step_state("critic"), "Reviews the report and scores it")
    st.markdown('</div>', unsafe_allow_html=True)


# ── Kick off a run ────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.error = None
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.topic_run = topic.strip()
        st.rerun()

# ── Run pipeline (resumes at the first incomplete step on each rerun) ────────
if st.session_state.running and not st.session_state.done:
    results = dict(st.session_state.results)
    topic_val = st.session_state.topic_run

    try:
        # ── Step 1: Search ──
        if "search" not in results:
            with st.spinner("Searching for sources..."):
                agent1 = search_agent()
                sr = invoke_with_retry(agent1, {
                    "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
                })
                results["search"] = sr["messages"][-1].content
                st.session_state.results = dict(results)

        # ── Step 2: Scrape ──
        if "reader" not in results:
            with st.spinner("Reading the most relevant source..."):
                agent2 = scrape_agent()
                rr = invoke_with_retry(agent2, {
                    "messages": [("user",
                        f"Below are web search results about '{topic_val}'. "
                        f"Each result is formatted as: title, then its URL on the next line, "
                        f"then a content snippet. Pick the single most relevant URL from the "
                        f"list below (copy it exactly as written) and scrape it for deeper content.\n\n"
                        f"Search Results:\n{results['search'][:3000]}"
                    )]
                })
                results["reader"] = rr["messages"][-1].content
                st.session_state.results = dict(results)

        # ── Step 3: Writer ──
        if "writer" not in results:
            with st.spinner("Drafting the report..."):
                research_combined = (
                    f"SEARCH RESULTS:\n{results['search'][:2500]}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{results['reader'][:2500]}"
                )
                results["writer"] = invoke_with_retry(writer_chain, {
                    "topic": topic_val,
                    "research": research_combined
                })
                st.session_state.results = dict(results)

        # ── Step 4: Critic ──
        if "critic" not in results:
            with st.spinner("Reviewing the report..."):
                results["critic"] = invoke_with_retry(critic_chain, {
                    "report": results["writer"]
                })
                st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as exc:
        failed_step = next((s for s in steps if s not in results), "search")
        st.session_state.error = {"step": failed_step, "message": str(exc)}
        st.session_state.running = False
        st.rerun()


# ── Error display ─────────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="error-banner">
        <strong>The pipeline stopped at: {st.session_state.error['step']}.</strong><br><br>
        {st.session_state.error['message']}
    </div>
    """, unsafe_allow_html=True)


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">The findings</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("Search results, raw", expanded=False):
            st.markdown(f'<div class="raw-output">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Scraped content, raw", expanded=False):
            st.markdown(f'<div class="raw-output">{r["reader"]}</div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown('<div class="section-label" style="margin-top:2rem;">The report</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-panel">', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label="Download report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown('<div class="section-label" style="margin-top:2.2rem;">The critic\'s notes</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="feedback-panel">', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
    Built with a LangChain multi-agent pipeline, rendered in Streamlit.
</div>
""", unsafe_allow_html=True)