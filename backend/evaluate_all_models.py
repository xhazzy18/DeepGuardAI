import os
from collections import defaultdict

from ai_detector import detect_ai_image
from ai_detector_v2 import detect_ai_image_v2
from ai_detector_v4 import detect_ai_image_v4


REAL_DIR = r".\test_dataset\real"
FAKE_DIR = r".\test_dataset\fake"

MAX_PER_CLASS = 960

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def get_images(folder):
    return sorted(
        [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(EXTENSIONS)
        ]
    )[:MAX_PER_CLASS]


real_images = get_images(REAL_DIR)
fake_images = get_images(FAKE_DIR)


print()
print("========================================")
print("       DEEPGUARD MODEL COMPARISON")
print("========================================")
print()
print(f"REAL images: {len(real_images)}")
print(f"FAKE images: {len(fake_images)}")
print(f"TOTAL:       {len(real_images) + len(fake_images)}")
print()


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


models = {

    "V1": detect_ai_image,

    "V2": detect_ai_image_v2,

    "V4": detect_ai_image_v4

}


results = defaultdict(
    lambda: {
        "correct": 0,
        "total": 0,
        "tp": 0,
        "tn": 0,
        "fp": 0,
        "fn": 0
    }
)


for model_name, detector in models.items():

    print()
    print("----------------------------------------")
    print(f"Testing {model_name}")
    print("----------------------------------------")

    for file_path in real_images:

        try:

            output = detector(file_path)

            fake_score = get_fake_score(output)

            predicted_fake = fake_score >= 50

            results[model_name]["total"] += 1

            if predicted_fake:

                results[model_name]["fp"] += 1

            else:

                results[model_name]["tn"] += 1
                results[model_name]["correct"] += 1

        except Exception as error:

            print(
                f"ERROR: {file_path}"
            )

    for file_path in fake_images:

        try:

            output = detector(file_path)

            fake_score = get_fake_score(output)

            predicted_fake = fake_score >= 50

            results[model_name]["total"] += 1

            if predicted_fake:

                results[model_name]["tp"] += 1
                results[model_name]["correct"] += 1

            else:

                results[model_name]["fn"] += 1

        except Exception as error:

            print(
                f"ERROR: {file_path}"
            )


print()
print()
print("========================================")
print("             FINAL RESULTS")
print("========================================")
print()


for model_name in models:

    r = results[model_name]

    accuracy = (
        r["correct"] / r["total"]
        if r["total"]
        else 0
    )

    precision = (
        r["tp"] /
        (r["tp"] + r["fp"])
        if (r["tp"] + r["fp"])
        else 0
    )

    recall = (
        r["tp"] /
        (r["tp"] + r["fn"])
        if (r["tp"] + r["fn"])
        else 0
    )

    f1 = (
        2 * precision * recall /
        (precision + recall)
        if (precision + recall)
        else 0
    )

    print(f"{model_name}")
    print("-" * 40)

    print(
        f"Accuracy:   {accuracy * 100:.2f}%"
    )

    print(
        f"Precision:  {precision * 100:.2f}%"
    )

    print(
        f"Recall:     {recall * 100:.2f}%"
    )

    print(
        f"F1 Score:   {f1 * 100:.2f}%"
    )

    print()

    print(
        f"TP: {r['tp']}  "
        f"TN: {r['tn']}  "
        f"FP: {r['fp']}  "
        f"FN: {r['fn']}"
    )

    print()