import streamlit as st
import cohere
import os
import re
from dotenv import load_dotenv
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import fitz #Importing  PyMuPDF package traditionally it can be imported as fitz
load_dotenv()
cohere_api_key= os.getenv("COHERE_API_KEY")
# INITILIZING THE COHERE CLIENT 
cohere_client = cohere.ClientV2(api_key =os.getenv("COHERE_API_KEY"))
analysis_instructions = {

    "🧬 Extract Genes / Proteins": """
Analyze the supplied biological research paper specifically for genes and proteins.

Instructions:
- Identify genes and proteins explicitly mentioned in the supplied document.
- Clearly distinguish genes from proteins whenever the document provides enough information to do so.
- For each identified molecule, explain its biological role in the context of this paper.
- Explain why it is relevant to the experiment, mechanism, disease, pathway, or findings being discussed.
- Mention important relationships or interactions between identified genes/proteins when supported by the paper.
- Do not invent genes, proteins, functions, interactions, or experimental claims that are not supported by the supplied document.
- If the role of a molecule is unclear from the paper, explicitly state that rather than guessing.
- Organize the response clearly using headings, bullet points, or a table when appropriate.
""",

    "🧪 Explain Experimental Methodology": """
Analyze and explain the experimental methodology used in the supplied biological research paper.

Instructions:
- Identify the main research question or experimental objective.
- Explain the overall experimental design in logical chronological order.
- Identify important samples, organisms, cell lines, biological materials, reagents, or experimental groups when mentioned.
- Explain controls, comparison groups, and important experimental variables.
- Describe how samples or data were collected and analyzed.
- Explain why major methodological steps were performed when this can be determined from the paper.
- Distinguish experimental procedures from statistical or computational analyses.
- Translate highly technical methodology into understandable language while preserving scientific accuracy.
- Do not invent missing experimental details.
- Clearly state when important methodological information is not provided in the supplied text.
""",

    "🔬 Identify Laboratory Techniques": """
Identify and explain the laboratory and analytical techniques used in the supplied biological research paper.

Instructions:
- Identify laboratory techniques explicitly mentioned or clearly described in the paper.
- Examples may include PCR, qPCR, electrophoresis, chromatography, sequencing, microscopy, Western blotting, ELISA, cell culture, cloning, centrifugation, flow cytometry, spectroscopy, or other techniques.
- For each technique, explain what it does in general and how it was used specifically in this study.
- Explain what biological information or measurement the technique produced.
- Mention important instruments, assays, stains, markers, or reagents when relevant.
- Where possible, connect each technique to the experimental question it helped answer.
- Do not claim that a technique was used merely because it would normally be expected in that type of experiment.
- If the exact technique cannot be determined from the paper, state the uncertainty.
- Present the techniques in a clear structured format.
""",

    "📊 Explain Results": """
Analyze and explain the results reported in the supplied biological research paper.

Instructions:
- Identify the major experimental findings.
- Explain each important result in clear biological language.
- Distinguish observed results from the authors' interpretation of those results.
- Explain important increases, decreases, correlations, differences, trends, or other reported effects.
- Mention relevant experimental groups or controls when necessary to understand a result.
- Explain reported statistical significance when provided, without inventing statistical values.
- Connect important results to the research question or hypothesis.
- Explain what figures, tables, or measurements demonstrate when their information is available in the extracted text.
- Do not fabricate numerical values, statistical significance, figures, or conclusions.
- Clearly state when information required to interpret a result is unavailable.
- Finish with a concise summary of the paper's major findings.
""",

    "🧫 Explain Biological Mechanisms": """
Explain the biological mechanisms discussed or demonstrated in the supplied research paper.

Instructions:
- Identify the major biological processes, molecular pathways, cellular mechanisms, or physiological mechanisms discussed in the paper.
- Explain each mechanism step by step where possible.
- Identify important genes, proteins, enzymes, receptors, signaling molecules, cells, tissues, or pathways involved.
- Explain cause-and-effect relationships described by the authors.
- Connect molecular events to cellular or organism-level effects when supported by the document.
- Distinguish mechanisms demonstrated experimentally from mechanisms merely proposed or discussed by the authors.
- Simplify complicated pathways without removing scientifically important details.
- Do not introduce unsupported pathways, interactions, or mechanisms from general biological knowledge as though they were findings of this paper.
- Clearly indicate uncertainty or proposed mechanisms when appropriate.
""",

    "📖 Generate Revision Notes": """
Convert the supplied biological research paper into high-quality revision notes for a student.

Instructions:
- Identify the most important concepts and findings from the paper.
- Organize the notes into logical sections such as background, objective, methodology, techniques, major findings, mechanisms, and conclusions where applicable.
- Use concise bullet points instead of unnecessarily long paragraphs.
- Highlight important genes, proteins, pathways, biological terms, techniques, and experimental findings.
- Explain difficult concepts briefly where necessary.
- Include important experimental relationships and cause-and-effect connections.
- Prioritize information useful for understanding and remembering the paper.
- Do not add unsupported information merely to make the notes more complete.
- End with a short 'Key Takeaways' section containing the most important points to remember.
""",

    "❓ Generate Viva Questions": """
Generate viva/oral-examination questions based specifically on the supplied biological research paper.

Instructions:
- Generate questions that test genuine understanding rather than simple memorization.
- Include questions about the research objective, methodology, laboratory techniques, biological mechanisms, results, interpretation, and conclusions when applicable.
- Include a mixture of easy, intermediate, and advanced questions.
- Provide a concise scientifically accurate answer immediately after each question.
- Include some reasoning questions such as why a technique was used, why a control was necessary, or what a particular result implies.
- Base the questions on information contained in or directly supported by the supplied document.
- Do not create questions requiring information that the paper does not provide unless clearly marked as a broader conceptual question.
- Group questions by difficulty level.
""",

    "🧠 Explain Difficult Terminology": """
Identify and explain difficult biological, biochemical, medical, experimental, and statistical terminology appearing in the supplied research paper.

Instructions:
- Identify technical terms that may be difficult for a student to understand.
- Prioritize terms important for understanding the paper rather than ordinary scientific vocabulary.
- Give a clear and simple definition of each term.
- Then explain what the term means specifically in the context of this research paper.
- Expand abbreviations and acronyms where their meanings can be determined.
- Explain specialized experimental or statistical terminology when relevant.
- Preserve scientific accuracy while making explanations accessible.
- Avoid defining extremely basic words unless they have a specialized meaning in the paper.
- Do not invent definitions for ambiguous abbreviations; state when the meaning cannot be determined confidently.
- Present terminology in a clean glossary-style format.
""",

    "📝 Generate Flashcards": """
Generate study flashcards based specifically on the supplied biological research paper.

Instructions:
- Create question-and-answer flashcards covering the most important information in the paper.
- Cover important concepts, genes, proteins, biological mechanisms, experimental techniques, methodology, results, and conclusions where applicable.
- Keep each question focused on one concept.
- Keep answers concise enough for active recall while still scientifically accurate.
- Include both factual recall and conceptual understanding questions.
- Include some 'why' and 'how' questions when appropriate.
- Avoid repetitive or trivial flashcards.
- Do not introduce facts unsupported by the supplied paper.
- Organize the flashcards clearly as numbered Question/Answer pairs.
"""
}
output_formats = {

    "🧬 Extract Genes / Proteins": """
OUTPUT FORMAT:
- Do not use large multi-column tables.
- Organize the response using Markdown headings.

Use this structure:

## 🧬 Genes Identified
For each gene:
### [Gene name]
- **Type:** Gene
- **Role in the paper:** Explain its role.
- **Biological function:** Brief explanation.
- **Relevance to the study:** Explain why it matters.

## 🧪 Proteins Identified
For each protein:
### [Protein name]
- **Type:** Protein
- **Biological function:** Brief explanation.
- **Role in this study:** Explain its relevance.

## 🔗 Important Relationships
Explain important gene-protein or protein-protein relationships supported by the paper.

## 🎯 Key Takeaways
Provide a short summary of the most important genes and proteins.
""",

    "🧪 Explain Experimental Methodology": """
OUTPUT FORMAT:
- Do not use large multi-column tables.
- Explain the experiment in chronological order.

Use this structure:

## 🎯 Research Objective
Briefly explain what the researchers were trying to investigate.

## 🧪 Experimental Design
Explain the overall experimental setup.

## 🧬 Biological Materials
List relevant organisms, cells, tissues, samples, genes, proteins, or biological materials.

## 🔬 Experimental Procedure
Explain the methodology step-by-step using a numbered list.

## 🧫 Controls and Variables
Explain experimental groups, controls, and important variables when available.

## 📊 Data Analysis
Explain how experimental data were analyzed.

## 🎯 Methodology Summary
Briefly summarize the overall experimental strategy.
""",

    "🔬 Identify Laboratory Techniques": """
OUTPUT FORMAT:
- Do not use large multi-column tables.
- Give each important technique its own section.

Use this structure:

## 🔬 Laboratory Techniques Identified

For each technique:

### [Technique name]

**What it is:**  
Give a short scientific explanation.

**How it was used in this paper:**  
Explain its specific use.

**What it measured or revealed:**  
Explain what information the technique provided.

**Why it mattered:**  
Explain how it contributed to the research question.

---

Finish with:

## 🧪 Overall Experimental Toolkit
Briefly explain how the major techniques worked together in the study.
""",

    "📊 Explain Results": """
OUTPUT FORMAT:
- Avoid large multi-column tables.
- Separate individual major findings clearly.

Use this structure:

## 📊 Major Findings

For each important finding:

### Finding [number]: [Short descriptive title]

**What was observed:**  
Explain the reported result.

**Comparison / control:**  
Mention relevant experimental groups or controls if available.

**Biological meaning:**  
Explain what the result means biologically.

**Statistical evidence:**  
Mention statistical significance only when reported in the paper.

**Why it matters:**  
Connect the finding to the research question.

---

## 🎯 Overall Conclusion
Summarize what the combined results demonstrate.
""",

    "🧫 Explain Biological Mechanisms": """
OUTPUT FORMAT:
- Do NOT use tables.
- Give every major biological mechanism its own section.
- Prefer numbered steps for pathways and processes.

Use this structure:

## 🧫 [Mechanism name]

### What it is
Give a concise explanation of the biological mechanism.

### How it works
Explain the mechanism step-by-step:

1. First biological event.
2. Next molecular or cellular event.
3. Continue until the biological outcome is reached.

### Key Molecules / Genes / Cells
- Important molecule, gene, protein, cell, or pathway
- Explain its role briefly.

### Biological Outcome
Explain the final cellular, molecular, physiological, or experimental effect.

### Evidence in the Paper
State whether the mechanism was experimentally demonstrated, observed, proposed, discussed, or referenced by the authors.

---

Repeat this structure for each major mechanism.

## 🎯 Mechanism Summary
Briefly connect the major mechanisms discussed in the paper.
""",

    "📖 Generate Revision Notes": """
OUTPUT FORMAT:
Create clean student-friendly revision notes.

Use this structure:

# 📖 Revision Notes

## 🎯 Research Objective
Short explanation.

## 🧬 Important Biological Concepts
- Key concept → explanation
- Key concept → explanation

## 🔬 Methodology
Summarize the experimental approach using concise bullet points.

## 🧪 Important Techniques
List important laboratory or analytical techniques with brief explanations.

## 🧫 Biological Mechanisms
Summarize important mechanisms and pathways.

## 📊 Major Results
- Finding → meaning
- Finding → meaning

## 🧠 Important Terms
List particularly important terminology with short definitions.

## ⭐ Key Takeaways
Give the most important points a student should remember.

Prefer concise bullet points and clear headings rather than long paragraphs.
""",

    "❓ Generate Viva Questions": """
OUTPUT FORMAT:
Do not use tables.

Organize questions by difficulty.

# ❓ Viva Questions

## 🟢 Basic Questions

### Question 1
**Q:** [Question]

**Answer:**  
[Concise answer]

### Question 2
**Q:** [Question]

**Answer:**  
[Concise answer]

## 🟡 Intermediate Questions

Use the same Question/Answer format.

Include questions requiring explanation and reasoning.

## 🔴 Advanced Questions

Use the same Question/Answer format.

Include questions about experimental reasoning, interpretation, mechanisms, limitations, or implications where supported by the paper.

## 🎯 Challenge Question
Finish with one difficult conceptual question based on the paper and provide its answer.
""",

    "🧠 Explain Difficult Terminology": """
OUTPUT FORMAT:
- Create a clean glossary.
- Do not use large tables.
- Give every important term its own small section.

Use this structure:

# 🧠 Scientific Terminology Explained

### 1. [Term]
**Simple meaning:**  
Explain it in clear language.

**In this paper:**  
Explain what the term means specifically in the context of the supplied research paper.

### 2. [Term]
**Simple meaning:**  
Explanation.

**In this paper:**  
Context-specific explanation.

Continue for the important difficult terms.

## 🔤 Important Abbreviations
- **[Abbreviation]** — Full form and short explanation.
- Include only abbreviations whose meanings can be determined reliably.

## ⭐ Terms Worth Remembering
Finish with a short list of the most important terminology needed to understand the paper.
""",

    "📝 Generate Flashcards": """
OUTPUT FORMAT:
Do not use tables.
Create clean study flashcards suitable for active recall.

# 📝 Study Flashcards

## Flashcard 1

**❓ Question:**  
[Question]

**💡 Answer:**  
[Concise answer]

---

## Flashcard 2

**❓ Question:**  
[Question]

**💡 Answer:**  
[Concise answer]

---

Continue this format for the remaining flashcards.

Include a mixture of:
- Biological concepts
- Genes and proteins
- Experimental techniques
- Biological mechanisms
- Important results
- Why/how reasoning questions

Keep individual answers concise enough to function as genuine flashcards.
"""
}
def create_analysis_pdf(result, paper_name, analysis_tool):
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    elements = []

    # Report heading
    elements.append(
        Paragraph("BioResearch AI", styles["Title"])
    )

    elements.append(
        Paragraph("Research Paper Analysis", styles["Heading2"])
    )

    elements.append(Spacer(1, 20))
    
    elements.append(
    Paragraph(f"<b>Paper:</b> {paper_name}", styles["BodyText"])
)

    elements.append(
    Paragraph(f"<b>Analysis Mode:</b> {analysis_tool}", styles["BodyText"])
)

    elements.append(Spacer(1, 20)) 
    # Convert the AI response into PDF paragraphs
      # Convert Markdown headings into proper PDF headings
    for line in result.split("\n"): 
      line = line.strip()
# Convert Markdown bold syntax to ReportLab bold tags
      line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
      if not line:
        elements.append(Spacer(1, 6))
        continue

      if line.startswith("### "):
        elements.append(
            Paragraph(line[4:], styles["Heading3"])
        )

      elif line.startswith("## "):
        elements.append(
            Paragraph(line[3:], styles["Heading2"])
        )

      elif line.startswith("# "):
        elements.append(
            Paragraph(line[2:], styles["Heading1"])
        )
      elif line.startswith("- "):
          elements.append(
         Paragraph(
            f"• {line[2:]}",
            styles["BodyText"]
        )
    )

      else:
       elements.append(
        Paragraph(line, styles["BodyText"])
    )

    elements.append(Spacer(1, 6))
    pdf.build(elements)

    buffer.seek(0)

    return buffer.getvalue()
st.set_page_config(
    page_title="BioResearch AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)
# CRAFTING CSS

st.markdown("""
<style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    div.stButton > button[kind="primary"] {
    border-radius: 10px;
    font-weight: 600;
    border: none;
    color: white;
    background: linear-gradient(
        90deg,
        #6366f1 0%,
        #8b5cf6 50%,
        #06b6d4 100%
    );
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.25);
    transition: all 0.25s ease;
}
    [data-testid="stFileUploaderDropzone"] {
    border-radius: 12px;
    border: 1px dashed rgba(99, 102, 241, 0.55);
    background: linear-gradient(
        135deg,
        rgba(99, 102, 241, 0.08),
        rgba(6, 182, 212, 0.05)
    );
}
    [data-testid="stMetric"] {
    padding: 18px;
    border-radius: 14px;

    background: linear-gradient(
        135deg,
        rgba(139, 92, 246, 0.10),
        rgba(236, 72, 153, 0.04)
    );

    border: 1px solid rgba(167, 139, 250, 0.20);

    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}
    [data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(32, 29, 48, 0.98) 0%,
            rgba(22, 23, 36, 0.98) 100%
        );
    border-right: 1px solid rgba(167, 139, 250, 0.16);
}
    [data-baseweb="select"] > div {
    border-radius: 10px;
    background-color: rgba(30, 28, 45, 0.85);
    border-color: rgba(167, 139, 250, 0.25);
}

[data-testid="stDivider"] {
    border-color: rgba(167, 139, 250, 0.12);
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
}
[data-testid="stCaptionContainer"] {
    color: rgba(235, 232, 245, 0.68);
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid rgba(139, 92, 246, 0.18) !important;
    background: rgba(255, 255, 255, 0.018);
    padding: 4px;
}
[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid rgba(139, 92, 246, 0.15);
}
h2, h3 {
    letter-spacing: -0.02em;
}

h3 {
    margin-top: 0.8rem;
    margin-bottom: 0.4rem;
}
[data-testid="stDownloadButton"] button {
    border-radius: 10px;
    background: rgba(139, 92, 246, 0.07);
    border: 1px solid rgba(139, 92, 246, 0.22);
    color: rgba(245, 243, 255, 0.90);
    font-weight: 500;
}
    [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(139, 92, 246, 0.13),
            transparent 32%
        ),
        radial-gradient(
            circle at 90% 15%,
            rgba(236, 72, 153, 0.07),
            transparent 28%
        ),
        #11131f;
}
@media (max-width: 768px) {

    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-size: 2rem !important;
        line-height: 1.15 !important;
    }

    h2 {
        font-size: 1.55rem !important;
        line-height: 1.2 !important;
    }

    h3 {
        font-size: 1.3rem !important;
        line-height: 1.25 !important;
    }

}
[data-testid="stMetric"] {
    padding: 10px 14px !important;
    border-radius: 10px !important;
    min-height: 0 !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
}
/* Compact Streamlit's vertical layout on phones */
[data-testid="stVerticalBlock"] {
    gap: 0.75rem !important;
}

/* Smaller separators */
[data-testid="stDivider"] {
    margin-top: 0.6rem !important;
    margin-bottom: 0.6rem !important;
}

/* Compact bordered cards/containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
}

/* Smaller captions */
[data-testid="stCaptionContainer"] {
    font-size: 0.82rem !important;
    line-height: 1.4 !important;
}
/* Keep Document Overview metric columns compact on mobile */
[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
    flex-direction: row !important;
    gap: 0.45rem !important;
}

/* Each metric gets one-third of the row */
[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"])
[data-testid="stColumn"] {
    width: 33.33% !important;
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* Compact metric cards */
[data-testid="stMetric"] {
    padding: 9px 8px !important;
    min-height: 75px !important;
}

/* Small labels */
[data-testid="stMetricLabel"] p {
    font-size: 0.72rem !important;
    white-space: nowrap;
}

/* Smaller values */
[data-testid="stMetricValue"] {
    font-size: 1.15rem !important;
}
/* Tighter section spacing on mobile */
[data-testid="stDivider"] {
    margin-top: 0.35rem !important;
    margin-bottom: 0.35rem !important;
}

/* Reduce Streamlit block spacing */
.block-container [data-testid="stVerticalBlock"] {
    gap: 0.55rem !important;
}

/* Compact section headings */
h2, h3 {
    margin-top: 0.35rem !important;
    margin-bottom: 0.25rem !important;
}

/* Keep paragraphs compact */
p {
    margin-bottom: 0.4rem;
}
/* Compact Streamlit's top mobile header */
[data-testid="stHeader"] {
    height: 2.5rem !important;
    min-height: 2.5rem !important;
}

/* Keep the sidebar toggle centered in the smaller header */
[data-testid="stSidebarCollapsedControl"] {
    top: 0.25rem !important;
}

/* Pull the page upward after shrinking the header */
.block-container {
    padding-top: 0.75rem !important;
}
        );
}
</style>
""", unsafe_allow_html=True)
with st.container(border=True):
    st.title("🧬 BioResearch AI")
    st.markdown("### AI-powered biological research paper analysis")
    st.write(
        "Upload a research paper and transform complex biology into structured, understandable insights."
    )
st.divider()
st.subheader("📄 Research Paper")

uploaded_file = st.file_uploader(
    "Upload a biological or biotechnology research paper",
    type=["pdf"],
    help="PDF files only • Maximum 30 pages"
)
# CREATING SIDEBAR NOW
st.sidebar.title("⚙️ Analysis Settings")
st.sidebar.caption(
    "Customize how BioResearch AI analyzes and explains your paper."
)
st.sidebar.divider()
st.sidebar.markdown("### 🤖 AI Model")
model = st.sidebar.selectbox(
    "Choose AI model",
    ["command-a-plus-05-2026", "command-r-08-2024", "command-r-plus-08-2024"],
    index=None,
    placeholder="Select a model..."
)
st.sidebar.markdown("### 🧠 Explanation Level")
explanation_level = st.sidebar.selectbox(
    "Choose explanation level",
    ["Simple", "UG", "Advanced"],
    index=None,
    placeholder="Select a level..."
)
st.sidebar.markdown("### 📏 Response Depth")
response_depth = st.sidebar.selectbox(
    "Choose response depth",
    ["Concise", "Detailed", "Comprehensive"],
    index=None,
    placeholder="Select response depth..."
)

st.sidebar.caption(
    "🧬 BioResearch AI • Powered by Cohere"
)
# Next step: Detect successful PDF upload
# creating if condition:
if uploaded_file:
    st.success("Research paper loaded successfully")
    st.caption(f"📄 **{uploaded_file.name}**")
    pdf_bytes = uploaded_file.getvalue() #pdf_bytes = uploaded PDF's getvalue() ---- >> takes the uploaded PDF and gives you its raw binary data.
    pdf_document = fitz.open(stream=pdf_bytes , filetype="pdf") # tells PyMuPDF:-->> Here's some binary data in memory. Treat it as a PDF and open it.
    page_count = pdf_document.page_count # to count pages in that pdf 
    paper_text = ""
    for page in pdf_document:
        paper_text += page.get_text() # this is for extracting text from the pdf 
    st.markdown("#### 📋 Document Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📑 Pages", page_count)
    with col2:
        st.metric("📝 Characters", f"{len(paper_text):,}")
    with col3:
        if paper_text.strip():
            st.metric("🔎 Text Status", "Ready")
        else:
            st.metric("🔎 Text Status", "Unreadable")
    if not paper_text.strip(): # if the pdf is picture based and not text based this warning would be shown 
        st.error("No readable text could be extracted and the PDF may be scanned/image-based.")
        
st.divider()
st.subheader("🔬 Analyze Your Paper")
st.caption("Choose what you want BioResearch AI to investigate in this research paper.")
analysis_tool = st.selectbox(
    "What would you like to analyze?",
    [
        "🧬 Extract Genes / Proteins",
        "🧪 Explain Experimental Methodology",
        "🔬 Identify Laboratory Techniques",
        "📊 Explain Results",
        "🧫 Explain Biological Mechanisms",
        "📖 Generate Revision Notes",
        "❓ Generate Viva Questions",
        "🧠 Explain Difficult Terminology",
        "📝 Generate Flashcards"
    ],
    index=None,
    placeholder="Choose an analysis mode..."
)

analyze_button = st.button(
    "🚀 Analyze Paper",
    type="primary",
    use_container_width=True
)
if analyze_button:

    if not uploaded_file:
        st.error("⚠️ Please upload a research paper first.")
        st.stop()

    if not model:
        st.error("⚠️ Please select an AI model.")
        st.stop()

    if not explanation_level:
        st.error("⚠️ Please choose an explanation level.")
        st.stop()

    if not response_depth:
        st.error("⚠️ Please choose a response depth.")
        st.stop()

    if not analysis_tool:
        st.error("⚠️ Please select an analysis tool.")
        st.stop()

    if not paper_text.strip():
        st.error("⚠️ No readable text was found in this PDF.")
        st.stop()


    selected_instruction = analysis_instructions[analysis_tool]
    selected_format = output_formats[analysis_tool]
    messages = [
    {
        "role": "system",
        "content": f"""
You are BioResearch AI, an assistant specialized in analyzing biological and biotechnology research papers.

Follow these rules:
- Base your analysis primarily on the supplied research paper.
- Never fabricate experimental results, genes, proteins, methods, statistics, or conclusions.
- If information is missing or unclear, explicitly say so.
- Clearly distinguish information stated in the paper from general biological knowledge.
- Explanation level: {explanation_level}
- Response depth: {response_depth}

Specific analysis task:
{selected_instruction}
Required response format:
{selected_format}
"""
    },
    {
        "role": "user",
        "content": f"""
Analyze the following research paper according to the instructions provided.

--- RESEARCH PAPER START ---

{paper_text}

--- RESEARCH PAPER END ---
"""
    }
]
if analyze_button:
    try:
        with st.spinner(f"🧬 Analyzing paper • {analysis_tool}"):
            response = cohere_client.chat(
                model=model,
                messages=messages
            )

        result = ""

        for content in response.message.content:
            if content.type == "text":
                result += content.text
        if not result.strip():
           st.error("⚠️ No text response was returned.")
        else:
          st.divider()
          st.subheader("🧬 Analysis Results")
          st.caption(f"Analysis mode: {analysis_tool}")
          with st.container(border=True):
            st.markdown(result)
          pdf_data = create_analysis_pdf(
    result,
    uploaded_file.name,
    analysis_tool
)
          st.download_button(
    label="📥 Download Analysis as PDF",
    data=pdf_data,
    file_name="bioresearch_analysis.pdf",
    mime="application/pdf",
    use_container_width=True
)
    except Exception as e:
        st.error(f"⚠️ Analysis failed: {e}")