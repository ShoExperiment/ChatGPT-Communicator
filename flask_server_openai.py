from flask import Flask, request, jsonify
import openai
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def index():
    return "Flask server is running! Use the /chatgpt endpoint for API calls."



@app.route('/chatgpt', methods=['POST'])
@cross_origin()

def chatgpt():
    try:
        data = request.json
        print(f"Received data: {data}")

        #prompt = data.get('prompt')
        messages = data.get('messages')
        mode = data.get('mode', "gpt-3.5-turbo")
        temperature = data.get('temperature', 0.7)  # default value
        max_tokens = data.get('max_tokens', 300)  # default value,,
        top_p = data.get('top_p', 0)  # default value,
        frequency_penalty = data.get('frequency_penalty', 0)  # default value
        presence_penalty = data.get('presence_penalty', 0)  # default value

        #print(f"Prompt received: {prompt}")
        print(f"Messages received: {messages}")
        print(f"Mode selected: {mode}")
        print(f"Temperature: {temperature}")
        print(f"Max Tokens: {max_tokens}")
        print(f"Top P: {top_p}")
        print(f"Frequency penalty: {frequency_penalty}")
        print(f"Presence penalty: {presence_penalty}")

        response = openai.ChatCompletion.create(
            model=mode,
            messages=messages,
            #messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        chatgpt_response = response.choices[0]["message"]["content"].strip()
        print(f"Response from ChatGPT: {chatgpt_response}")
        
        return jsonify({"response": chatgpt_response})
    except Exception as e:
        print("Error in Flask server:", e)
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
