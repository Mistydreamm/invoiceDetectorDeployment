
import streamlit as st
from paddleocr import PaddleOCR
import cv2
import fitz
import numpy as np
import os.path
import detector
import json

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

uploaded_file = st.file_uploader("📎 Uploadez une facture au format PDF ou PNG", type=["pdf", "png"])

if uploaded_file is not None:
    ext = uploaded_file.name.split(".")[-1].lower()
    temp_path = f"temp_upload.{ext}"

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("📄 Analyse OCR en cours..."):
        pngOrPdf(temp_path)

    with st.spinner("🧠 Envoi au modèle pour extraction comptable..."):
        detector.sendPrompt()

# Affichage si le JSON existe
if os.path.exists("facture_analysee.json"):
    st.subheader("📊 Résultat de l'analyse (facture_analysee.json)")
    with open("facture_analysee.json", "r", encoding="utf-8") as f:
        result_json = json.load(f)
        st.json(result_json)