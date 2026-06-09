from litellm import completion

response = completion(
    model="ollama/qwen2.5:7b",
    messages=[
        {"role": "user", "content": "What is AI?"}
    ],
    api_base="http://localhost:11434",
    api_key="ollama",
    timeout=300
)

print(response["choices"][0]["message"]["content"])