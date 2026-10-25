import torch
from datasets import load_from_disk
from peft import LoraConfig
from transformers import BitsAndBytesConfig
from trl import GRPOConfig, GRPOTrainer
from reward import format_reward, accuracy_reward

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"   # move to 3B/7B once this works

ds = load_from_disk("datasets/grpo_train")

cfg = GRPOConfig(
    output_dir="grpo_eclipse",
    learning_rate=1e-5,
    num_generations=4,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=1,
    max_completion_length=200,
    beta=0.04,
    bf16=False,
    fp16=True,
    logging_steps=10,
    save_steps=200,
    max_steps=50,
    reward_weights=[0.2, 1.0],
    model_init_kwargs={
        "quantization_config": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        ),
        "dtype": torch.float16,
        "attn_implementation": "sdpa",
    },
)

trainer = GRPOTrainer(
    model=MODEL_ID,
    args=cfg,
    train_dataset=ds,
    reward_funcs=[format_reward, accuracy_reward],
    peft_config=LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules="all-linear",
        task_type="CAUSAL_LM",
    ),
)

# fp16 AMP needs trainable params in fp32
for p in trainer.model.parameters():
    if p.requires_grad:
        p.data = p.data.float()

print("all dtypes:", {p.dtype for p in trainer.model.parameters()})
print("trainable dtypes:", {p.dtype for p in trainer.model.parameters() if p.requires_grad})

trainer.train()
trainer.save_model("grpo_eclipse/final")