from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification


MODEL_NAME = "prithivMLmods/deepfake-detector-model-v1"


print("Loading DeepGuard AI model...")


processor = AutoImageProcessor.from_pretrained(
    MODEL_NAME
)

model = AutoModelForImageClassification.from_pretrained(
    MODEL_NAME
)

model.eval()


print("DeepGuard AI model loaded successfully.")


def detect_ai_image(file_path: str):

    image = Image.open(
        file_path
    ).convert("RGB")


    inputs = processor(
        images=image,
        return_tensors="pt"
    )


    with torch.no_grad():

        outputs = model(
            **inputs
        )

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )[0]


    results = []


    for index, probability in enumerate(
        probabilities
    ):

        label = model.config.id2label[index]

        results.append({

            "label": label,

            "score": round(
                float(probability),
                4
            )

        })


    return results