from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# Cargar modelo y tokenizer
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("🔁 Cargando modelo... esto puede tardar un poco la primera vez")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)

# Crear el pipeline de chat
chat = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

# Bucle de conversación
print("✅ Listo! Escribí algo para hablar con TinyLlama. (Escribí 'salir' para terminar)\n")

while True:
    user_input = input("🧍 Tú: ")

    if user_input.lower() in ["salir", "exit", "quit"]:
        print("👋 Chau! Hasta la próxima.")
        break

    response = chat(f"<|user|>\n{user_input}\n<|assistant|>\n", max_new_tokens=150, do_sample=True, temperature=0.7, top_p=0.9)
    print("🤖 CL4P-TP:", response[0]["generated_text"].split("<|assistant|>\n")[-1].strip())
