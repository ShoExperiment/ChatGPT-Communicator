# **ChatGPT Communicator Plugin for Glyphs**

<img width="1235" alt="image" src="https://github.com/ShoExperiment/ChatGPT-Communicator/assets/131850635/53ddb4c5-d032-41c9-ac6f-a2571d2d34db">


## **Description**

This plugin, developed by Shotaro Nakano, aims to integrate the capabilities of GPT (Generative Pre-trained Transformer) into the Glyphs font editor. It uses a Flask server to send and receive prompts to a GPT model and brings the responses into Glyphs. The plugin can also manipulate the macro panel in Glyphs, allowing for a more integrated development experience.

## **Requirements**

Python 3  
Glyphs 3  
Flask Server running for GPT communication (flask_server_openai.py)  
OpenAI API key  

## **Fearures**

* **User and System Prompt Templates:** Predefined prompts for user and system.  
* **Model Selection:** Choose between different GPT models. You can set your own model. 
* **Parameter Tuning:** Adjust various parameters like temperature, max tokens, etc., using sliders.  
* **History & Iteration:** Maintain a history of prompts and responses for future reference. Also, this will be a number of attemps that Auto Pilot does.  
* **Auto Pilot:** Automatically automatically run GPT-generated Python code until success.  
* **Macro Panel Integration:** Load and save Python scripts from Glyphs' macro panel.  

## **Installation**
* Clone this repository or download the ZIP file.  

* Install nessesary python libraries.  
  Most likely you have to install followings:  
  `openai`    
  `flask`  
  `flask_cors`  
  They have to be installed in the Python environment of the server.  
  I felt that comminicating with GPT through the server is easier than directly commnicating with GPT.  

* Set your OPENAI API Key  
  Run Terminal and type  
  `export OPENAI_API_KEY="your key"`  
  or  
  Open flask_server_openai.py and change the following code  
  `openai.api_key = os.environ.get("OPENAI_API_KEY")`  
  to  
  `openai.api_key = "your key"`
  
* Run the server.  
  `Python3 your/location/flask_server_openai.py`
  

* Move the downloaded files to Glyphs' Plugins folder.
* Reload Glyphs to activate the plugin.

## **Usage**

### **Opening the Plugin**

* Once installed, the plugin can be accessed from the Glyphs' Window menu.  
* Clicking on it will open a dialog window.  
    
### **Setting Up**
    
* **System/User Prompts:** You can select a predefined template or input your own prompt.  
You can modify the prompt templates and set your own gpt model.  
`Right Click the plugin > Show Pakage Contents > Contents > Resources`  
Edit the text files in it.  
* **Model and Parameters:** Choose the GPT model and set parameters like temperature, max tokens, etc.
### **Running**
Click on the "Fetch" button to send the prompt to the GPT model. The received code will appear in a Responce. You can edit the received code and save or load scripts.  
  
The "Auto Pilot" feature can be used to run the model multiple times automatically until a generated python code run without error.  
The "Run Code" will excute python code in the Responce. The python code will be automatically extracted from the code.  
The check box of "Include texts in Responce field into Prompt" can be use when you want to put text in the Responce field. If you newly wirte a python code in the Responce field, open an existing python code or import a python code from Macro then you should use this option, because they are not in the conversation history.  
  
## **Macro Panel**
Click on "Import from Macro" to fetch the current Python code in the Macro panel.  
Use "Export to Macro" to send the generated code to the Macro panel.  

## **License**

This project is licensed under the MIT License.
