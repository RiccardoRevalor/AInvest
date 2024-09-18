import os
from groq import Groq
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM

chat_history_cloud = []

def trim_chat_history(max_length=2000):
    global chat_history_cloud
    total_length = sum(len(msg["content"]) for msg in chat_history_cloud)
    
    while total_length > max_length:
        # Rimuovi il primo messaggio (il più vecchio)
        total_length -= len(chat_history_cloud[0]["content"])
        chat_history_cloud.pop(0)


def generateResponse(content, model="llama3-8b-8192", temperature=1):
    """
    function that generates a response to a given prompt using the Groq API

    Args:
    content: str, the prompt to generate a response to
    model: str, the model to use for generating the response, default is llama3-8b-8192
    temperature: float, the temperature to use for generating the response, default is 1

    Returns:
    res: str, the generated response
    """

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    #trim_chat_history()

    # Aggiungi il messaggio corrente alla storia
    #chat_history_cloud.append({"role": "user", "content": content})

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        #messages=chat_history_cloud,
        model=model,
        temperature=temperature
    )

    res = chat_completion.choices[0].message.content
    #chat_history_cloud.append({"role": "assistant", "content": res})

    return res

def revision(prompt, response, model="llama3-8b-8192", temperature=1):
    """
    This function takes a prompt and a response and generates a revision of the response
    The strategy is: at first, generate a plan for how to revise the response, then generate the revised response incorporating the plan

    Args:
    prompt: str, the prompt to generate a response to
    response: str, the response to revise
    model: str, the model to use for generating the response, default is llama3-8b-8192
    temperature: float, the temperature to use for generating the response, default is 1

    Returns:
    updatedPlan: str, the updated plan
    revision: str, the revised response
    """

    revisionPrompt = f"""
    You were given a task and your results are at the end. Self critique, find flaws in your plan and thought, and update the plan i.e tell me what would you change if you were given the opportunity again. Do not return a json, just your thoughts and reasoning.

    You were given a prompt.
    {prompt}

    Then you produced some results.
    {response}

    Now talk about why your response was not up to the mark. And discuss what you will change. Your plan should be at max one paragraph.
    """
    updatedPlan = generateResponse(revisionPrompt, model, temperature)

    # revise
    revisePrompt = f"""
    You produced some results.
    {response}

    But then someone provided you some critique on how to improve the results. Incorporate the critique into your plan. Return revised output.
    {updatedPlan}
    """
    revision = generateResponse(revisePrompt, model, temperature)
    return updatedPlan, revision


# Crea la memoria per tenere traccia della conversazione
memory = ConversationBufferMemory()

def generateResponseLocally(content, model="llama3.1"):
    llm = OllamaLLM(model=model)  
    #response = llm.invoke(content)


    # Definisci un template per la conversazione
    prompt_template = PromptTemplate(
        input_variables=["history", "input"], 
        template="History:\n{history}\n\nNew message:\n{input}\n"
    )

    # Crea una sequenza utilizzando il template e il modello
    conversation = prompt_template | llm

    # Prepara l'input per la conversazione (aggiungendo la memoria)
    input_with_memory = {
        "history": memory.load_memory_variables({})["history"],  # Carica la storia della conversazione
        "input": content
    }

    # Genera la risposta utilizzando la sequenza
    response = conversation.invoke(input_with_memory)

    # Aggiorna la memoria con il nuovo input
    memory.save_context({"input": content}, {"response": response})

    return response


