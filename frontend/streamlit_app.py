from __future__ import annotations

import time

import requests
import streamlit as st


API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/v1")

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


st.title("Construction Document RAG")

tab_upload, tab_chat = st.tabs(["Upload & Process", "Chat"])

with tab_upload:
    st.subheader("Upload PDF")
    uploaded = st.file_uploader("PDF", type=["pdf"])
    if st.button("Upload", type="primary", disabled=uploaded is None):
        with st.spinner("Uploading..."):
            data = api_post(
                "/documents",
                files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
            )
        doc_id = data["id"]
        st.success(f"Uploaded: {doc_id}")
        progress = st.progress(0)
        status_box = st.empty()
        while True:
            status = poll_status(doc_id)
            progress.progress(int(status["progress"]))
            status_box.info(f"{status['status']}: {status.get('message') or ''}")
            if status["status"] in {"completed", "failed"}:
                break
            time.sleep(2)

with tab_chat:
    st.subheader("Ask a question")
    docs = list_documents()
    options = {f"{d['filename']} ({d['status']}) - {d['id']}": d for d in docs}
    selected_key = st.selectbox("Document", [""] + list(options.keys()))
    if not selected_key:
        st.info("Select a processed document to start chatting.")
    else:
        doc = options[selected_key]
        if doc["status"] != "completed":
            st.warning("Document is not processed yet.")
        else:
            q = st.text_input("Question")
            if st.button("Ask", type="primary", disabled=not q.strip()):
                with st.spinner("Retrieving & generating answer..."):
                    resp = api_post(f"/documents/{doc['id']}/query", json={"question": q})
                st.markdown(resp["answer"])
                with st.expander("Citations"):
                    for c in resp.get("citations", []):
                        st.markdown(f"- p.{c['page_number']} (`{c['chunk_id']}`): {c['excerpt']}")

            if st.button("Clear chat history"):
                api_delete(f"/documents/{doc['id']}/chat/history")
                st.success("Cleared.")

