"""Build an Excel workbook from Azure DevOps work item data."""

import io
from typing import Any

import pandas as pd


def _identity(val: Any) -> str:
    """Flatten an ADO identity object to a display name string."""
    if isinstance(val, dict):
        return val.get("displayName") or val.get("uniqueName") or str(val)
    return val or ""


def _text(val: Any) -> str:
    """Return val as a plain string (works for HTML fields too)."""
    return str(val) if val is not None else ""


_KNOWN_FIELDS = {
    "System.AreaPath",
    "System.TeamProject",
    "System.IterationPath",
    "System.WorkItemType",
    "System.State",
    "System.Reason",
    "System.AssignedTo",
    "System.CreatedDate",
    "System.CreatedBy",
    "System.ChangedDate",
    "System.ChangedBy",
    "System.CommentCount",
    "System.Title",
    "System.BoardColumn",
    "System.BoardColumnDone",
    "Microsoft.VSTS.Common.Priority",
    "Microsoft.VSTS.Common.Severity",
    "Microsoft.VSTS.Common.ValueArea",
    "Microsoft.VSTS.Common.BusinessValue",
    "Microsoft.VSTS.Common.BacklogPriority",
    "Microsoft.VSTS.Common.StackRank",
    "System.Description",
    "Microsoft.VSTS.Common.AcceptanceCriteria",
    "Microsoft.VSTS.TCM.ReproSteps",
    "Microsoft.VSTS.Common.ActivatedDate",
    "Microsoft.VSTS.Common.ActivatedBy",
    "Microsoft.VSTS.Common.ResolvedDate",
    "Microsoft.VSTS.Common.ResolvedBy",
    "Microsoft.VSTS.Common.ClosedDate",
    "Microsoft.VSTS.Common.ClosedBy",
    "System.Tags",
}


def _flatten_relations(relations: list[dict]) -> str:
    if not relations:
        return ""
    parts = []
    for rel in relations:
        rel_type = rel.get("rel", "")
        rel_url = rel.get("url", "")
        name = (rel.get("attributes") or {}).get("name", "")
        parts.append(f"{rel_type} | {name} | {rel_url}")
    return "\n".join(parts)


def _pick_fields(fields: dict) -> dict:
    return {
        "Area Path": fields.get("System.AreaPath"),
        "Team Project": fields.get("System.TeamProject"),
        "Iteration Path": fields.get("System.IterationPath"),
        "Work Item Type": fields.get("System.WorkItemType"),
        "State": fields.get("System.State"),
        "Reason": fields.get("System.Reason"),
        "Assigned To": _identity(fields.get("System.AssignedTo")),
        "Created Date": fields.get("System.CreatedDate"),
        "Created By": _identity(fields.get("System.CreatedBy")),
        "Changed Date": fields.get("System.ChangedDate"),
        "Changed By": _identity(fields.get("System.ChangedBy")),
        "Comment Count": fields.get("System.CommentCount"),
        "Title": fields.get("System.Title"),
        "Board Column": fields.get("System.BoardColumn"),
        "Board Column Done": fields.get("System.BoardColumnDone"),
        "Priority": fields.get("Microsoft.VSTS.Common.Priority"),
        "Severity": fields.get("Microsoft.VSTS.Common.Severity"),
        "Value Area": fields.get("Microsoft.VSTS.Common.ValueArea"),
        "Business Value": fields.get("Microsoft.VSTS.Common.BusinessValue"),
        "Backlog Priority": fields.get("Microsoft.VSTS.Common.BacklogPriority"),
        "Stack Rank": fields.get("Microsoft.VSTS.Common.StackRank"),
        "Description": _text(fields.get("System.Description")),
        "Acceptance Criteria": _text(
            fields.get("Microsoft.VSTS.Common.AcceptanceCriteria")
        ),
        "Repro Steps": _text(fields.get("Microsoft.VSTS.TCM.ReproSteps")),
        "Activated Date": fields.get("Microsoft.VSTS.Common.ActivatedDate"),
        "Activated By": _identity(fields.get("Microsoft.VSTS.Common.ActivatedBy")),
        "Resolved Date": fields.get("Microsoft.VSTS.Common.ResolvedDate"),
        "Resolved By": _identity(fields.get("Microsoft.VSTS.Common.ResolvedBy")),
        "Closed Date": fields.get("Microsoft.VSTS.Common.ClosedDate"),
        "Closed By": _identity(fields.get("Microsoft.VSTS.Common.ClosedBy")),
        "Tags": fields.get("System.Tags"),
    }


def build_excel(
    work_items: list[dict],
    comments_map: dict[int, list[dict]],
    revisions_map: dict[int, list[dict]],
) -> bytes:
    """Assemble the four-sheet workbook and return raw bytes."""
    wi_rows: list[dict] = []
    comment_rows: list[dict] = []
    revision_rows: list[dict] = []
    custom_rows: list[dict] = []

    for wi in work_items:
        wid = wi.get("id")
        if wid is None:
            continue
        fields: dict = wi.get("fields", {})
        relations: list = wi.get("relations", [])

        wi_rows.append(
            {
                "ID": wid,
                "Rev": wi.get("rev"),
                "URL": wi.get("url"),
                **_pick_fields(fields),
                "Relations": _flatten_relations(relations),
            }
        )

        for field_name, field_value in fields.items():
            if field_name not in _KNOWN_FIELDS:
                custom_rows.append(
                    {
                        "Work Item ID": wid,
                        "Field Name": field_name,
                        "Field Value": _text(field_value),
                    }
                )

        for c in comments_map.get(wid, []):
            comment_rows.append(
                {
                    "Work Item ID": wid,
                    "Comment ID": c.get("id"),
                    "Created Date": c.get("createdDate"),
                    "Created By": _identity(c.get("createdBy")),
                    "Modified Date": c.get("modifiedDate"),
                    "Modified By": _identity(c.get("modifiedBy")),
                    "Text": _text(c.get("text")),
                }
            )

        for r in revisions_map.get(wid, []):
            r_fields = r.get("fields", {})
            revision_rows.append(
                {
                    "Work Item ID": wid,
                    "Revision": r.get("rev"),
                    "Changed Date": r_fields.get("System.ChangedDate"),
                    "Changed By": _identity(r_fields.get("System.ChangedBy")),
                    "State": r_fields.get("System.State"),
                    "Reason": r_fields.get("System.Reason"),
                    "Title": r_fields.get("System.Title"),
                    "Assigned To": _identity(r_fields.get("System.AssignedTo")),
                }
            )

    df_wi = pd.DataFrame(wi_rows)
    df_comments = pd.DataFrame(comment_rows)
    df_revisions = pd.DataFrame(revision_rows)
    df_custom = pd.DataFrame(custom_rows)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_wi.to_excel(writer, sheet_name="WorkItems", index=False)
        df_comments.to_excel(writer, sheet_name="Comments", index=False)
        df_revisions.to_excel(writer, sheet_name="Revisions", index=False)
        df_custom.to_excel(writer, sheet_name="CustomFields", index=False)
    buf.seek(0)
    return buf.read()
