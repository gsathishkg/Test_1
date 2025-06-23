import streamlit as st
import json

st.set_page_config(page_title="Mermaid Flowchart Designer", layout="wide")

if "steps" not in st.session_state:
    st.session_state.steps = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.title("🌊 Mermaid Flowchart Designer")

# Mermaid generator with styling
def generate_mermaid_source(steps):
    lines = ["graph TD"]
    styles = []
    defined_ids = set()

    for step in steps:
        defined_ids.add(step["id"])
        if step["type"] == "start":
            lines.append(f'{step["id"]}(["{step["label"]}"])')
            styles.append(f'class {step["id"]} start;')
        elif step["type"] == "end":
            lines.append(f'{step["id"]}(["{step["label"]}"])')
            styles.append(f'class {step["id"]} end;')
        elif step["type"] == "decision":
            lines.append(f'{step["id"]}{{"{step["label"]}"}}')
            styles.append(f'class {step["id"]} decision;')
        else:
            lines.append(f'{step["id"]}["{step["label"]}"]')
            styles.append(f'class {step["id"]} process;')

        for nxt in step.get("next", []):
            label = f'|{nxt["label"]}|' if nxt.get("label") else ""
            lines.append(f'{step["id"]} {label} --> {nxt["id"]}')

    # Style block
    lines.append("classDef start fill:#c6f6d5,stroke:#2f855a,stroke-width:2px;")
    lines.append("classDef process fill:#bee3f8,stroke:#3182ce,stroke-width:2px;")
    lines.append("classDef decision fill:#fbd38d,stroke:#dd6b20,stroke-width:2px;")
    lines.append("classDef end fill:#feb2b2,stroke:#c53030,stroke-width:2px;")
    lines.extend(styles)

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
            lbl = st.text_input(
                f"Edge Label {i+1} (Yes/No/Continue)",
                value=default["next"][i].get("label", "") if i < len(default["next"]) else "",
                placeholder="Yes / No / Continue"
            )
        with col2:
            nid = st.text_input(
                f"Next Step ID {i+1}",
                value=default["next"][i]["id"] if i < len(default["next"]) else "",
                placeholder="S002"
            )
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

# Display steps with edit/delete
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

# Mermaid Diagram Preview
st.subheader("🖼 Flowchart Preview (Mermaid.js)")
mermaid_code = generate_mermaid_source(st.session_state.steps)
st.markdown(f"```mermaid\n{mermaid_code}\n```", unsafe_allow_html=True)

# Show Mermaid source
with st.expander("🔍 Mermaid Source"):
    st.code(mermaid_code, language="mermaid")

# Check for missing step links
defined_ids = {s["id"] for s in st.session_state.steps}
for step in st.session_state.steps:
    for nxt in step.get("next", []):
        if nxt["id"] not in defined_ids:
            st.warning(f"⚠️ Step `{step['id']}` points to undefined step ID `{nxt['id']}`")

# Import/Export
with st.expander("💾 Save / Load Flow"):
    st.download_button("📥 Download JSON", json.dumps(st.session_state.steps, indent=2), file_name="flow.json")
    uploaded = st.file_uploader("Upload flow JSON", type=["json"])
    if uploaded:
        st.session_state.steps = json.load(uploaded)
        st.experimental_rerun()
