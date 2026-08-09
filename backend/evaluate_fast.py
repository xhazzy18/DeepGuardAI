import os
from ai_detector import detect_ai_image
from ai_detector_v2 import detect_ai_image_v2
from ai_detector_v4 import detect_ai_image_v4


REAL_DIR = r".\test_dataset\real"
FAKE_DIR = r".\test_dataset\fake"

MAX_PER_CLASS = 100
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def get_images(folder):
    return sorted(
        [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(EXTENSIONS)
        ]
    )[:MAX_PER_CLASS]


def get_fake_score(results):

    for item in results:

        label = str(item.get("label", "")).lower()
        score = float(item.get("score", 0))

        if label in ("fake", "deepfake"):
            return score * 100

    return 0.0


real_images = get_images(REAL_DIR)
fake_images = get_images(FAKE_DIR)


models = {
    "V1": detect_ai_image,
    "V2": detect_ai_image_v2,
    "V4": detect_ai_image_v4
}


print()
print("========================================")
print("       DEEPGUARD MODEL EVALUATION")
print("========================================")
print()
print(f"REAL images: {len(real_images)}")
print(f"FAKE images: {len(fake_images)}")
print(f"TOTAL:       {len(real_images) + len(fake_images)}")
print()


for model_name, detector in models.items():

    print()
    print("========================================")
    print(f"TESTING {model_name}")
    print("========================================")

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    # ==============================
    # REAL
    # ==============================

    print("Testing REAL images...")

    for i, file_path in enumerate(real_images, 1):

        try:

            result = detector(file_path)

            fake_score = get_fake_score(result)

            predicted_fake = fake_score >= 50

            if predicted_fake:
                fp += 1
            else:
                tn += 1

            if i % 25 == 0:
                print(f"REAL: {i}/{len(real_images)}")

        except Exception as e:

            print(
                f"ERROR REAL: "
                f"{os.path.basename(file_path)}"
            )

    # ==============================
    # FAKE
    # ==============================

    print("Testing FAKE images...")

    for i, file_path in enumerate(fake_images, 1):

        try:

            result = detector(file_path)

            fake_score = get_fake_score(result)

            predicted_fake = fake_score >= 50

            if predicted_fake:
                tp += 1
            else:
                fn += 1

            if i % 25 == 0:
                print(f"FAKE: {i}/{len(fake_images)}")

        except Exception as e:

            print(
                f"ERROR FAKE: "
                f"{os.path.basename(file_path)}"
            )

    total = tp + tn + fp + fn

    accuracy = (tp + tn) / total if total else 0

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0
    )

    f1 = (
        2 * precision * recall /
        (precision + recall)
        if precision + recall
        else 0
    )

    print()
    print("----------------------------------------")
    print(f"{model_name} RESULTS")
    print("----------------------------------------")

    print(f"Accuracy:   {accuracy * 100:.2f}%")
    print(f"Precision:  {precision * 100:.2f}%")
    print(f"Recall:     {recall * 100:.2f}%")
    print(f"F1 Score:   {f1 * 100:.2f}%")

    print()
    print(f"TP: {tp}")
    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")

    print()

print("========================================")
print("          EVALUATION COMPLETE")
print("========================================")