import streamlit as st
import json
import os
from datetime import date

st.set_page_config(page_title="Network Infrastructure Manager", layout="centered")

DATA_FILE = "ethernet_drops_data.json"

ROOMS = (
    [f"Classroom {i}" for i in range(1, 15)]
    + [
        "Teachers' Lounge",
        "Front Office",
        "Fernanda / Roberval Office",
        "Talita / Julio Office",
        "Principal's Office",
        "PROATI Office",
        "Resources Classroom",
    ]
)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {room: 0 for room in ROOMS}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if "drops" not in st.session_state:
    st.session_state.drops = load_data()

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
    st.caption("Press Ctrl + P in your browser and select 'Save as PDF' to save this report.")
