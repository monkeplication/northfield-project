import re
import sys
from collections import Counter
from pathlib import Path

from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Inches, Mm, Pt
from openpyxl import Workbook
from openpyxl.styles import Font

sys.path.insert(0, "src")
from fleet_findings import (
    DATA,
    clean_events,
    energy_summary,
    fault_summary,
    load_events,
    part_summary,
    state_summary,
    usage_summary,
)

NAME = "Vaibhav Singh"
OUT = Path("submission")


def add_text(paragraph, text):
    for part in re.split(r"(\*\*.+?\*\*|`.+?`)", text):
        if part.startswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`"):
            paragraph.add_run(part[1:-1]).font.name = "Consolas"
        else:
            paragraph.add_run(part)


def add_code(doc, code):
    run = doc.add_paragraph().add_run(code)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)


def add_table(doc, lines):
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines if not line.startswith("| ---")]
    table = doc.add_table(rows=len(rows), cols=len(rows[0]), style="Table Grid")
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            add_text(table.cell(r, c).paragraphs[0], f"**{cell}**" if r == 0 else cell)


def add_markdown(doc, text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue
        if line.startswith("```"):
            end = lines.index("```", i + 1)
            add_code(doc, "\n".join(lines[i + 1 : end]))
            i = end
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            doc.add_heading(line.lstrip("# ").replace("`", ""), level=level)
        elif line.startswith("- "):
            add_text(doc.add_paragraph(style="List Bullet"), line[2:])
        elif re.match(r"\d+\. ", line):
            add_text(doc.add_paragraph(style="List Number"), line.split(". ", 1)[1])
        elif line.strip():
            add_text(doc.add_paragraph(), line)
        i += 1


def build_word():
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Inches(0.75)
    doc.styles["Normal"].font.size = Pt(10)
    doc.add_heading(f"{NAME}: Northfield SDE Case Assessment", level=0)
    doc.add_paragraph("Code, tests and README are in the accompanying repository.")
    for i, name in enumerate(["NOTES.md", "FINDINGS.md"]):
        if i:
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        add_markdown(doc, Path("docs", name).read_text())
    doc.save(OUT / f"{NAME}_Case Assessment.docx")


def style_sheet(sheet):
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for column in sheet.columns:
        width = max(len(str(c.value or "")) for c in column) + 2
        sheet.column_dimensions[column[0].column_letter].width = min(60, width)


def add_rows(book, title, header, rows):
    sheet = book.create_sheet(title)
    sheet.append(header)
    for row in rows:
        sheet.append(row)
    style_sheet(sheet)
    return sheet


def _as_cell(value):
    if isinstance(value, str) and value.lstrip("-").isdigit():
        return int(value)
    return value


def build_excel():
    rows = load_events(DATA)
    kept, removed = clean_events(rows)
    reasons = Counter(reason for reason, _ in removed)

    book = Workbook()
    book.remove(book.active)

    add_rows(
        book,
        "Cleaning log",
        ["Problem", "Action", "Rows"],
        [
            ["Exact duplicate (same event_id, same values)", "Kept first copy, dropped the rest", reasons["duplicate"]],
            ["Same event_id but different values", "Would keep first copy and flag", reasons["conflicting duplicate"]],
            ["Missing timestamp", "Dropped: cannot be placed in time order", reasons["missing timestamp"]],
            ["Timestamp outside 2026-11-02", "Dropped: belongs to another reporting day", reasons["outside reporting day"]],
            ["State not in the five known values", "Would drop", reasons["unknown state"]],
            ["Session end before start", "Would drop", reasons["session ends before it starts"]],
            ["Rows loaded", "", len(rows)],
            ["Rows kept", "", len(kept)],
        ],
    )

    add_rows(
        book,
        "Removed rows",
        ["Reason", "event_id", "tool_id", "timestamp"],
        [[reason, r["event_id"], r["tool_id"], r["timestamp"] or "(blank)"] for reason, r in removed],
    )

    faults = fault_summary(kept)
    fault_last = len(faults["codes"]) + 2
    fault_rows = []
    for idx, item in enumerate(faults["codes"], start=2):
        fault_rows.append([item["code"], item["count"], f"=B{idx}/B${fault_last}", "yes" if item["in_top_k"] else "no"])
    fault_rows.append(["Total", f"=SUM(B2:B{fault_last - 1})", f"=B{fault_last}/B${fault_last}", ""])
    fault_sheet = add_rows(book, "Fault codes", ["Fault code", "Count", "Share of faults", "In top 3"], fault_rows)
    for r in range(2, fault_last + 1):
        fault_sheet[f"C{r}"].number_format = "0%"

    usage = usage_summary(kept)
    usage_last = len(usage["by_tool"]) + 2
    usage_rows = []
    for idx, item in enumerate(usage["by_tool"], start=2):
        usage_rows.append(
            [item["tool_id"], item["sessions"], item["raw_minutes"], item["merged_minutes"], f"=C{idx}-D{idx}", f"=E{idx}/D{idx}"]
        )
    usage_rows.append(
        [
            "Total",
            f"=SUM(B2:B{usage_last - 1})",
            f"=SUM(C2:C{usage_last - 1})",
            f"=SUM(D2:D{usage_last - 1})",
            f"=C{usage_last}-D{usage_last}",
            f"=E{usage_last}/D{usage_last}",
        ]
    )
    usage_sheet = add_rows(
        book,
        "Usage minutes",
        ["Tool", "Sessions", "Raw minutes", "Merged minutes", "Double counted", "Overstated by"],
        usage_rows,
    )
    for r in range(2, usage_last + 1):
        usage_sheet[f"F{r}"].number_format = "0%"

    add_rows(
        book,
        "Latest state",
        ["Tool", "Latest state", "At", "Safety state", "Energy or fault events after", "Sessions running after", "State disagrees with activity"],
        [
            [
                item["tool_id"],
                item["state"],
                item["time"],
                "yes" if item["is_safety"] else "no",
                item["events_after"],
                item["sessions_after"],
                "yes" if item["state_mismatch"] else "no",
            ]
            for item in state_summary(kept)
        ],
    )

    parts = part_summary(kept)
    part_rows = [
        [item["part"], item["scans"], item["distinct_spellings"], ", ".join(item["spellings"])]
        for item in parts["families"]
    ]
    part_rows.append(["Total", parts["total_scans"], parts["distinct_labels"], f"{len(parts['families'])} families"])
    add_rows(book, "Part families", ["Part", "Scans", "Distinct spellings", "Spellings"], part_rows)

    add_rows(
        book,
        "Energy windows",
        ["Tool", "Slots", "Net energy", "Windows that net to zero"],
        [[item["tool_id"], item["slots"], item["net_energy"], item["zero_windows"]] for item in energy_summary(kept)],
    )

    header = list(rows[0])
    add_rows(book, "Clean events", header, [[_as_cell(v) for v in row.values()] for row in kept])
    add_rows(book, "Raw events", header, [[_as_cell(v) for v in row.values()] for row in rows])

    book.save(OUT / f"{NAME}_Case Analysis.xlsx")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build_word()
    build_excel()
    print(f"Wrote files to {OUT}/")
