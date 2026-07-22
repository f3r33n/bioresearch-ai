# 🧬 BioResearch AI

BioResearch AI is an AI-powered research paper analyzer built with Python and Streamlit, designed specifically for biology and biotechnology papers.

Upload a PDF, choose how you want it analyzed, and get structured explanations tailored to your study or research needs.

## ✨ Features

- 📄 Upload and extract text from research papers
- 🧬 Explain biological mechanisms
- 🧪 Analyze experimental methodology
- 📊 Interpret results and findings
- 🧠 Explain difficult terminology
- 📝 Generate revision notes
- 🃏 Generate flashcards
- 🎤 Generate viva questions
- 📋 Summarize research papers
- 🎓 Adjustable explanation level
- 📏 Adjustable response depth
- 📥 Export AI analysis as PDF
- 📱 Responsive desktop and mobile interface

## 📸 Preview

### Desktop
![BioResearch AI Desktop](screenshots/desktop.png)

### Mobile
![BioResearch AI Mobile](screenshots/mobile.png)

## 🛠️ Built With

- Python
- Streamlit
- Cohere API
- PyMuPDF
- ReportLab
- Custom CSS

## 🚀 Running Locally

Clone the repository:

git clone https://github.com/YOUR_USERNAME/bioresearch-ai.git

Install dependencies:

pip install -r requirements.txt

Create a `.env` file:

COHERE_API_KEY=your_api_key_here

Run the application:

streamlit run pdf.py

## ⚠️ Limitations

BioResearch AI is an educational prototype. AI-generated analysis may contain inaccuracies and should not replace critical reading of the original research paper.

Scanned/image-only PDFs may not work correctly because the current version relies primarily on extractable PDF text.

## 🔮 Future Improvements

- Large-document chunking
- OCR support for scanned papers
- Paper-aware citations
- Improved PDF reports
- Better handling of tables and figures

## 👨‍💻 Author

Built as a learning project exploring Python, Streamlit, LLM APIs, PDF processing, and AI-assisted scientific analysis.
