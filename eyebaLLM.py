from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import json


model_id = "Qwen/Qwen2.5-7B-Instruct"
tok = AutoTokenizer.from_pretrained(model_id)
quant_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    quantization_config=quant_config,
    dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
)


val = [json.loads(l) for l in open("datasets/reasonning_traces.jsonl")]
messages = val[0]["messages"][:1]
text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tok(text, return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=600)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
print("EXPECTED:\n", val[0]["messages"][1]["content"])

instruction = "Your goal is to predict outcomes of battles in the boardgame Eclipse. "
rules = open("eclipse_battle_rules_simplified.txt", "r").read()
battle = "How do you think the following battle will go? 1 cruiser with 2 initiative, 1 computer, 1 hull and 1 yellow canon VS 1 starbase with 4 initiative, 2 hull, 1 computer and 1 yellow canon. I want a short paragraph of reasoning and a numerical probability at the end. "

prompt = instruction + "\n" + rules + "\n" + battle + "\n"



inputs = tok(prompt, return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=1000)
print(tok.decode(out[0]))