import os
from ai_detector_v4 import detect_ai_image_v4


REAL_DIR = r".\test_dataset\real"
FAKE_DIR = r".\test_dataset\fake"


def get_images(folder):
    extensions = (".jpg", ".jpeg", ".png", ".webp")

    return sorted(
        [
            os.path.join(folder, file)
            for file in os.listdir(folder)
            if file.lower().endswith(extensions)
        ]
    )


real_images = get_images(REAL_DIR)
fake_images = get_images(FAKE_DIR)


correct = 0
total = 0

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0


print()
print("==============================")
print("   DEEPGUARD AI V4 TEST")
print("==============================")
print()

print("Testing REAL images...")
print()

for file_path in real_images:

    results = detect_ai_image_v4(file_path)

    fake_score = 0

    for item in results:

        if item["label"].lower() == "deepfake":

            fake_score = item["score"] * 100

    predicted_fake = fake_score >= 50

    filename = os.path.basename(file_path)

    if predicted_fake:

        prediction = "FAKE"
        false_positive += 1

    else:

        prediction = "REAL"
        true_negative += 1
        correct += 1

    total += 1

    print(
        f"{filename:<35}"
        f"Actual: REAL  "
        f"Fake: {fake_score:6.2f}% "
        f"Predicted: {prediction:<4} "
        f"[{'CORRECT' if not predicted_fake else 'WRONG'}]"
    )


print()
print("Testing FAKE images...")
print()

for file_path in fake_images:

    results = detect_ai_image_v4(file_path)

    fake_score = 0

    for item in results:

        if item["label"].lower() == "deepfake":

            fake_score = item["score"] * 100

    predicted_fake = fake_score >= 50

    filename = os.path.basename(file_path)

    if predicted_fake:

        prediction = "FAKE"
        true_positive += 1
        correct += 1

    else:

        prediction = "REAL"
        false_negative += 1

    total += 1

    print(
        f"{filename:<35}"
        f"Actual: FAKE  "
        f"Fake: {fake_score:6.2f}% "
        f"Predicted: {prediction:<4} "
        f"[{'CORRECT' if predicted_fake else 'WRONG'}]"
    )


accuracy = (
    correct / total
    if total
    else 0
)

precision = (
    true_positive /
    (true_positive + false_positive)
    if (true_positive + false_positive)
    else 0
)

recall = (
    true_positive /
    (true_positive + false_negative)
    if (true_positive + false_negative)
    else 0
)

f1 = (
    2 * precision * recall /
    (precision + recall)
    if (precision + recall)
    else 0
)


print()
print("==============================")
print("       MODEL PERFORMANCE")
print("==============================")
print()

print(f"Total images:       {total}")
print(f"Correct:            {correct}")
print(f"Incorrect:          {total - correct}")
print(f"Accuracy:           {accuracy * 100:.2f}%")
print(f"Precision:          {precision * 100:.2f}%")
print(f"Recall:             {recall * 100:.2f}%")
print(f"F1 Score:           {f1 * 100:.2f}%")

print()
print("==============================")
print("       CONFUSION MATRIX")
print("==============================")
print()

print(f"True Positives:     {true_positive}")
print(f"True Negatives:     {true_negative}")
print(f"False Positives:    {false_positive}")
print(f"False Negatives:    {false_negative}")

print()
print("Test complete.")