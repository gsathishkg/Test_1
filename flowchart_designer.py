import streamlit as st
import json

st.set_page_config(page_title="Mermaid Flowchart Designer", layout="wide")
st.title("🌊 Mermaid Flowchart Designer (No Graphviz Required)")

if "steps" not in st.session_state:
    st.session_state.steps = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

def generate_mermaid(steps):
    lines = ["graph TD"]
    for step in steps:
        sid = step["id"]
        s_label = step["label"]
        s_type = step["type"]
        shape = {
            "start": f'{sid}(({s_label}))',
            "end": f'{sid}(({s_label}))',
            "decision": f'{sid}{{{s_label}}}',
            "process": f'{sid}[{s_label}]'
        }.get(s_type, f'{sid}[{s_label}]')
        lines.append(shape)
        for nxt in step.get("next", []):
            tid = nxt["id"]
            label = nxt.get("label", "")
            lines.append(f'{sid} --|{label}| {tid}')
    return "\n".join(lines)

# Input form
with st.form("step_form", clear_on_submit=True):
    if st.session_state.edit_index is None:
        st.subheader("➕ Add New Step")
        default = {"id": "", "label": "", "type": "process", "next": []}
    else:
        st.subheader("✏️ Edit Step")
        default = st.session_state.steps[st.session_state.edit_index]

    step_id = st.text_input("Step ID", value=default["id"])
    label = st.text_input("Label", value=default["label"])
    step_type = st.selectbox("Step Type", ["start", "process", "decision", "end"],
                             index=["start", "process", "decision", "end"].index(default["type"]))
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

# Edit/Delete
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
st.subheader("🖼 Flowchart Preview (Mermaid.js)")
if st.session_state.steps:
    mermaid = generate_mermaid(st.session_state.steps)
    st.markdown(f"```mermaid\n{mermaid}\n```")

else:
    st.info("Add steps to generate the flowchart.")

# Inject Mermaid.js script
st.components.v1.html("""
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
""", height=0)
