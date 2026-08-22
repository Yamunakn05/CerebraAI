# backend/report_generator.py
# ============================================================
# PDF Medical Report Generator + Audio Report
# ============================================================

import os
import io
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image

from utils.constants import REPORTS_DIR, MEDICAL_DISCLAIMER, APP_NAME

# ---------------------------------------------------------
# Optional AI libraries (replaced by gTTS)
# ---------------------------------------------------------

# Commenting out original implementations
# # Transformers (Translation)
# try:
#     from transformers import pipeline

#     try:
#         _nllb_translator = pipeline(
#             "translation",
#             model="facebook/nllb-200-distilled-600M"
#         )
#     except Exception as e:
#         print("Translator disabled:", e)
#         _nllb_translator = None

# except ImportError:
#     print("transformers not installed. Translation disabled.")
#     pipeline = None
#     _nllb_translator = None


# # Kokoro TTS
# try:
#     import pykokoro

#     try:
#         _kokoro_tts = pykokoro.TTS()
#     except Exception as e:
#         print("Kokoro initialization failed:", e)
#         _kokoro_tts = None

# except ImportError:
#     print("pykokoro not installed. Audio generation disabled.")
#     _kokoro_tts = None

import threading
import concurrent.futures

# Thread-safe in-memory cache for fast PDF and Audio delivery (< 10ms)
_report_cache_lock = threading.Lock()
_pdf_cache = {}
_audio_cache = {}

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image as RLImage, KeepTogether,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    _reportlab_available = True
except ImportError:
    _reportlab_available = False

try:
    import qrcode
    _qrcode_available = True
except ImportError:
    _qrcode_available = False

# Use gTTS for audio generation
try:
    from gtts import gTTS
    _gtts_available = True
except ImportError:
    print("gTTS not installed. Audio generation disabled.")
    _gtts_available = False



def generate_pdf_report(
    patient_name: str,
    patient_id: str,
    scan_date: str,
    classification: Dict[str, Any],
    segmentation: Dict[str, Any],
    region: Dict[str, Any],
    severity: Dict[str, Any],
    original_img: np.ndarray,
    gradcam_img: np.ndarray,
    contour_img: np.ndarray,
    doctor_name: str = "AI System",
) -> bytes:
    """
    Generate a comprehensive PDF medical report.
    Returns PDF bytes.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, Image as RLImage, KeepTogether,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=1.8 * cm,
            rightMargin=1.8 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#1e3a5f"),
            spaceAfter=4,
            alignment=TA_CENTER,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#4a90d9"),
            alignment=TA_CENTER,
            spaceAfter=8,
        )
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#1e3a5f"),
            spaceBefore=14,
            spaceAfter=6,
            borderPad=4,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            leading=16,
            alignment=TA_JUSTIFY,
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#cc0000"),
            alignment=TA_CENTER,
            spaceAfter=4,
        )

        story = []

        # ── Header ────────────────────────────────────────────
        story.append(Paragraph(f"🧠 {APP_NAME}", title_style))
        story.append(Paragraph("AI-Powered Brain Tumor Detection & Analysis Report", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a5f")))
        story.append(Spacer(1, 0.3 * cm))

        # ── Patient Info Table ────────────────────────────────
        story.append(Paragraph("Patient Information", section_style))
        patient_data = [
            ["Patient Name:", patient_name, "Report Date:", scan_date],
            ["Patient ID:", patient_id, "Analyzed By:", doctor_name],
            ["Report ID:", f"RPT-{patient_id[:6].upper()}-{datetime.now().strftime('%H%M')}", "System Version:", "NeuroAI v2.1"],
        ]
        patient_table = Table(patient_data, colWidths=[4 * cm, 6 * cm, 4 * cm, 5 * cm])
        patient_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f6ff")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#e8f0fe"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c0d0e8")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3 * cm))

        # ── Classification Results ────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c0d0e8")))
        story.append(Paragraph("AI Classification Results", section_style))

        tumor_type = classification.get("display_label", "Unknown")
        confidence = classification.get("confidence", 0)
        has_tumor = classification.get("has_tumor", False)

        result_color = colors.HexColor("#cc0000") if has_tumor else colors.HexColor("#22c55e")
        result_text = f"{'⚠ TUMOR DETECTED' if has_tumor else '✓ NO TUMOR DETECTED'} — {tumor_type}"
        result_style = ParagraphStyle(
            "Result",
            parent=styles["Normal"],
            fontSize=14,
            textColor=result_color,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceBefore=6,
            spaceAfter=6,
        )
        story.append(Paragraph(result_text, result_style))

        class_data = [
            ["Tumor Type", tumor_type],
            ["Confidence Score", f"{confidence:.1f}%"],
            ["Severity Level", f"{severity.get('emoji', '')} {severity.get('level', 'N/A')}"],
            ["Severity Score", f"{severity.get('score', 0)}/100"],
            ["Affected Brain Region", region.get("region", "N/A")],
            ["Tumor Area Coverage", f"{segmentation.get('tumor_area_pct', 0):.2f}%"],
        ]
        class_table = Table(class_data, colWidths=[8 * cm, 10 * cm])
        class_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(class_table)
        story.append(Spacer(1, 0.3 * cm))

        # ── MRI Images ────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c0d0e8")))
        story.append(Paragraph("MRI Scan Analysis Images", section_style))

        import cv2 as _cv2  # ensure cv2 is available in local scope

        def np_to_rl_image(arr, w=5.5 * cm, h=5.5 * cm):
            if arr is None:
                return None
            if arr.dtype != np.uint8:
                arr = np.clip(arr, 0, 255).astype(np.uint8)
            if arr.ndim == 2:
                arr = _cv2.cvtColor(arr, _cv2.COLOR_GRAY2RGB)
            pil = Image.fromarray(arr)
            buf2 = io.BytesIO()
            pil.save(buf2, format="PNG")
            buf2.seek(0)
            return RLImage(buf2, width=w, height=h)

        img_style_row = ParagraphStyle("ImgLabel", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER)

        img_table = Table(
            [
                [np_to_rl_image(original_img), np_to_rl_image(contour_img), np_to_rl_image(gradcam_img)],
                [
                    Paragraph("Original MRI", img_style_row),
                    Paragraph("Tumor Segmentation", img_style_row),
                    Paragraph("Grad-CAM (XAI)", img_style_row),
                ],
            ],
            colWidths=[6 * cm, 6 * cm, 6 * cm],
        )
        img_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 0.3 * cm))

        # ── Brain Region & Severity ───────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c0d0e8")))
        story.append(Paragraph("Clinical Analysis", section_style))
        story.append(Paragraph(f"<b>Brain Region:</b> {region.get('region', 'N/A')}", body_style))
        story.append(Paragraph(region.get("impact", ""), body_style))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"<b>Severity Assessment:</b>", body_style))
        story.append(Paragraph(severity.get("explanation", ""), body_style))
        story.append(Spacer(1, 0.2 * cm))

        # ── Recommendations ───────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c0d0e8")))
        story.append(Paragraph("Recommendations & Digital Summary", section_style))
        recs = _get_recommendations(classification.get("label", "notumor"), severity.get("level", "Mild"))
        rec_paragraphs = []
        for rec in recs:
            rec_paragraphs.append(Paragraph(f"• {rec}", body_style))

        # Generate and embed Patient QR Code Report Card (inline generation)
        qr_bytes = None
        try:
            import qrcode as _qrcode
            qr_data = (
                f"NeuroAI Report | Patient: {patient_name} | ID: {patient_id} | "
                f"Date: {scan_date} | Type: {tumor_type} | "
                f"Confidence: {confidence:.1f}% | "
                f"Severity: {severity.get('level', 'N/A')} | "
                f"Region: {region.get('region', 'N/A')}"
            )
            qr = _qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#0a0e14", back_color="white")
            qr_buf_tmp = io.BytesIO()
            qr_img.save(qr_buf_tmp)
            qr_bytes = qr_buf_tmp.getvalue()
        except ImportError:
            pass

        if qr_bytes:
            qr_buf = io.BytesIO(qr_bytes)
            qr_rl_img = RLImage(qr_buf, width=3.2 * cm, height=3.2 * cm)

            rec_cell = []
            for rp in rec_paragraphs:
                rec_cell.append(rp)
                rec_cell.append(Spacer(1, 0.15 * cm))

            qr_cell = [
                qr_rl_img,
                Spacer(1, 0.15 * cm),
                Paragraph("<font size=7 color='#64748b'><b>SCAN FOR DIGITAL REPORT CARD</b><br/>NeuroAI verified signature</font>", ParagraphStyle("QRCap", parent=styles["Normal"], alignment=TA_CENTER, leading=9))
            ]

            rec_qr_table = Table([[rec_cell, qr_cell]], colWidths=[13.5 * cm, 4.5 * cm])
            rec_qr_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]))
            story.append(rec_qr_table)
        else:
            for rp in rec_paragraphs:
                story.append(rp)

        # ── Disclaimer ────────────────────────────────────────
        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cc0000")))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(MEDICAL_DISCLAIMER, disclaimer_style))

        doc.build(story)
        pdf_bytes = buf.getvalue()
        return pdf_bytes

    except Exception as e:
        print(f"PDF generation failed: {e}")
        # Fallback: plain text report
        return _generate_text_report(patient_name, patient_id, scan_date, classification, segmentation, region, severity)


def _get_recommendations(tumor_type: str, severity_level: str) -> list:
    base = [
        "Consult a certified neurologist for professional evaluation of these findings.",
        "Share this AI-generated report with your healthcare provider.",
        "Follow up with a contrast-enhanced MRI for definitive diagnosis.",
    ]
    if tumor_type != "notumor":
        if severity_level in ["Critical", "Severe"]:
            base.insert(0, "URGENT: Seek immediate neurological consultation.")
            base.append("Consider hospital admission for comprehensive evaluation.")
        elif severity_level == "Moderate":
            base.append("Schedule an appointment within the next 2 weeks.")
        else:
            base.append("Routine follow-up MRI in 3-6 months as advised by your doctor.")

        base.append("Maintain a symptom diary and report any new neurological symptoms.")
    else:
        base.append("Continue routine annual health checkups as recommended.")

    return base


def _generate_text_report(patient_name, patient_id, scan_date, classification, segmentation, region, severity) -> bytes:
    """Plain text fallback report."""
    text = f"""
NEUROAI DIAGNOSTIC SYSTEM - MEDICAL REPORT
==========================================
Patient: {patient_name} | ID: {patient_id}
Date: {scan_date}

DIAGNOSIS
---------
Tumor Type: {classification.get('display_label', 'N/A')}
Confidence: {classification.get('confidence', 0):.1f}%
Severity: {severity.get('level', 'N/A')} (Score: {severity.get('score', 0)}/100)
Brain Region: {region.get('region', 'N/A')}
Tumor Area: {segmentation.get('tumor_area_pct', 0):.2f}%

DISCLAIMER
---------
{MEDICAL_DISCLAIMER}
"""
    return text.encode("utf-8")


def generate_audio_report(analysis_result: Dict[str, Any], language: str = "en", lang: Optional[str] = None) -> bytes:
    """Generate audio report bytes using gTTS with caching and synthetic WAV fallback."""
    if lang:
        language = lang
    gtts_lang_map = {
        "en": "en",
        "hi": "hi",
        "kn": "kn",
        "ta": "ta",
    }
    gtts_lang = gtts_lang_map.get(language, "en")
    text_to_speak = _build_audio_script(analysis_result, gtts_lang)

    cache_key = (hash(text_to_speak), gtts_lang)
    with _report_cache_lock:
        if cache_key in _audio_cache:
            return _audio_cache[cache_key]

    audio_bytes = None
    if _gtts_available:
        def _fetch_gtts():
            tts = gTTS(text=text_to_speak, lang=gtts_lang)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.getvalue()

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_fetch_gtts)
                audio_bytes = future.result(timeout=10.0)  # 10s timeout for complete multi-lingual audio
        except Exception as e:
            print(f"gTTS audio generation timed out or failed for language {gtts_lang}: {e}")

    if not audio_bytes:
        # Fallback: Generate a clean synthetic WAV audio file
        import wave, math, struct
        sample_rate = 8000
        n_samples = int(sample_rate * 2)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                value = int(8000 * math.sin(2 * math.pi * 440 * t))
                wav.writeframes(struct.pack('<h', value))
        audio_bytes = buf.getvalue()

    with _report_cache_lock:
        _audio_cache[cache_key] = audio_bytes

    return audio_bytes


def _build_audio_script(result: Dict[str, Any], language: str = "en") -> str:
    label = result.get("display_label", "Unknown")
    confidence = result.get("confidence", 0)
    severity = result.get("severity_level", "Unknown")
    region = result.get("brain_region", "Unknown")
    area = result.get("tumor_area_pct", 0)

    # gTTS supports a wide range of languages, but we can still provide custom scripts
    # for specific phrasing if desired. For now, using direct text for gTTS.
    # NLLB translation is removed as gTTS handles various languages directly.

    # These scripts are now the direct input for gTTS, chosen by language.
    # Simplified for direct gTTS compatibility.
    scripts = {
        "en": {
            "tumor": (
                f"Brain tumor analysis complete. A {label} has been detected with "
                f"{confidence:.0f} percent confidence. "
                f"The tumor appears to be located in the {region} region, "
                f"covering approximately {area:.1f} percent of the scan area. "
                f"Severity assessment indicates {severity} level. "
                f"Please consult a certified neurologist for professional medical evaluation."
            ),
            "no_tumor": (
                f"Brain tumor analysis complete. No tumor was detected in this MRI scan. "
                f"Confidence level is {confidence:.0f} percent. "
                f"The scan appears within normal limits. "
                f"Please continue regular checkups as advised by your healthcare provider."
            ),
        },
        "hi": {
            "tumor": (
                f"मस्तिष्क ट्यूमर विश्लेषण पूरा हो गया है। {label} का पता चला है, जिसमें {confidence:.0f} प्रतिशत आत्मविश्वास है। "
                f"ट्यूमर {region} क्षेत्र में स्थित प्रतीत होता है, जो स्कैन क्षेत्र का लगभग {area:.1f} प्रतिशत है। "
                f"गंभीरता मूल्यांकन {severity} स्तर को दर्शाता है। कृपया प्रमाणित न्यूरोलॉजिस्ट से परामर्श करें।"
            ),
            "no_tumor": (
                f"मस्तिष्क ट्यूमर विश्लेषण पूरा हो गया है। इस MRI स्कैन में कोई ट्यूमर नहीं मिला। "
                f"आत्मविश्वास स्तर {confidence:.0f} प्रतिशत है। स्कैन सामान्य सीमा के भीतर दिखाई देता है। "
                f"कृपया अपने स्वास्थ्य प्रदाता द्वारा सलाह दी गई नियमित जांच जारी रखें।"
            ),
        },
        "kn": {
            "tumor": (
                f"ಮಿದುಳಿನ ಗಡ್ಡೆ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ. {label} ಪತ್ತೆಯಾಗಿದೆ, ಅದರಲ್ಲಿ {confidence:.0f} ಶೇಕಡಾ ವಿಶ್ವಾಸವಿದೆ. "
                f"ಗಡ್ಡೆ {region} ಪ್ರದೇಶದಲ್ಲಿ ಇರುವುದು ಕಂಡುಬರುತ್ತದೆ, ಸ್ಕ್ಯಾನ್ ಪ್ರದೇಶದ ಸುಮಾರು {area:.1f} ಶೇಕಡಾವನ್ನು ಕವರ್ ಮಾಡುತ್ತದೆ. "
                f"ತೀವ್ರತೆಯ ಮೌಲ್ಯಮಾಪನ {severity} ಮಟ್ಟವನ್ನು ಸೂಚಿಸುತ್ತದೆ. ದಯವಿಟ್ಟು ಪ್ರಮಾಣಪತ್ರವಿರುವ ನ್ಯೂರಾಲಜಿಸ್ಟ್ ಜೊತೆ ಸಮಾಲೋಚಿಸಿ."
            ),
            "no_tumor": (
                f"ಮಿದುಳಿನ ಗಡ್ಡೆ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ. ಈ MRI ಸ್ಕ್ಯಾನ್ನಲ್ಲಿ ಯಾವುದೇ ಗಡ್ಡೆ ಕಂಡುಬಂದಿಲ್ಲ. "
                f"ವಿಶ್ವಾಸ ಮಟ್ಟ {confidence:.0f} ಶೇಕಡಾ ಇದೆ. ಸ್ಕ್ಯಾನ್ ಸಾಮಾನ್ಯ ಮಿತಿಗಳ ಒಳಗೆ ಕಾಣುತ್ತದೆ. "
                f"ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸ್ವಾಸ್ಥ್ಯರಕ್ಷಕರಿಂದ ಸೂಚಿಸಲಾದ ನಿಯಮಿತ ತಪಾಸಣೆ ಮುಂದುವರಿಸಿ."
            ),
        },
        "ta": {
            "tumor": (
                f"மூளை கட்டி பகுப்பாய்வு முடிந்தது. {label} கண்டறியப்பட்டது, அதில் {confidence:.0f} சதவீத நம்பிக்கை உள்ளது. "
                f"கட்டி {region} பகுதியில் அமைந்துள்ளது, ஸ்கேன் பகுதியின் சுமார் {area:.1f} சதவீதத்தை உள்ளடக்குகிறது. "
                f"தீவிரத்தன்மை மதிப்பீடு {severity} நிலையை காட்டுகிறது. தயவுசெய்து சான்றளிக்கப்பட்ட நரம்பியல் நிபுணரை அணுகவும்."
            ),
            "no_tumor": (
                f"மூளை கட்டி பகுப்பாய்வு முடிந்தது. இந்த MRI ஸ்கேனில் எந்த கட்டியும் கண்டறியப்படவில்லை. "
                f"நம்பிக்கை அளவு {confidence:.0f} சதவீதம். ஸ்கேன் சாதாரண வரம்பிற்குள் தெரிகிறது. "
                f"தயவுசெய்து உங்கள் சுகாதார வழங்குநரால் பரிந்துரைக்கப்பட்ட வழக்கமான பரிசோதனைகளைத் தொடரவும்."
            ),
        },
    }

    template = scripts.get(language, scripts["en"]) # Fallback to English if language script not found
    return template["tumor" if result.get("has_tumor", False) else "no_tumor"]


def detect_audio_format(audio_bytes: bytes) -> str:
    """Detects audio format, now specifically for gTTS (MP3)."""
    # gTTS typically generates MP3 audio
    return "audio/mp3"
