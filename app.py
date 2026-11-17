import streamlit as st
import json
import os
from datetime import date
from fpdf import FPDF

st.set_page_config(page_title="Network Infrastructure Manager", layout="centered")

DATA_FILE = "ethernet_drops_data.json"

ROOMS = (
    [f"Classroom {i}" for i in range(1, 15)]
    + [
        "Teachers' Lounge",
        "Secretariat Office",
        "Fernanda / Roberval Office",
        "Talita / Julio Office",
        "Rogério / Ana Office",
        "Principal's Office",
        "PROATI Room",
        "Resource Room",
        "Appendice Room",
    ]
)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for room in ROOMS:
                        if room not in data:
                            data[room] = 0
                    return data
        except (json.JSONDecodeError, ValueError):
            pass
    default_data = {room: 0 for room in ROOMS}
    save_data(default_data)
    return default_data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def create_pdf_bytes(drops_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    report_date = date.today().strftime("%B %d, %Y")
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 12, f"Network Infrastructure Report - {report_date}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(230, 236, 245)
    pdf.cell(140, 10, "  Location", border=1, fill=True)
    pdf.cell(50, 10, "Ethernet Drops  ", border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    total_drops = 0
    for room in ROOMS:
        count = drops_dict.get(room, 0)
        total_drops += count
        safe_room_name = room.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(140, 8, f"  {safe_room_name}", border=1)
        pdf.cell(50, 8, f"{count}  ", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(215, 225, 240)
    pdf.cell(140, 10, "  TOTAL ETHERNET DROPS", border=1, fill=True)
    pdf.cell(50, 10, f"{total_drops}  ", border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())

if "drops" not in st.session_state:
    st.session_state.drops = load_data()
else:
    for room in ROOMS:
        if room not in st.session_state.drops:
            st.session_state.drops[room] = 0

if "selected" not in st.session_state:
    st.session_state.selected = "Classroom 1"

st.title("Network Infrastructure Manager")
st.caption("Select a location below, then add or remove Ethernet Drops.")

cols = st.columns(3)
for idx, room in enumerate(ROOMS):
    count = st.session_state.drops.get(room, 0)
    is_selected = (st.session_state.selected == room)
    label = f"🔵 {room} ({count})" if is_selected else f"{room} ({count})"
    
    if cols[idx % 3].button(label, key=f"btn_{room}", use_container_width=True):
        st.session_state.selected = room
        st.rerun()

st.divider()

active_room = st.session_state.selected
current_count = st.session_state.drops.get(active_room, 0)

st.subheader(f"Selected: {active_room} ({current_count} Ethernet Drops)")

col_add, col_rem = st.columns(2)

if col_add.button("+ Add Ethernet Drop", type="primary", use_container_width=True):
    st.session_state.drops[active_room] += 1
    save_data(st.session_state.drops)
    st.rerun()

if col_rem.button("- Remove Ethernet Drop", disabled=(current_count == 0), use_container_width=True):
    st.session_state.drops[active_room] -= 1
    save_data(st.session_state.drops)
    st.rerun()

if current_count > 0:
    drop_cols = st.columns(3)
    for n in range(1, current_count + 1):
        drop_cols[(n - 1) % 3].info(f"Ethernet Drop #{n:02d}")
else:
    st.write(f"*No Ethernet Drops registered in {active_room} yet.*")

st.divider()

with st.expander("View & Export PDF Report"):
    st.markdown(f"### Network Infrastructure Report — {date.today().strftime('%B %d, %Y')}")
    total = sum(st.session_state.drops.values())
    
    report_rows = [{"Location": r, "Ethernet Drops": st.session_state.drops.get(r, 0)} for r in ROOMS]
    report_rows.append({"Location": "TOTAL ETHERNET DROPS", "Ethernet Drops": total})
    
    st.table(report_rows)

    pdf_bytes = create_pdf_bytes(st.session_state.drops)
    st.download_button(
        label="Download",
        data=pdf_bytes,
        file_name=f"network_infrastructure_report_{date.today().isoformat()}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )
