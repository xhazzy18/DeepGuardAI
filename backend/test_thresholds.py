from PIL import Image
import glob
import os
from transformers import pipeline

MODEL = "umm-maybe/AI-image-detector"

detector = pipeline(
    "image-classification",
    model=MODEL
)

real_files = glob.glob(r"test_dataset\real\*")
fake_files = glob.glob(r"test_dataset\fake\*")

results = []

print(f"REAL images: {len(real_files)}")
print(f"FAKE images: {len(fake_files)}")
print("\nAnalyzing images...\n")

def artificial_score(path):
    image = Image.open(path).convert("RGB")
    predictions = detector(image)

    for p in predictions:
        if p["label"].lower() == "artificial":
            return p["score"]

    return 0.0


for i, path in enumerate(real_files, 1):
    score = artificial_score(path)
    results.append((score, 0))

    if i % 50 == 0:
        print(f"REAL: {i}/{len(real_files)}")


for i, path in enumerate(fake_files, 1):
    score = artificial_score(path)
    results.append((score, 1))

    if i % 50 == 0:
        print(f"FAKE: {i}/{len(fake_files)}")


print("\n" + "=" * 70)
print("THRESHOLD ANALYSIS")
print("=" * 70)

thresholds = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
]

best = None

for threshold in thresholds:

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for score, actual in results:

        predicted = 1 if score >= threshold else 0

        if actual == 1 and predicted == 1:
            tp += 1

        elif actual == 0 and predicted == 0:
            tn += 1

        elif actual == 0 and predicted == 1:
            fp += 1

        elif actual == 1 and predicted == 0:
            fn += 1

    total = tp + tn + fp + fn

    accuracy = (tp + tn) / total if total else 0

    precision = tp / (tp + fp) if (tp + fp) else 0

    recall = tp / (tp + fn) if (tp + fn) else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    print(
        f"Threshold {threshold:.2f} | "
        f"Accuracy {accuracy:.3f} | "
        f"Precision {precision:.3f} | "
        f"Recall {recall:.3f} | "
        f"F1 {f1:.3f}"
    )

    if best is None or f1 > best["f1"]:
        best = {
            "threshold": threshold,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }


print("\n" + "=" * 70)
print("BEST THRESHOLD")
print("=" * 70)

print(f"Threshold : {best['threshold']:.2f}")
print(f"Accuracy  : {best['accuracy']:.3f}")
print(f"Precision : {best['precision']:.3f}")
print(f"Recall    : {best['recall']:.3f}")
print(f"F1 Score  : {best['f1']:.3f}")