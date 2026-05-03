from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_groq(question, context):
    prompt = f"""You are an intelligent document assistant.
Answer the question based only on the context provided below.
If the answer is not found in the context, politely say "This information was not found in the document."

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.7
    )

    return response.choices[0].message.content