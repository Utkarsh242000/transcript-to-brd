"""Streamlit web app – Azure DevOps Query → Excel Exporter."""

import time
from datetime import datetime

import streamlit as st

from ado_export.client import AzureDevOpsClient, parse_query_url
from ado_export.excel_builder import build_excel

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Azure DevOps → Excel Exporter",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Azure DevOps Query → Excel Exporter")
st.markdown(
    "Paste a saved Azure DevOps query URL and your Personal Access Token (PAT) "
    "to export all matching work items – including comments, revisions, and custom "
    "fields – into a downloadable Excel workbook."
)

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
with st.form("export_form"):
    query_url = st.text_input(
        "Azure DevOps Query URL",
        placeholder=(
            "https://dev.azure.com/{org}/{project}/_queries/query/{query_id}/"
        ),
        help=(
            "Open the saved query in your browser and copy the full URL from the "
            "address bar. The URL must contain the query GUID."
        ),
    )

    pat = st.text_input(
        "Personal Access Token (PAT)",
        type="password",
        help=(
            "Your Azure DevOps PAT with at least **Work Items (Read)** scope. "
            "The token is used only during this session and is never stored."
        ),
    )

    submitted = st.form_submit_button("🚀 Fetch & Export", use_container_width=True)

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
if submitted:
    # --- Basic validation ---
    if not query_url.strip():
        st.error("Please enter an Azure DevOps query URL.")
        st.stop()
    if not pat.strip():
        st.error("Please enter your Personal Access Token (PAT).")
        st.stop()

    try:
        org, project, query_id = parse_query_url(query_url.strip())
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.info(
        f"**Organisation:** {org}  \n**Project:** {project}  \n**Query ID:** {query_id}"
    )

    client = AzureDevOpsClient(org, project, pat.strip())

    # --- Step 1: run query ---
    with st.spinner("Running saved query…"):
        try:
            work_item_ids = client.run_query(query_id)
        except Exception as exc:
            st.error(f"Failed to run query: {exc}")
            st.stop()

    if not work_item_ids:
        st.warning("The query returned no work items.")
        st.stop()

    st.success(f"Found **{len(work_item_ids)}** work item(s).")

    # --- Step 2: fetch work item details ---
    with st.spinner(f"Fetching details for {len(work_item_ids)} work item(s)…"):
        try:
            work_items = client.get_work_items(work_item_ids)
        except Exception as exc:
            st.error(f"Failed to fetch work items: {exc}")
            st.stop()

    # --- Step 3: fetch comments & revisions per work item ---
    comments_map: dict[int, list[dict]] = {}
    revisions_map: dict[int, list[dict]] = {}

    progress_bar = st.progress(0, text="Fetching comments and revisions…")
    total = len(work_items)

    for idx, wi in enumerate(work_items):
        wid: int = wi["id"]
        progress_bar.progress(
            (idx + 1) / total,
            text=f"Comments & revisions for work item {wid} ({idx + 1}/{total})",
        )

        try:
            comments_map[wid] = client.get_comments(wid)
        except Exception as exc:
            st.warning(f"Could not fetch comments for #{wid}: {exc}")
            comments_map[wid] = []

        try:
            revisions_map[wid] = client.get_revisions(wid)
        except Exception as exc:
            st.warning(f"Could not fetch revisions for #{wid}: {exc}")
            revisions_map[wid] = []

        time.sleep(0.05)

    progress_bar.empty()

    # --- Step 4: build Excel ---
    with st.spinner("Building Excel workbook…"):
        try:
            excel_bytes = build_excel(work_items, comments_map, revisions_map)
        except Exception as exc:
            st.error(f"Failed to generate Excel workbook: {exc}")
            st.stop()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"azure_devops_export_{timestamp}.xlsx"

    st.success("✅ Export complete! Click the button below to download your workbook.")

    st.download_button(
        label="⬇️ Download Excel Workbook",
        data=excel_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.markdown(
        "**Workbook sheets:**\n"
        "- **WorkItems** – main fields for every work item\n"
        "- **Comments** – all comments per work item\n"
        "- **Revisions** – full revision history per work item\n"
        "- **CustomFields** – any non-standard fields found\n"
    )
