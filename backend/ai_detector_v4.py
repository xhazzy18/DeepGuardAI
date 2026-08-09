from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_NAME = "prithivMLmods/Deep-Fake-Detector-v2-Model"

print("Loading DeepGuard AI V4 model...")

processor = AutoImageProcessor.from_pretrained(
    MODEL_NAME
)

model = AutoModelForImageClassification.from_pretrained(
    MODEL_NAME
)

model.eval()

print("DeepGuard AI V4 model loaded successfully.")
print("Labels:", model.config.id2label)


def detect_ai_image_v4(file_path: str):

    image = Image.open(file_path).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )[0]

    results = []

    for index, probability in enumerate(probabilities):

        results.append({
            "label": model.config.id2label[index],
            "score": round(
                float(probability),
                4
            )
        })

    return results