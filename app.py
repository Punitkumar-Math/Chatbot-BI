import streamlit as st
import requests

from workflow_engine import recommend_workflow

st.set_page_config(page_title="Bioinformatics AI Assistant", layout="wide")

st.title("🧬 Bioinformatics Workflow Chatbot")

st.write("Generate workflows, code, and ask bioinformatics questions.")

# ---------------------------
# CHAT MEMORY
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------
# LLM FUNCTION (OLLAMA)
# ---------------------------

def ask_llm(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    if "response" in data:
        return data["response"]
    else:
        return str(data)

# ---------------------------
# STUDY DESIGN WIZARD
# ---------------------------

st.subheader("Study Design")

if "study_step" not in st.session_state:
    st.session_state.study_step = 0


# Step 1 – Study Type
if st.session_state.study_step == 0:

    study_type = st.selectbox(
        "Select study type",
        ["Bulk RNA-seq", "Single-cell RNA-seq", "Spatial transcriptomics", "ATAC-seq"]
    )

    if st.button("Next"):

        st.session_state.study_type = study_type
        st.session_state.study_step = 1


# Step 2 – Sample number per condition
elif st.session_state.study_step == 1:

    st.write("Specify sample numbers per condition")

    condition1 = st.text_input("Condition 1 name", "Control")
    n1 = st.number_input("Samples in Condition 1", min_value=1, value=3)

    condition2 = st.text_input("Condition 2 name", "Treatment")
    n2 = st.number_input("Samples in Condition 2", min_value=1, value=3)

    total_samples = n1 + n2

    st.info(f"Total samples: {total_samples}")

    if st.button("Next"):

        st.session_state.condition1 = condition1
        st.session_state.condition2 = condition2
        st.session_state.n1 = n1
        st.session_state.n2 = n2
        st.session_state.samples = total_samples

        st.session_state.study_step = 2


# Step 3 – Experimental design
elif st.session_state.study_step == 2:

    design = st.selectbox(
        "Experimental design",
        ["Case vs Control", "Time series", "Multiple conditions"]
    )

    if st.button("Generate Workflow"):

        st.session_state.design = design
        st.session_state.study_step = 3


# Step 4 – Workflow suggestion
elif st.session_state.study_step == 3:

    st.success("Study design captured")

    st.write("Study type:", st.session_state.study_type)
    st.write("Samples:", st.session_state.samples)
    st.write("Design:", st.session_state.design)

    prompt = f"""
    You are a bioinformatics expert.

    Study design:

    Study type: {st.session_state.study_type}
    Number of samples: {st.session_state.samples}
    Experimental design: {st.session_state.design}

    Provide:

    1. Recommended workflow
    2. Tools to use
    3. Example pipeline
    """

    result = ask_llm(prompt)

    st.markdown("### Recommended Pipeline")

    st.write(result)

# ---------------------------
# WORKFLOW GENERATOR SECTION
# ---------------------------

st.subheader("Generate Analysis Workflow")

data_type = st.selectbox(
    "What type of data?",
    ["Single-cell RNA-seq", "Bulk RNA-seq", "Spatial transcriptomics"]
)

platform = st.selectbox(
    "Platform",
    ["10x Genomics", "SmartSeq", "Visium", "Other"]
)

goal = st.selectbox(
    "Analysis Goal",
    ["Cell type annotation", "Differential expression", "Trajectory analysis"]
)

language = st.selectbox(
    "Preferred Language",
    ["R", "Python"]
)

if st.button("Generate Workflow & Code"):

    prompt = f"""
    You are a bioinformatics expert.

    Create a bioinformatics analysis pipeline.

    Data type: {data_type}
    Platform: {platform}
    Goal: {goal}
    Programming language: {language}

    First give a step-by-step workflow.

    Then provide full runnable code.
    """

    with st.spinner("Generating workflow..."):

        result = ask_llm(prompt)

        st.session_state.messages.append(
            {"role": "assistant", "content": result}
        )

        st.markdown("### Generated Workflow & Code")
        st.write(result)


# ---------------------------
# CHAT SECTION
# ---------------------------

st.subheader("Ask Questions / Debug Errors")

# Show previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
user_input = st.chat_input("Ask about workflow, code, or errors...")


if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ---------------------------
    # WORKFLOW RECOMMENDER
    # ---------------------------

    workflow = recommend_workflow(user_input)

    if workflow:

        with st.chat_message("assistant"):

            st.markdown("### Recommended Workflow")

            for step, tool in workflow["workflow"]:
                st.write(f"{step} – {tool}")

        st.session_state.messages.append(
            {"role": "assistant", "content": str(workflow["workflow"])}
        )

    else:

        # ---------------------------
        # FALLBACK TO LLM
        # ---------------------------

        context = ""

        for msg in st.session_state.messages:
            context += f"{msg['role']}: {msg['content']}\n"

        prompt = f"""
        You are a bioinformatics assistant.

        Conversation history:
        {context}

        Answer the latest user question clearly.
        Provide explanations and code if necessary.
        """

        with st.spinner("Thinking..."):

            response = ask_llm(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )