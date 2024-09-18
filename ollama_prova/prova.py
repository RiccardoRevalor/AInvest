from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.1")

response = llm.invoke("The first man on the moon was ...")
print(response)