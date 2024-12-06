from ollama import Client
from tabulate import tabulate

client = Client(host='http://localhost:11434')

def test_generate():
  response = client.generate(
    model = 'llama3.2', 
    prompt = "why is the sky blue?",
  )
  print(response)

def test_chat_stream():
  stream = client.chat(
    model='llama3.1',
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    stream=True,
  )

  for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)

def test_embed():
  response = client.embed(
    # model='nomic-embed-text',
    model='all-minilm',
    input='This is a test',
  )
  import numpy as np
  print(np.array(response['embeddings']).shape)

def test_list_models():
  response = client.list()
  data = {
    'Model': [model.model for model in response.models],
    'Size': [f"{model.size / 1e9:.2f}GB" for model in response.models],
  }
  print(tabulate(data, headers='keys'))

if __name__ == '__main__':
  # test_generate()
  # test_chat_stream()
  # test_embed()
  test_list_models()

# python scripts\demo_ollama.py