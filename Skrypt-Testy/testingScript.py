import json
import subprocess

# Odczytaj zawartość pliku rozmowy.json
with open('rozmowy.json', 'r') as file:
    data = json.load(file)

# Funkcja do wysyłania pojedynczej konwersacji na serwer
def send_conversation(conversation):
    messages = []
    for msg in conversation['message']:
        messages.append({
            "content": msg["content"],
            "role": msg["role"]
        })

    data_to_send = json.dumps(messages)

    curl_command = [
        'curl',
        '-X', 'POST',
        'https://localhost:7019/LLMResponseAdvanced',
        '-H', 'accept: text/plain',
        '-H', 'Content-Type: application/json',
        '-d', data_to_send
    ]

    try:
        subprocess.run(curl_command, check=True)
        print("Wysłano konwersację na serwer.")
    except subprocess.CalledProcessError as e:
        print("Błąd podczas wysyłania konwersacji na serwer:", e)

# Iteracja przez wszystkie konwersacje i wysłanie ich na serwer
for conversation in data:
    send_conversation("ANSERW",conversation)