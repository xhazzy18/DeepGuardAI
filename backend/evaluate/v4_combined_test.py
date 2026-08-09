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

from analyzer import analyze_image


BASE = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REAL_DIR = os.path.join(
    BASE,
    "test_dataset",
    "real"
)

FAKE_DIR = os.path.join(
    BASE,
    "test_dataset",
    "fake"
)


def get_images(folder):

    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        )
    ]


def get_combined_score(path):

    result = analyze_image(path)

    ai_score = float(
        result.get("ai_fake_score", 0)
    )

    forensic_score = float(
        result.get("forensic_score", 0)
    )

    # AI model remains the primary signal.
    # Forensics provide supporting evidence only.

    combined_score = (
        ai_score * 0.80
        +
        forensic_score * 0.20
    )

    return ai_score, forensic_score, combined_score


real_images = get_images(REAL_DIR)
fake_images = get_images(FAKE_DIR)

print(f"REAL images: {len(real_images)}")
print(f"FAKE images: {len(fake_images)}")


real_scores = []
fake_scores = []


print("\nTesting REAL images...")

for i, path in enumerate(real_images, 1):

    ai_score, forensic_score, combined = (
        get_combined_score(path)
    )

    real_scores.append(
        combined
    )

    if i % 25 == 0:

        print(
            f"REAL: {i}/{len(real_images)}"
        )


print("\nTesting FAKE images...")

for i, path in enumerate(fake_images, 1):

    ai_score, forensic_score, combined = (
        get_combined_score(path)
    )

    fake_scores.append(
        combined
    )

    if i % 25 == 0:

        print(
            f"FAKE: {i}/{len(fake_images)}"
        )


print("\n" + "=" * 60)
print("V4 + FORENSIC COMBINED SCORE")
print("=" * 60)


print("\nREAL IMAGES")

print(
    f"Average: "
    f"{sum(real_scores) / len(real_scores):.2f}%"
)

print(
    f"Median:  "
    f"{sorted(real_scores)[len(real_scores)//2]:.2f}%"
)


print("\nFAKE IMAGES")

print(
    f"Average: "
    f"{sum(fake_scores) / len(fake_scores):.2f}%"
)

print(
    f"Median:  "
    f"{sorted(fake_scores)[len(fake_scores)//2]:.2f}%"
)


print("\n" + "=" * 60)
print("COMBINED THRESHOLD CLASSIFICATION")
print("=" * 60)


for threshold in [30, 40, 50, 60, 70, 80]:

    real_correct = sum(
        score < threshold
        for score in real_scores
    )

    fake_correct = sum(
        score >= threshold
        for score in fake_scores
    )

    total = (
        len(real_scores)
        +
        len(fake_scores)
    )

    accuracy = (
        (real_correct + fake_correct)
        / total
        * 100
    )

    print(
        f"{threshold}% threshold -> "
        f"REAL correct: "
        f"{real_correct}/{len(real_scores)} | "
        f"FAKE correct: "
        f"{fake_correct}/{len(fake_scores)} | "
        f"Accuracy: "
        f"{accuracy:.2f}%"
    )