import sys
import os
import numpy as np

# Allow importing modules from the backend directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, BASE_DIR)

from ai_detector_v2 import detect_ai_image_v2


REAL_DIR = os.path.join(
    BASE_DIR,
    "test_dataset",
    "real"
)

FAKE_DIR = os.path.join(
    BASE_DIR,
    "test_dataset",
    "fake"
)


def get_images(folder):

    extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    )

    files = []

    for root, _, names in os.walk(folder):

        for name in names:

            if name.lower().endswith(extensions):

                files.append(
                    os.path.join(
                        root,
                        name
                    )
                )

    return sorted(files)


def get_fake_score(path):

    results = detect_ai_image_v2(path)

    for item in results:

        label = str(
            item.get("label", "")
        ).lower()

        if label == "fake":

            return (
                float(
                    item.get("score", 0)
                ) * 100
            )

    return 0.0


# =========================================================
# LOAD DATASET
# =========================================================

real_images = get_images(
    REAL_DIR
)

fake_images = get_images(
    FAKE_DIR
)


print("=" * 60)
print("DEEPGUARD AI V2 FULL DATASET EVALUATION")
print("=" * 60)

print(
    f"REAL images: {len(real_images)}"
)

print(
    f"FAKE images: {len(fake_images)}"
)

print(
    f"TOTAL:       "
    f"{len(real_images) + len(fake_images)}"
)


real_scores = []
fake_scores = []


# =========================================================
# REAL IMAGES
# =========================================================

print("\nTesting REAL images...")


for i, path in enumerate(
    real_images,
    1
):

    try:

        score = get_fake_score(
            path
        )

        real_scores.append(
            score
        )

    except Exception as e:

        print(
            f"Error: {path}"
        )

        print(e)

    if (
        i % 25 == 0
        or i == len(real_images)
    ):

        print(
            f"REAL: "
            f"{i}/{len(real_images)}"
        )


# =========================================================
# FAKE IMAGES
# =========================================================

print("\nTesting FAKE images...")


for i, path in enumerate(
    fake_images,
    1
):

    try:

        score = get_fake_score(
            path
        )

        fake_scores.append(
            score
        )

    except Exception as e:

        print(
            f"Error: {path}"
        )

        print(e)

    if (
        i % 25 == 0
        or i == len(fake_images)
    ):

        print(
            f"FAKE: "
            f"{i}/{len(fake_images)}"
        )


real_scores = np.array(
    real_scores
)

fake_scores = np.array(
    fake_scores
)


# =========================================================
# SAFETY CHECK
# =========================================================

if len(real_scores) == 0:

    raise RuntimeError(
        "No REAL images were successfully evaluated."
    )

if len(fake_scores) == 0:

    raise RuntimeError(
        "No FAKE images were successfully evaluated."
    )


# =========================================================
# DISTRIBUTION
# =========================================================

print(
    "\n" + "=" * 60
)

print(
    "V2 FAKE-SCORE DISTRIBUTION"
)

print(
    "=" * 60
)


print("\nREAL IMAGES")

print(
    f"Minimum:   "
    f"{real_scores.min():7.2f}%"
)

print(
    f"Maximum:   "
    f"{real_scores.max():7.2f}%"
)

print(
    f"Average:   "
    f"{real_scores.mean():7.2f}%"
)

print(
    f"Median:    "
    f"{np.median(real_scores):7.2f}%"
)

print(
    f"Below 30%: "
    f"{np.sum(real_scores < 30)}"
)

print(
    f"30-59%:    "
    f"{np.sum((real_scores >= 30) & (real_scores < 60))}"
)

print(
    f"60-79%:    "
    f"{np.sum((real_scores >= 60) & (real_scores < 80))}"
)

print(
    f"80%+:      "
    f"{np.sum(fake_scores >= 80)}"
)


print("\nFAKE IMAGES")

print(
    f"Minimum:   "
    f"{fake_scores.min():7.2f}%"
)

print(
    f"Maximum:   "
    f"{fake_scores.max():7.2f}%"
)

print(
    f"Average:   "
    f"{fake_scores.mean():7.2f}%"
)

print(
    f"Median:    "
    f"{np.median(fake_scores):7.2f}%"
)

print(
    f"Below 30%: "
    f"{np.sum(fake_scores < 30)}"
)

print(
    f"30-59%:    "
    f"{np.sum((fake_scores >= 30) & (fake_scores < 60))}"
)

print(
    f"60-79%:    "
    f"{np.sum((fake_scores >= 60) & (fake_scores < 80))}"
)

print(
    f"80%+:      "
    f"{np.sum(fake_scores >= 80)}"
)


# =========================================================
# THRESHOLD CLASSIFICATION
# =========================================================

print(
    "\n" + "=" * 60
)

print(
    "THRESHOLD CLASSIFICATION"
)

print(
    "=" * 60
)


total = (
    len(real_scores)
    + len(fake_scores)
)


for threshold in [
    30,
    40,
    50,
    60,
    70,
    80
]:

    # REAL should be below threshold
    real_correct = np.sum(
        real_scores < threshold
    )

    # FAKE should be at/above threshold
    fake_correct = np.sum(
        fake_scores >= threshold
    )

    accuracy = (
        (
            real_correct
            + fake_correct
        )
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


print(
    "\nEvaluation complete."
)