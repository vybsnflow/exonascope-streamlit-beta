import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

st.set_page_config(page_title="ExonaScope Fact Pattern Generator", layout="wide")
st.title("📄 ExonaScope – Fact Pattern Generator (Beta)")

st.markdown("""
Welcome to the **ExonaScope beta testing tool**. This app lets you upload a legal document (e.g., affidavit or police report),
extract text page-by-page, and summarize it into a court-style fact pattern using GPT.

### 🔐 Beta Access Required
Password: `ExonaBeta2024!`

### How to Use:
1. Upload a single PDF.
2. Click "Generate Fact Pattern"
3. Copy the result into the Motion Generator app
""")

if st.text_input("🔐 Enter Beta Access Password", type="password") != "ExonaBeta2024!":
    st.warning("This app is currently restricted to beta testers. Please enter the correct password.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

uploaded_file = st.file_uploader("📎 Upload a single PDF document", type="pdf")

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    all_text = []

    st.subheader("📖 Extracted Text Preview")
    for page_num, page in enumerate(doc):
        page_text = page.get_text().strip()
        if page_text:
            label = f"[{uploaded_file.name}, p. {page_num + 1}]"
            labeled = f"{label}\n{page_text}"
            all_text.append(labeled)
            with st.expander(f"{label}", expanded=False):
                st.text(page_text)

    combined_text = "\n\n".join(all_text)

    st.subheader("✏️ Generate Fact Pattern with GPT")
    if st.button("🔍 Generate Fact Pattern Now"):
        with st.spinner("Generating fact pattern..."):
            prompt = f"""You are a legal assistant. Using only the facts below, create a neutral, paragraph-style Statement of Facts. Cite each fact using the source label in parentheses. Do not invent or infer facts.

{combined_text}
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You generate legally neutral fact patterns."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                generated_facts = response.choices[0].message.content.strip()
                st.session_state["generated_facts"] = generated_facts
                st.success("✅ Fact pattern generated successfully.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if "generated_facts" in st.session_state:
        st.subheader("📄 Fact Pattern Output")
        st.text_area("You can copy this into the Motion Generator", value=st.session_state["generated_facts"], height=300)
        st.download_button("💾 Download Fact Pattern (.txt)",
                           st.session_state["generated_facts"].encode(),
                           file_name="fact_pattern.txt")
