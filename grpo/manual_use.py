from grpo.grpo_dataset_generation import INSTRUCTION

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


BASE = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER = "grpo_eclipse/interrupted"

print ("printing LoRA weights to check whether tehre is actual training. Value should be greater than 0")
import safetensors.torch as st
w = st.load_file("grpo_eclipse/interrupted/adapter_model.safetensors")
for k, v in w.items():
    if "lora_B" in k:
        print(k, v.abs().max().item())
        break

tok = AutoTokenizer.from_pretrained(BASE)
model = AutoModelForCausalLM.from_pretrained(
    BASE,
    device_map="auto",
    quantization_config=BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    ),
    dtype=torch.float16,
    attn_implementation="sdpa",
)
model = PeftModel.from_pretrained(model, ADAPTER)
model.eval()


def predict(battle_text, max_new_tokens=200):
    messages = [
        {"role": "system", "content": INSTRUCTION},
        {"role": "user", "content": battle_text},
    ]
    inputs = tok.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    return tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

if __name__ == "__main__":
    battle = ("1 ship with 0 initiative, 1 hit chance, 1 hull and 1 small canon "
              "VS 1 ship with 4 initiative, 2 hull, 1 hit chance and 1 small canon.")
    print (battle)
    print ("base model output: ")
    with model.disable_adapter():
        print("base   :", predict(battle))
    print ("trained model output: ")
    print(predict(battle))