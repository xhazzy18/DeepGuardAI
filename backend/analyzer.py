from PIL import Image, ExifTags
import os
import cv2
import numpy as np

from ai_detector_v4 import detect_ai_image_v4


def analyze_image(file_path: str):
    findings = []
    metadata_findings = []
    forensic_indicators = []

    try:
        # =========================================================
        # AI DETECTION - V4
        # =========================================================

        ai_results = detect_ai_image_v4(file_path)

        ai_fake_score = 0.0

        for item in ai_results:
            label = str(item.get("label", "")).lower().strip()
            score = float(item.get("score", 0))

            if label in {
                "deepfake",
                "fake",
                "artificial",
                "ai-generated",
                "ai generated",
                "synthetic",
            }:
                ai_fake_score = max(
                    ai_fake_score,
                    score * 100
                )

        ai_score = round(ai_fake_score, 2)

        # =========================================================
        # OPEN IMAGE
        # =========================================================

        image = Image.open(file_path)

        width, height = image.size
        image_format = image.format or "Unknown"
        file_size = os.path.getsize(file_path)

        # =========================================================
        # BASIC IMAGE VALIDATION
        # =========================================================

        if width < 256 or height < 256:

            findings.append(
                "Low-resolution image detected; "
                "this may reduce forensic reliability"
            )

            forensic_indicators.append(
                "low_resolution"
            )

        # =========================================================
        # EXIF / METADATA ANALYSIS
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

                try:
                    readable_exif[tag_name] = str(value)

                except Exception:
                    readable_exif[tag_name] = "<unreadable>"

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

                software = readable_exif["Software"]

                metadata_findings.append(
                    f"Software metadata present: {software}"
                )

                findings.append(
                    "Image-processing software metadata was detected; "
                    "this may indicate editing or processing, "
                    "but does not prove manipulation"
                )

                forensic_indicators.append(
                    "software_metadata"
                )

            if "DateTime" in readable_exif:

                metadata_findings.append(
                    f"Capture/edit timestamp: "
                    f"{readable_exif['DateTime']}"
                )

        # =========================================================
        # OPENCV IMAGE ANALYSIS
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
        # IMAGE NOISE ANALYSIS
        #
        # Technical measurement only.
        # NOT treated as proof of AI generation.
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
                "Very low high-frequency image noise was measured"
            )

        elif noise_level > 40:

            findings.append(
                "High high-frequency image noise was measured"
            )

        else:

            findings.append(
                "Image noise measurement is within the observed range"
            )

        # =========================================================
        # EDGE ANALYSIS
        #
        # Technical measurement only.
        # NOT treated as a deepfake indicator.
        # =========================================================

        edges = cv2.Canny(
            gray,
            100,
            200
        )

        edge_ratio = float(
            np.mean(edges > 0)
        )

        # =========================================================
        # IMAGE CHARACTERISTICS
        # =========================================================

        if image_format.upper() == "JPEG":

            findings.append(
                "JPEG-compressed image detected"
            )

        elif image_format.upper() == "PNG":

            findings.append(
                "PNG image detected"
            )

        # =========================================================
        # FORENSIC EVIDENCE SCORING
        #
        # IMPORTANT:
        # This is a supporting-indicator score.
        # It is NOT a probability of manipulation.
        # It is NOT a ground-truth forensic conclusion.
        # =========================================================

        forensic_score = 0

        # ---------------------------------------------------------
        # 1. Software / editing metadata
        # ---------------------------------------------------------

        if "software_metadata" in forensic_indicators:

            forensic_score += 15

        # ---------------------------------------------------------
        # 2. Low resolution
        #
        # Only a small weight because low resolution affects
        # reliability rather than proving manipulation.
        # ---------------------------------------------------------

        if "low_resolution" in forensic_indicators:

            forensic_score += 5

        # ---------------------------------------------------------
        # 3. Very low image noise
        # ---------------------------------------------------------

        if noise_level < 3:

            forensic_score += 10

            if "very_low_noise" not in forensic_indicators:

                forensic_indicators.append(
                    "very_low_noise"
                )

        # ---------------------------------------------------------
        # 4. Very high image noise
        # ---------------------------------------------------------

        elif noise_level > 40:

            forensic_score += 8

            if "high_noise" not in forensic_indicators:

                forensic_indicators.append(
                    "high_noise"
                )

        # ---------------------------------------------------------
        # 5. Very low edge density
        # ---------------------------------------------------------

        if edge_ratio < 0.015:

            forensic_score += 8

            if "low_edge_density" not in forensic_indicators:

                forensic_indicators.append(
                    "low_edge_density"
                )

        # ---------------------------------------------------------
        # 6. Very high edge density
        # ---------------------------------------------------------

        elif edge_ratio > 0.25:

            forensic_score += 6

            if "high_edge_density" not in forensic_indicators:

                forensic_indicators.append(
                    "high_edge_density"
                )

        # ---------------------------------------------------------
        # 7. Missing EXIF metadata
        #
        # Common for WhatsApp, screenshots, social media,
        # and exported images, therefore only a very small weight.
        # ---------------------------------------------------------

        if not exif_data:

            forensic_score += 3

            if "missing_exif" not in forensic_indicators:

                forensic_indicators.append(
                    "missing_exif"
                )

        # ---------------------------------------------------------
        # 8. JPEG compression context
        #
        # JPEG compression does NOT mean manipulation.
        # Only minimal contextual weight is applied.
        # ---------------------------------------------------------

        if image_format.upper() == "JPEG":

            forensic_score += 2

            if "jpeg_compression" not in forensic_indicators:

                forensic_indicators.append(
                    "jpeg_compression"
                )

        # ---------------------------------------------------------
        # FINAL SCORE LIMIT
        # ---------------------------------------------------------

        forensic_score = min(
            max(
                forensic_score,
                0
            ),
            100
        )

        # =========================================================
        # FORENSIC LEVEL
        # =========================================================

        if forensic_score >= 40:

            forensic_level = "Strong"

        elif forensic_score >= 20:

            forensic_level = "Moderate"

        elif forensic_score > 0:

            forensic_level = "Weak"

        else:

            forensic_level = "None"

        # =========================================================
        # AI SCORE INTERPRETATION
        #
        # V4 is an uncalibrated model score.
        # It is NOT a probability.
        # =========================================================

        if ai_score >= 70:

            ai_level = "High"

        elif ai_score >= 40:

            ai_level = "Moderate"

        else:

            ai_level = "Low"

        # =========================================================
        # FINAL RISK ASSESSMENT
        #
        # AI detection is the primary signal.
        # Forensic analysis provides supporting context.
        # =========================================================

        if ai_score >= 70:

            if forensic_score >= 20:

                risk = "HIGH"

                assessment = (
                    "The AI detector produced a high synthetic-media "
                    "score and additional contextual forensic indicators "
                    "were identified."
                )

                findings.append(
                    "AI assessment is supported by additional "
                    "forensic/contextual indicators"
                )

            else:

                risk = "MEDIUM"

                assessment = (
                    "The AI detector produced a high synthetic-media "
                    "score, but independent forensic support is limited."
                )

                findings.append(
                    "High AI score detected, but supporting forensic "
                    "evidence is limited"
                )

        elif ai_score >= 40:

            if forensic_score >= 20:

                risk = "MEDIUM"

                assessment = (
                    "The image produced a moderate synthetic-media "
                    "score with additional forensic/contextual indicators."
                )

                findings.append(
                    "Moderate AI indicators have supporting "
                    "forensic/contextual signals"
                )

            else:

                risk = "MEDIUM"

                assessment = (
                    "The AI detector produced a moderate synthetic-media "
                    "score. The available forensic analysis is inconclusive."
                )

                findings.append(
                    "AI assessment is moderate and forensic evidence "
                    "is inconclusive"
                )

        else:

            if forensic_score >= 20:

                risk = "LOW"

                assessment = (
                    "The AI detector produced a low synthetic-media "
                    "score, although some contextual forensic indicators "
                    "were identified."
                )

                findings.append(
                    "AI assessment is predominantly authentic, "
                    "but contextual indicators were detected"
                )

            else:

                risk = "LOW"

                assessment = (
                    "The AI detector produced a low synthetic-media "
                    "score and no significant supporting forensic "
                    "indicators were identified."
                )

                findings.append(
                    "No strong synthetic-media indicators were identified"
                )

        # =========================================================
        # AUTHENTICITY SCORE
        #
        # Presentation score only.
        # NOT a calibrated probability.
        # =========================================================

        authenticity_score = round(
            max(
                0,
                min(
                    100,
                    100 - ai_score
                )
            )
        )

        # =========================================================
        # AI FINDING
        # =========================================================

        if ai_score >= 70:

            findings.append(
                "AI detector produced a high synthetic-media score"
            )

        elif ai_score >= 40:

            findings.append(
                "AI detector produced a moderate synthetic-media score"
            )

        else:

            findings.append(
                "AI detector produced a low synthetic-media score"
            )

        # =========================================================
        # FORENSIC FINDING
        # =========================================================

        if forensic_score >= 40:

            findings.append(
                "Multiple contextual forensic indicators were identified"
            )

        elif forensic_score >= 20:

            findings.append(
                "Several supporting forensic indicators were identified"
            )

        elif forensic_score > 0:

            findings.append(
                "Limited contextual forensic indicators were identified"
            )

        else:

            findings.append(
                "No significant supporting forensic indicators were detected"
            )

        # =========================================================
        # TECHNICAL SUMMARY
        # =========================================================

        technical = {

            "width": width,

            "height": height,

            "format": image_format,

            "file_size": file_size,

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

            "has_exif":
                bool(exif_data),

            "has_software_metadata":
                "Software" in readable_exif,

            "resolution_indicator":
                int(
                    "low_resolution"
                    in forensic_indicators
                )
        }

        # =========================================================
        # FINAL RESULT
        # =========================================================

        return {

            "deepfake_probability":
                ai_score,

            "ai_fake_score":
                ai_score,

            "ai_score_type":
                "uncalibrated_model_score",

            "confidence":
                ai_level,

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

            "forensic_level":
                forensic_level,

            "forensic_indicators":
                forensic_indicators,

            "findings":
                findings,

            "metadata":
                metadata_findings,

            "technical":
                technical
        }

    # =============================================================
    # ERROR HANDLING
    # =============================================================

    except Exception as error:

        return {

            "deepfake_probability":
                0,

            "ai_fake_score":
                0,

            "ai_score_type":
                "error",

            "confidence":
                "Unavailable",

            "authenticity_score":
                0,

            "risk":
                "ERROR",

            "assessment":
                "Analysis failed",

            "ai_detection":
                [],

            "forensic_score":
                0,

            "forensic_level":
                "Unavailable",

            "forensic_indicators":
                [],

            "findings": [
                f"Analysis failed: {str(error)}"
            ],

            "metadata":
                [],

            "technical":
                {}
        }