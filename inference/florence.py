import io
import base64
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import inference  # leave this here to make sure HF_HOME is set before model loads

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# torch.compile was tested but provides negligible speedup on CPU (~2.5s vs ~2.4s)
# while adding 73s+ startup cost for warmup compilation. Not worth it.
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-base-ft",
    torch_dtype=torch_dtype,
    trust_remote_code=True,
    forced_bos_token_id=0,
    attn_implementation="eager"   # ✅ IMPORTANT FIX
).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base-ft", trust_remote_code=True)

def infer(image_b64: str, task: str = "<CAPTION>") -> dict:
    image = Image.open(io.BytesIO(base64.b64decode(image_b64)))
    inputs = processor(text=task, images=image, return_tensors="pt").to(device, torch_dtype)
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=256,
        num_beams=1,
        do_sample=False,
        early_stopping=False
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    return processor.post_process_generation(generated_text, task=task, image_size=(image.width, image.height))
