import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import PyPDF2
except ImportError:
    install('PyPDF2')
    import PyPDF2

try:
    reader = PyPDF2.PdfReader('Informe Final Herramienta de gestion de horarios (1).pdf')
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
except Exception as e:
    print(f"Error reading PDF: {e}")
