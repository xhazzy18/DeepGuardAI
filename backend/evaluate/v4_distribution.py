import sys
import os
import statistics

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from ai_detector_v4 import detect_ai_image_v4

BASE = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REAL_DIR = os.path.join(BASE, "test_dataset", "real")
FAKE_DIR = os.path.join(BASE, "test_dataset", "fake")


def get_fake_score(path):
    results = detect_ai_image_v4(path)

    for item in results:
        if item["label"].lower() == "deepfake":
            return item["score"] * 100

    return 0.0


def get_images(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]


real_images = get_images(REAL_DIR)
fake_images = get_images(FAKE_DIR)

print(f"REAL images: {len(real_images)}")
print(f"FAKE images: {len(fake_images)}")


real_scores = []
fake_scores = []


print("\nTesting REAL images...")

for i, path in enumerate(real_images, 1):
    score = get_fake_score(path)
    real_scores.append(score)

    if i % 25 == 0:
        print(f"REAL: {i}/{len(real_images)}")


print("\nTesting FAKE images...")

for i, path in enumerate(fake_images, 1):
    score = get_fake_score(path)
    fake_scores.append(score)

    if i % 25 == 0:
        print(f"FAKE: {i}/{len(fake_images)}")


print("\n" + "=" * 60)
print("V4 FAKE-SCORE DISTRIBUTION")
print("=" * 60)


def show_stats(name, scores):
    print(f"\n{name}")

    print(f"Minimum:  {min(scores):6.2f}%")
    print(f"Maximum:  {max(scores):6.2f}%")
    print(f"Average:  {statistics.mean(scores):6.2f}%")
    print(f"Median:   {statistics.median(scores):6.2f}%")

    print(
        f"Below 30%: "
        f"{sum(s < 30 for s in scores)}"
    )

    print(
        f"30-59%:   "
        f"{sum(30 <= s < 60 for s in scores)}"
    )

    print(
        f"60-79%:   "
        f"{sum(60 <= s < 80 for s in scores)}"
    )

    print(
        f"80%+:     "
        f"{sum(s >= 80 for s in scores)}"
    )


show_stats("REAL IMAGES", real_scores)
show_stats("FAKE IMAGES", fake_scores)


print("\n" + "=" * 60)
print("THRESHOLD CLASSIFICATION")
print("=" * 60)

for threshold in [30, 40, 50, 60, 70, 80]:

    real_correct = sum(
        s < threshold for s in real_scores
    )

    fake_correct = sum(
        s >= threshold for s in fake_scores
    )

    total = len(real_scores) + len(fake_scores)

    accuracy = (
        (real_correct + fake_correct)
        / total
        * 100
    )

    print(
        f"{threshold}% threshold -> "
        f"REAL correct: {real_correct}/{len(real_scores)} | "
        f"FAKE correct: {fake_correct}/{len(fake_scores)} | "
        f"Accuracy: {accuracy:.2f}%"
    )