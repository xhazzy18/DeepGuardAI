import os
from ai_detector import detect_ai_image

REAL_DIR = r".\test_dataset\real"
FAKE_DIR = r".\test_dataset\fake"

THRESHOLD = 50

results = []

def test_folder(folder, actual_label):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if not os.path.isfile(file_path):
            continue

        if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        try:
            predictions = detect_ai_image(file_path)

            fake_score = 0

            for item in predictions:
                if str(item["label"]).lower() == "fake":
                    fake_score = float(item["score"]) * 100

            predicted_label = "FAKE" if fake_score >= THRESHOLD else "REAL"

            correct = predicted_label == actual_label

            results.append({
                "file": filename,
                "actual": actual_label,
                "fake_score": fake_score,
                "predicted": predicted_label,
                "correct": correct
            })

        except Exception as error:
            print(f"ERROR: {filename}")
            print(error)


print("\n==============================")
print("   DEEPGUARD AI MODEL TEST")
print("==============================\n")

print("Testing REAL images...")
test_folder(REAL_DIR, "REAL")

print("\nTesting FAKE images...")
test_folder(FAKE_DIR, "FAKE")


print("\n==============================")
print("          RESULTS")
print("==============================\n")

for result in results:
    status = "CORRECT" if result["correct"] else "WRONG"

    print(
        f"{result['file']:<35} "
        f"Actual: {result['actual']:<5} "
        f"Fake: {result['fake_score']:>6.2f}% "
        f"Predicted: {result['predicted']:<5} "
        f"[{status}]"
    )


total = len(results)
correct = sum(r["correct"] for r in results)

accuracy = (correct / total * 100) if total else 0


# Confusion matrix
true_positive = sum(
    r["actual"] == "FAKE"
    and r["predicted"] == "FAKE"
    for r in results
)

true_negative = sum(
    r["actual"] == "REAL"
    and r["predicted"] == "REAL"
    for r in results
)

false_positive = sum(
    r["actual"] == "REAL"
    and r["predicted"] == "FAKE"
    for r in results
)

false_negative = sum(
    r["actual"] == "FAKE"
    and r["predicted"] == "REAL"
    for r in results
)


precision = (
    true_positive / (true_positive + false_positive) * 100
    if (true_positive + false_positive)
    else 0
)

recall = (
    true_positive / (true_positive + false_negative) * 100
    if (true_positive + false_negative)
    else 0
)

f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall)
    else 0
)


print("\n==============================")
print("       MODEL PERFORMANCE")
print("==============================")

print(f"Total images:       {total}")
print(f"Correct:            {correct}")
print(f"Incorrect:          {total - correct}")
print(f"Accuracy:           {accuracy:.2f}%")
print(f"Precision:          {precision:.2f}%")
print(f"Recall:             {recall:.2f}%")
print(f"F1 Score:           {f1:.2f}%")

print("\n==============================")
print("       CONFUSION MATRIX")
print("==============================")

print(f"True Positives:     {true_positive}")
print(f"True Negatives:     {true_negative}")
print(f"False Positives:    {false_positive}")
print(f"False Negatives:    {false_negative}")

print("\n==============================")
print("       INTERPRETATION")
print("==============================")

if accuracy >= 80:
    print("Model shows promising performance on this test set.")
elif accuracy >= 60:
    print("Model shows moderate performance and needs calibration.")
else:
    print("Model performance is poor on this test set.")

print("\nTest complete.")