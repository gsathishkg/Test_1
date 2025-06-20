import streamlit as st
from graphviz import Digraph
from pptx import Presentation
from pptx.util import Inches
import json
import os

st.set_page_config(page_title="Flowchart Designer", layout="wide")

if "steps" not in st.session_state:
    st.session_state.steps = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.title("🎨 Flowchart Designer")

def generate_flowchart(steps):
    dot = Digraph(format="png")
    dot.attr(rankdir='TB', splines='ortho', nodesep='1', ranksep='1')
    step_map = {s["id"]: s for s in steps}
    added = set()

    def add_node(nid):
        if nid in added: return
        step = step_map.get(nid, {"label": nid, "type": "process"})
        shape = {
            "start": "circle",
            "end": "doublecircle",
            "decision": "diamond",
            "process": "box"
        }.get(step["type"], "box")
        style = 'filled'
        fillcolor = 'lightgrey'
        if step["type"] == "start":
            fillcolor = '#cce5ff'
        elif step["type"] == "end":
            fillcolor = '#d4edda'
        elif step["type"] == "decision":
            fillcolor = '#fff3cd'
        dot.node(nid, step["label"], shape=shape, style=style, fillcolor=fillcolor)
        added.add(nid)

    for step in steps:
        add_node(step["id"])
        for nxt in step.get("next", []):
            add_node(nxt["id"])
            color = 'black'
            if nxt.get("label", "").lower() == "yes":
                color = 'green'
            elif nxt.get("label", "").lower() == "no":
                color = 'red'
            dot.edge(step["id"], nxt["id"], label=nxt.get("label", ""), color=color)
    return dot

# Input Form
with st.form("step_form", clear_on_submit=True):
    if st.session_state.edit_index is None:
        st.subheader("➕ Add New Step")
        default = {"id": "", "label": "", "type": "process", "next": []}
    else:
        st.subheader("✏️ Edit Step")
        default = st.session_state.steps[st.session_state.edit_index]

    step_id = st.text_input("Step ID", value=default["id"])
    label = st.text_input("Label", value=default["label"])
    step_type = st.selectbox("Step Type", ["start", "process", "decision", "end"], index=["start", "process", "decision", "end"].index(default["type"]))
    next_steps = []
    for i in range(2):
        col1, col2 = st.columns(2)
        with col1:
            nid = st.text_input(f"Next Step ID {i+1}", value=default["next"][i]["id"] if i < len(default["next"]) else "")
        with col2:
            lbl = st.text_input(f"Label (e.g., Yes/No) {i+1}", value=default["next"][i].get("label", "") if i < len(default["next"]) else "")
        if nid:
            next_steps.append({"id": nid, "label": lbl})

    submitted = st.form_submit_button("✅ Save Step")
    if submitted:
        new_step = {"id": step_id, "label": label, "type": step_type, "next": next_steps}
        if st.session_state.edit_index is None:
            st.session_state.steps.append(new_step)
        else:
            st.session_state.steps[st.session_state.edit_index] = new_step
            st.session_state.edit_index = None
        st.success("Step saved!")

# Edit/Delete UI
st.subheader("🧾 Flow Steps")
for idx, step in enumerate(st.session_state.steps):
    cols = st.columns([4, 1, 1])
    with cols[0]:
        st.code(json.dumps(step, indent=2))
    with cols[1]:
        if st.button("✏️ Edit", key=f"edit_{idx}"):
            st.session_state.edit_index = idx
    with cols[2]:
        if st.button("🗑 Delete", key=f"delete_{idx}"):
            del st.session_state.steps[idx]
            if st.session_state.edit_index == idx:
                st.session_state.edit_index = None
            st.experimental_rerun()

# Preview
st.subheader("🖼 Flowchart Preview")
flow = generate_flowchart(st.session_state.steps)
st.graphviz_chart(flow)

# Export
col1, col2, col3 = st.columns(3)

with col1:
    st.download_button("⬇️ Download PNG", data=flow.pipe(format="png"),
                       file_name="flowchart.png", mime="image/png")

with col2:
    if st.button("📊 Export to PPTX"):
        flow.render(filename="temp_flow", format="png", cleanup=True)
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.add_picture("temp_flow.png", Inches(1), Inches(1), height=Inches(5.5))
        prs.save("flowchart_output.pptx")
        with open("flowchart_output.pptx", "rb") as f:
            st.download_button("📥 Download PPTX", data=f, file_name="flowchart.pptx")

with col3:
    with st.expander("💾 Save / Load"):
        if st.download_button("📥 Download JSON", json.dumps(st.session_state.steps, indent=2), file_name="flow.json"):
            st.success("Saved JSON")
        uploaded = st.file_uploader("Upload flow JSON", type=["json"])
        if uploaded:
            st.session_state.steps = json.load(uploaded)
            st.experimental_rerun()
