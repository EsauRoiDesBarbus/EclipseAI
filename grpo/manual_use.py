from grpo.grpo_dataset_generation import INSTRUCTION

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


BASE = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER = "grpo_eclipse/final"

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
    battle = ("1 cruiser with 2 initiative, 1 computer, 1 hull and 1 yellow canon "
              "VS 1 starbase with 4 initiative, 2 hull, 1 computer and 1 yellow canon.")
    print(predict(battle))