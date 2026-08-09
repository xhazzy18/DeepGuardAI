import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import os

from ai_detector_v2 import detect_ai_image_v2
from ai_detector_v4 import detect_ai_image_v4


REAL_DIR = r".\test_dataset\real"
FAKE_DIR = r".\test_dataset\fake"

MAX_PER_CLASS = 100
THRESHOLDS = [30, 40, 50, 60, 70, 80]


def get_images(folder):

    return sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        )
    ])[:MAX_PER_CLASS]


def get_fake_score(results):

    for item in results:

        label = str(
            item.get("label", "")
        ).lower()

        score = float(
            item.get("score", 0)
        )

        if label in ("fake", "deepfake"):

            return score * 100

    return 0.0


real_images = get_images(REAL_DIR)
fake_images = get_images(FAKE_DIR)

print()
print(f"REAL images: {len(real_images)}")
print(f"FAKE images: {len(fake_images)}")
print()


models = {
    "V2": detect_ai_image_v2,
    "V4": detect_ai_image_v4
}


for model_name, detector in models.items():

    print()
    print("=" * 60)
    print(f"MODEL: {model_name}")
    print("=" * 60)

    scores = []

    print("Testing REAL images...")

    for i, path in enumerate(real_images, 1):

        result = detector(path)

        fake_score = get_fake_score(result)

        scores.append(
            (fake_score, False)
        )

        if i % 25 == 0:
            print(f"REAL: {i}/{len(real_images)}")

    print("Testing FAKE images...")

    for i, path in enumerate(fake_images, 1):

        result = detector(path)

        fake_score = get_fake_score(result)

        scores.append(
            (fake_score, True)
        )

        if i % 25 == 0:
            print(f"FAKE: {i}/{len(fake_images)}")

    print()

    for threshold in THRESHOLDS:

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for fake_score, actual_fake in scores:

            predicted_fake = (
                fake_score >= threshold
            )

            if actual_fake and predicted_fake:
                tp += 1

            elif actual_fake and not predicted_fake:
                fn += 1

            elif not actual_fake and predicted_fake:
                fp += 1

            else:
                tn += 1

        total = tp + tn + fp + fn

        accuracy = (
            (tp + tn) / total
            if total else 0
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp) else 0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn) else 0
        )

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if (precision + recall) else 0
        )

        print(
            f"Threshold {threshold}%  | "
            f"Accuracy: {accuracy * 100:6.2f}% | "
            f"Precision: {precision * 100:6.2f}% | "
            f"Recall: {recall * 100:6.2f}% | "
            f"F1: {f1 * 100:6.2f}% | "
            f"TP={tp} TN={tn} FP={fp} FN={fn}"
        )