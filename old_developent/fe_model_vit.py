import cv2
from transformers import ViTForImageClassification, AutoImageProcessor
from PIL import Image
import torch
from torchvision import transforms

# Load model
model = ViTForImageClassification.from_pretrained(
    "models/VIT/vit_stress_model",
    num_labels=2,
    local_files_only=True
)

# Manual image processing (if no preprocessor_config.json)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.5, 0.5, 0.5],  # ImageNet-compatible
        std=[0.5, 0.5, 0.5]
    )
])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not found ❌")
        break

    face = cv2.resize(frame, (224, 224))
    pil_img = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
    
    # Apply manual transform
    input_tensor = transform(pil_img).unsqueeze(0).to(device)

    # with torch.no_grad():
    #     outputs = model(pixel_values=input_tensor)
    #     pred = torch.argmax(outputs.logits, dim=1).item()

    with torch.no_grad():
        outputs = model(pixel_values=input_tensor)
        logits = outputs.logits
        print("Logits:", logits)
        pred = torch.argmax(logits, dim=1).item()

    print(f"Predicted stress level: {pred}")

    label = "STRESS" if pred == 1 else "NON-STRESS"
    cv2.putText(frame, label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    cv2.imshow("Stress Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
