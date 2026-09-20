from transformers import AutoModelForCausalLM, AutoTokenizer



prompt = "Your goal is to predict outcomes of battles in the boardgame Eclipse. "
rules = open("eclipse_battle_rules_simplified.txt", "r").read()
instruction = "How do you think the following battle will go? 1 cruiser with 2 initiative, 1 computer, 1 hull and 1 yellow canon VS 1 starbase with 4 initiative, 2 hull, 1 computer and 1 yellow canon. I want a short paragraph of reasoning and a numerical probability at the end. "

prompt= prompt + "\n" + rules + "\n" + instruction + "\n"

model_id = "Qwen/Qwen2.5-7B-Instruct"
tok = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", load_in_4bit=True)

inputs = tok(prompt, return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=1000)
print(tok.decode(out[0]))