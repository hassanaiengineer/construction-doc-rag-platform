from __future__ import annotations

import os
import time

import requests
import streamlit as st


def _get_api_base_url() -> str:
    # Avoid using `st.secrets` directly: it raises FileNotFoundError if no secrets.toml exists.
    env_url = os.getenv("API_BASE_URL")
    if env_url:
        return env_url.rstrip("/")
    return "http://localhost:8000/v1"


API_BASE_URL = _get_api_base_url()

st.set_page_config(page_title="Construction Document RAG", layout="wide")


def api_get(path: str):
    resp = requests.get(f"{API_BASE_URL}{path}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, **kwargs):
    resp = requests.post(f"{API_BASE_URL}{path}", timeout=120, **kwargs)
    resp.raise_for_status()
    return resp.json()


def api_delete(path: str):
    resp = requests.delete(f"{API_BASE_URL}{path}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def list_documents():
    return api_get("/documents").get("documents", [])


def poll_status(doc_id: str):
    return api_get(f"/documents/{doc_id}/status")


def backend_health() -> bool:
    try:
        return api_get("/admin/health").get("status") == "ok"
    except Exception:
        return False


st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; }
      .rag-hero {
        padding: 1.25rem 1.25rem;
        border: 1px solid rgba(49, 51, 63, 0.14);
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(99,102,241,0.10), rgba(16,185,129,0.08));
        margin-bottom: 1rem;
      }
      .rag-hero h1 { margin: 0; font-size: 1.85rem; }
      .rag-hero p { margin: 0.35rem 0 0; opacity: 0.92; }
      .rag-pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.85rem;
        border: 1px solid rgba(49, 51, 63, 0.14);
        background: rgba(255,255,255,0.55);
        margin-right: 0.4rem;
      }
      .rag-muted { opacity: 0.8; font-size: 0.92rem; }
      .rag-card {
        border: 1px solid rgba(49, 51, 63, 0.14);
        border-radius: 14px;
        padding: 1rem;
        background: rgba(255,255,255,0.35);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="rag-hero">
      <h1>Construction Document RAG</h1>
      <p>Production-ready document intelligence (OCR + retrieval + citations).</p>
      <div style="margin-top: 0.85rem">
        <span class="rag-pill">FastAPI</span>
        <span class="rag-pill">FAISS</span>
        <span class="rag-pill">OCR</span>
        <span class="rag-pill">Citations</span>
      </div>
      <p style="margin-top: 0.95rem;"><b>Built by Hassan Khan</b></p>
      <p class="rag-muted">Upload a PDF, wait for ingestion, then query with citations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

backend_ok = backend_health()

with st.sidebar:
    st.subheader("Connection")
    st.caption(f"API Base URL: {API_BASE_URL}")
    if backend_ok:
        st.success("Backend connected")
    else:
        st.error("Backend not reachable")
        st.info(
            "Start the API and reload:\n\n"
            "`uvicorn construction_rag.api.main:app --host 0.0.0.0 --port 8000`"
        )

    st.markdown("---")
    st.subheader("Environment")
    st.caption("For full capability set env vars in `.env` (see `README.md`).")
    st.write(f"- `OPENAI_API_KEY`: {'OK' if os.getenv('OPENAI_API_KEY') else 'missing'}")
    st.write(f"- `ANTHROPIC_API_KEY`: {'OK' if os.getenv('ANTHROPIC_API_KEY') else 'missing'}")
    st.write(f"- `LLM_PROVIDER`: `{os.getenv('LLM_PROVIDER', 'anthropic')}`")
    st.write(f"- `LLM_MODEL`: `{os.getenv('LLM_MODEL', '')}`")


tab_upload, tab_chat = st.tabs(["Upload & Process", "Chat"])

with tab_upload:
    st.subheader("Upload PDF")
    st.markdown(
        '<div class="rag-card">Use a real construction/architectural PDF for best results.</div>',
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("PDF document", type=["pdf"])

    can_upload = backend_ok and uploaded is not None
    if st.button("Upload & Process", type="primary", disabled=not can_upload):
        if not backend_ok:
            st.warning("Backend is not connected. Start the API and try again.")
            st.stop()

        with st.spinner("Uploading..."):
            try:
                data = api_post(
                    "/documents",
                    files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
                )
            except requests.HTTPError as exc:
                body = getattr(exc.response, "text", "") if hasattr(exc, "response") else ""
                st.error("Upload failed.")
                st.code(body or str(exc))
                st.info("Fix configuration in `.env` and check `README.md`, then restart the backend.")
                st.stop()

        doc_id = data["id"]
        st.success(f"Uploaded: {uploaded.name}")
        st.caption(f"Document ID: `{doc_id}`")

        progress = st.progress(0)
        status_box = st.empty()
        while True:
            status = poll_status(doc_id)
            progress.progress(int(status["progress"]))
            status_box.info(f"{status['status']}: {status.get('message') or ''}")
            if status["status"] in {"completed", "failed"}:
                break
            time.sleep(2)

        if status["status"] == "failed":
            st.error("Processing failed.")
            st.info("Set the required env vars in `.env`, restart the backend, and re-upload.")


with tab_chat:
    st.subheader("Ask a question")

    if not backend_ok:
        st.info("Backend is not connected. Start the API to list documents and query.")
        st.stop()

    docs = list_documents()
    options = {f"{d['filename']} ({d['status']}) - {d['id']}": d for d in docs}
    selected_key = st.selectbox("Document", [""] + list(options.keys()))

    if not selected_key:
        st.info("Select a processed document to start chatting.")
        st.stop()

    doc = options[selected_key]
    if doc["status"] != "completed":
        st.warning("Document is not processed yet.")
        st.stop()

    q = st.text_input("Question", placeholder="e.g., What is the slab thickness and where is it specified?")
    if st.button("Ask", type="primary", disabled=not q.strip()):
        with st.spinner("Retrieving & generating answer..."):
            try:
                resp = api_post(f"/documents/{doc['id']}/query", json={"question": q})
            except requests.HTTPError as exc:
                body = getattr(exc.response, "text", "") if hasattr(exc, "response") else ""
                st.error("Query failed.")
                st.code(body or str(exc))
                st.info("Set required API keys in `.env`, restart backend, and retry. See `README.md`.")
                st.stop()

        st.markdown(resp.get("answer", "") or "")
        with st.expander("Citations"):
            for c in resp.get("citations", []):
                st.markdown(f"- p.{c['page_number']} (`{c['chunk_id']}`): {c['excerpt']}")

    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("Clear chat history"):
            api_delete(f"/documents/{doc['id']}/chat/history")
            st.success("Cleared.")
