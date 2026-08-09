from PIL import Image, ExifTags
import os
import cv2
import numpy as np

from ai_detector_v4 import detect_ai_image_v4


def analyze_image(file_path: str):

    findings = []
    metadata_findings = []

    try:
        # =========================================================
        # AI DETECTION - V4
        # =========================================================

        ai_results = detect_ai_image_v4(file_path)

        ai_fake_score = 0.0

        for item in ai_results:

            label = str(item.get("label", "")).lower()
            score = float(item.get("score", 0))

            if label == "deepfake":
                ai_fake_score = score * 100

        # =========================================================
        # OPEN IMAGE
        # =========================================================

        image = Image.open(file_path)

        width, height = image.size
        image_format = image.format
        file_size = os.path.getsize(file_path)

        # =========================================================
        # EXIF / METADATA
        # =========================================================

        exif_data = image.getexif()
        readable_exif = {}

        if not exif_data:

            metadata_findings.append(
                "No EXIF metadata found"
            )

        else:

            for tag_id, value in exif_data.items():

                tag_name = ExifTags.TAGS.get(
                    tag_id,
                    str(tag_id)
                )

                readable_exif[tag_name] = value

            if "Make" in readable_exif:

                metadata_findings.append(
                    f"Camera manufacturer: "
                    f"{readable_exif['Make']}"
                )

            if "Model" in readable_exif:

                metadata_findings.append(
                    f"Camera model: "
                    f"{readable_exif['Model']}"
                )

            if "Software" in readable_exif:

                software = str(
                    readable_exif["Software"]
                )

                metadata_findings.append(
                    f"Software metadata present: {software}"
                )

                findings.append(
                    "Software metadata was detected; "
                    "this may indicate editing or processing "
                    "but does not by itself prove manipulation"
                )

        # =========================================================
        # OPENCV
        # =========================================================

        cv_image = cv2.imread(file_path)

        if cv_image is None:

            raise ValueError(
                "Unable to decode image"
            )

        gray = cv2.cvtColor(
            cv_image,
            cv2.COLOR_BGR2GRAY
        )

        # =========================================================
        # NOISE / RESIDUAL ANALYSIS
        # =========================================================

        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        residual = (
            gray.astype(np.float32)
            -
            blurred.astype(np.float32)
        )

        noise_level = float(
            np.std(residual)
        )

        if noise_level < 3:

            findings.append(
                "Very low image noise was detected"
            )

        elif noise_level > 40:

            findings.append(
                "Unusually high image noise was detected"
            )

        else:

            findings.append(
                "Image noise level is within the observed range"
            )

        # =========================================================
        # EDGE ANALYSIS
        # =========================================================

        edges = cv2.Canny(
            gray,
            100,
            200
        )

        edge_ratio = float(
            np.mean(edges > 0)
        )

        if edge_ratio < 0.01:

            findings.append(
                "Low edge-detail density detected"
            )

        elif edge_ratio > 0.20:

            findings.append(
                "High edge-detail density detected"
            )

        # =========================================================
        # JPEG ANALYSIS
        # =========================================================

        jpeg_indicator = 0

        if image_format == "JPEG":

            # Estimate JPEG compression artifacts using
            # high-frequency residual energy.

            dct_input = np.float32(gray) / 255.0

            dct = cv2.dct(
                dct_input
            )

            h, w = dct.shape

            block_h = min(h, 512)
            block_w = min(w, 512)

            sample = dct[
                :block_h,
                :block_w
            ]

            high_frequency_energy = float(
                np.mean(
                    np.abs(sample)
                )
            )

            if high_frequency_energy < 0.025:

                jpeg_indicator = 1

                findings.append(
                    "Low JPEG high-frequency energy detected"
                )

            elif high_frequency_energy > 0.15:

                jpeg_indicator = 1

                findings.append(
                    "High JPEG high-frequency energy detected"
                )

        # =========================================================
        # IMAGE SIZE / QUALITY
        # =========================================================

        resolution_indicator = 0

        if width < 256 or height < 256:

            resolution_indicator = 1

            findings.append(
                "Low-resolution image detected; "
                "resolution may affect AI and forensic reliability"
            )

        # =========================================================
        # FORENSIC EVIDENCE SCORE
        #
        # This is NOT a probability.
        # It represents supporting indicators only.
        # =========================================================

        forensic_score = 0

        if noise_level < 3:
            forensic_score += 10

        elif noise_level > 40:
            forensic_score += 5

        if edge_ratio < 0.01:
            forensic_score += 10

        if jpeg_indicator:
            forensic_score += 10

        if exif_data and "Software" in readable_exif:
            forensic_score += 10

        if resolution_indicator:
            forensic_score += 5

        forensic_score = min(
            forensic_score,
            100
        )

        # =========================================================
        # AI ASSESSMENT
        #
        # IMPORTANT:
        # V4 score is treated as an AI SCORE, NOT a calibrated
        # probability.
        # =========================================================

        ai_score = round(
            ai_fake_score,
            2
        )

        # =========================================================
        # EVIDENCE AGREEMENT
        # =========================================================

        supporting_forensic_evidence = forensic_score >= 20

        ai_high = ai_score >= 70
        ai_medium = 40 <= ai_score < 70
        ai_low = ai_score < 40

        # =========================================================
        # FINAL ASSESSMENT
        #
        # We deliberately avoid calling the AI score a probability.
        # =========================================================

        if ai_high and supporting_forensic_evidence:

            risk = "HIGH"

            assessment = (
                "High-risk synthetic-media indicators"
            )

            findings.append(
                "AI assessment and supporting forensic "
                "indicators are directionally consistent"
            )

        elif ai_high and not supporting_forensic_evidence:

            risk = "MEDIUM"

            assessment = (
                "AI indicates elevated manipulation risk, "
                "but supporting forensic evidence is weak"
            )

            findings.append(
                "AI assessment is not strongly supported "
                "by the available forensic indicators"
            )

        elif ai_medium and supporting_forensic_evidence:

            risk = "MEDIUM"

            assessment = (
                "Moderate manipulation indicators detected"
            )

            findings.append(
                "Moderate AI indicators have supporting "
                "forensic evidence"
            )

        elif ai_medium:

            risk = "MEDIUM"

            assessment = (
                "Inconclusive / moderate AI indicators"
            )

            findings.append(
                "AI indicators are moderate and forensic "
                "evidence is insufficient for a strong conclusion"
            )

        elif ai_low and supporting_forensic_evidence:

            risk = "LOW"

            assessment = (
                "Predominantly authentic characteristics, "
                "with some forensic anomalies"
            )

            findings.append(
                "AI assessment is predominantly authentic, "
                "but forensic anomalies were detected"
            )

        else:

            risk = "LOW"

            assessment = (
                "Predominantly authentic characteristics"
            )

            findings.append(
                "No strong synthetic-media evidence was identified"
            )

        # =========================================================
        # AUTHENTICITY SCORE
        #
        # This is an assessment score, not a probability.
        # =========================================================

        authenticity_score = round(
            100 - ai_score
        )

        # =========================================================
        # AI FINDINGS
        # =========================================================

        if ai_high:

            findings.append(
                "AI detector produced a high deepfake score"
            )

        elif ai_medium:

            findings.append(
                "AI detector produced a moderate deepfake score"
            )

        else:

            findings.append(
                "AI detector produced a low deepfake score"
            )

        # =========================================================
        # FORENSIC INTERPRETATION
        # =========================================================

        if forensic_score >= 40:

            findings.append(
                "Multiple forensic indicators were identified"
            )

        elif forensic_score >= 20:

            findings.append(
                "Some supporting forensic indicators were identified"
            )

        else:

            findings.append(
                "No significant supporting forensic indicators detected"
            )

        # =========================================================
        # FINAL RESULT
        # =========================================================

        return {

    # AI SCORE — NOT A CALIBRATED PROBABILITY
    "deepfake_probability": ai_score,

    "ai_fake_score": ai_score,

    "ai_score_type":
        "uncalibrated_model_score",

    "confidence":
        (
            "High"
            if ai_high and supporting_forensic_evidence
            else
            "Moderate"
            if ai_medium
            else
            "Low"
        ),

            "authenticity_score":
                authenticity_score,

            "risk":
                risk,

            "assessment":
                assessment,

            "ai_detection":
                ai_results,

            "forensic_score":
                forensic_score,

            "findings":
                findings,

            "metadata":
                metadata_findings,

            "technical": {

                "width":
                    width,

                "height":
                    height,

                "format":
                    image_format,

                "file_size":
                    file_size,

                "noise_level":
                    round(
                        noise_level,
                        2
                    ),

                "edge_ratio":
                    round(
                        edge_ratio,
                        4
                    ),

                "jpeg_indicator":
                    jpeg_indicator,

                "resolution_indicator":
                    resolution_indicator
            }
        }

    # =============================================================
    # ERROR HANDLING
    # =============================================================

    except Exception as error:

        return {

            "deepfake_probability":
                0,

            "authenticity_score":
                0,

            "risk":
                "ERROR",

            "assessment":
                "Analysis failed",

            "ai_detection":
                [],

            "ai_fake_score":
                0,

            "forensic_score":
                0,

            "findings": [

                f"Analysis failed: {str(error)}"

            ],

            "metadata":
                [],

            "technical":
                {}
        }