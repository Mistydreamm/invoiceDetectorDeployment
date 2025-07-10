
import streamlit as st
from paddleocr import PaddleOCR
import cv2
import fitz
import numpy as np
import os.path
import detector
import json
import glob 

# ---- OCR processing and detection ----

def write_results_to_file(texts, filename="ocr_results.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for line in texts:
            f.write(line + "\n")

def pngDetector(image_path):
    ocr = PaddleOCR(use_angle_cls=True, lang="fr")
    img = cv2.imread(image_path)
    result = ocr.predict(img)
    texts = result[0]['rec_texts']
    write_results_to_file(texts)

def pdfDetector(pdf_path):
    ocr = PaddleOCR(use_angle_cls=True, lang="fr")
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=300)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    result = ocr.predict(img)
    texts = result[0]['rec_texts']
    write_results_to_file(texts)

def pngOrPdf(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        pdfDetector(filepath)
    elif ext == ".png":
        pngDetector(filepath)
    else:
        st.error("Fichier non supporté (PDF ou PNG uniquement)")


st.title("Analyse de facture OCR avec extraction comptable")


input_folder = "images"  # Nom du dossier contenant les fichiers
file_paths = glob.glob(os.path.join(input_folder, "*.pdf")) + glob.glob(os.path.join(input_folder, "*.png"))

for file_path in file_paths:
    with st.spinner(f"📄 Analyse OCR de {os.path.basename(file_path)} en cours..."):
        pngOrPdf(file_path)
    with st.spinner("🧠 Envoi au modèle pour extraction comptable..."):
        basename = os.path.splitext(os.path.basename(file_path))[0]
        detector.sendPrompt(basename)
            
