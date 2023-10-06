# encoding: utf-8

###########################################################################################################
#
#
#	ChatGPT Communicator
#   By Shotaro Nakano TypeDesigner@Jiyukobo
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import subprocess
import json
import os
import re
#To process text strings
from Foundation import NSString
from Foundation import NSAttributedString
from Cocoa import NSSavePanel, NSUTF8StringEncoding
from Cocoa import NSOpenPanel, NSFileHandlingPanelOKButton
from AppKit import NSApp

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

class ChatGPTCommunicator(GeneralPlugin):

	# Definitions of IBOutlets

	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()

	#System
	systemPromptText = objc.IBOutlet()

	#system prompt popup
	systemPromptPupupButton = objc.IBOutlet()

	#Response
	responseText = objc.IBOutlet()

	#User Prompt
	userPromptText = objc.IBOutlet()

	#User prompt popup
	userPromptPupupButton = objc.IBOutlet()

	#Model selection
	modelSelected = objc.IBOutlet()

	#Temperature value
	temperatureText = objc.IBOutlet()
	#Temperature Slider
	temperatureSlider = objc.IBOutlet()

	#Maximum Length value
	maximumLengthText = objc.IBOutlet()
	#Temperature Slider
	maximumLengthSlider = objc.IBOutlet()

	#Top P value
	topPText = objc.IBOutlet()
	#Top P Slider
	topPSlider = objc.IBOutlet()

	#Frequency penalty value
	frequencyPenaltyText = objc.IBOutlet()
	#Frequency Slider
	frequencyPenaltySlider = objc.IBOutlet()

	#Presence penalty value
	presencePenaltyText = objc.IBOutlet()
    #Presence Slider
	presencePenaltySlider = objc.IBOutlet()

	#History/Itaration
	HistoryIterationPupupButton = objc.IBOutlet()

	#Include Response to prompt checkbutton
	includeReponceToPromptCheckButtom = objc.IBOutlet()

	#Defalt Setting of Parameter
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.modelSelection", "gpt-3.5-turbo")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.temperatureValue", 1.0)
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.maxTokensValue", 300)
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.topPValue", 1.0)
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.frequencyPenaltyValue", 0.0)
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.presencePenaltyValue", 0.0)
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.historyIteration", "1")
	#Default System Prompts
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt", "You are an apple")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_01", "You are font enginner")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_02", "You are genius")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_03", "")
	#Default System Prompts
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_01", "Write Python script for Glyphs 3 App")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_02", "Tell me how to use Glyphs 3 App: ")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_03", "")

	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.Response", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPrompt", "You are a helpful assistant.")
 
 	#History
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist0", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist1", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist2", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist3", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist4", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.Response_Hist0", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.Response_Hist1", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.Response_Hist2", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.Response_Hist3", "")
	Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.Response_Hist4", "")

	#Error message after an excution of a code
	error_message = ""
	#for server
	server_process = None

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'ChatGPT Communicator'
			})
		
		#Word on Run Button
		self.actionButtonLabel = Glyphs.localize({
			'en': 'Apply',
			})
		#Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
        
	#On dialog show
	@objc.python_method
	def start(self):
		self.responseText.setAutomaticQuoteSubstitutionEnabled_(False)
		self.clearHistory()
		self.initiateParameters()
		self.loadTemplates()
		self.initiatePromptTemplate()
		newMenuItem = NSMenuItem(self.name, self.showWindow_)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)

	def showWindow_(self, sender):
		window = self.dialog.window()
		window.makeKeyAndOrderFront_(self)

	def clearHistory(self):
		for i in reversed(range(0, 5)):
			#Clear user prompts and Responses
			Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i}"] = ""
			Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i}"] = ""

	def initiateParameters(self):
		#Initialize
		self.setMaxLengthValue_(None)
		self.setTemperatureValue_(None)
		self.setFrequencyPenaltyValue_(None)
		self.setPresencePenaltyValue_(None)
		self.setTopPValue_(None)
		self.setModel_(None)

	def initiatePromptTemplate(self):
		self.setPromptTemplate_(None)
		self.setSystemPromptTemplate_(None)

	def loadTemplates(self):
		#Function to read file content
		def read_file_content(file_name):
			with open(file_name, "r") as f:
				return f.read()

		#Get the current script's directory
		current_directory = os.path.dirname(os.path.realpath(__file__))

		#Build paths to the text files
		path_to_file_01 = os.path.join(current_directory, "SystemPromptTemplate01.txt")
		path_to_file_02 = os.path.join(current_directory, "SystemPromptTemplate02.txt")
		path_to_file_03 = os.path.join(current_directory, "SystemPromptTemplate03.txt")

		path_to_file_04 = os.path.join(current_directory, "UserPromptTemplate01.txt")
		path_to_file_05 = os.path.join(current_directory, "UserPromptTemplate02.txt")
		path_to_file_06 = os.path.join(current_directory, "UserPromptTemplate03.txt")

		#Read the content from the text files
		content_01 = read_file_content(path_to_file_01)
		content_02 = read_file_content(path_to_file_02)
		content_03 = read_file_content(path_to_file_03)
		content_04 = read_file_content(path_to_file_04)
		content_05 = read_file_content(path_to_file_05)
		content_06 = read_file_content(path_to_file_06)

		#Register the content to Glyphs defaults
		Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_01", content_01)
		Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_02", content_02)
		Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_03", content_03)
		Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_01", content_04)
		Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_02", content_05)
		Glyphs.registerDefault("com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_03", content_06)

	#Open a file
	@objc.IBAction
	def openPythonFile_(self, sender):
		#Create and configure the open panel
		openPanel = NSOpenPanel.openPanel()
		openPanel.setTitle_("Choose a Python script to open")
		openPanel.setCanChooseFiles_(True)
		openPanel.setCanChooseDirectories_(False)
		openPanel.setAllowsMultipleSelection_(False)
		openPanel.setAllowedFileTypes_(['py'])

		#Display the panel and check the user action
		if openPanel.runModal() == NSFileHandlingPanelOKButton:
			# Get the selected file URL
			file_url = openPanel.URLs()[0]
			file_path = file_url.path()

		#Read the file and put its contents into responseText
		try:
			with open(file_path, 'r', encoding='utf-8') as f:
				file_content = f.read()

			#Get the NSTextStorage object from the NSTextView
			text_storage = self.responseText.textStorage()
			#Clear any existing text
			text_storage.deleteCharactersInRange_((0, text_storage.length()))
			#Insert new text
			text_storage.appendAttributedString_(NSAttributedString.alloc().initWithString_(file_content))

			print(f"Script loaded from {file_path}")
		except Exception as e:
			print(f"Failed to load the script: {e}")

	#Add a title template to format the newly made script
	@objc.IBAction
	def setTitleTemplate_(self, sender):
		# Get the NSTextStorage object from the NSTextView
		text_storage = self.responseText.textStorage()

		#Create the title code string
		title_code = "#MenuTitle: The script title\n# -*- coding: utf-8 -*-\n__doc__ = \"\"\"\nWrite descriptions here.\n\"\"\"\n"
    
		#Convert title_code to NSAttributedString
		title_attributed_string = NSAttributedString.alloc().initWithString_(title_code)
    
		#Insert the title code at the beginning
		text_storage.insertAttributedString_atIndex_(title_attributed_string, 0)

 
 	#Save the newly made script
	@objc.IBAction
	def savePythonFile_(self, sender):
		#Fetch the text from responseText NSTextView
		text_storage = self.responseText.textStorage()
		text_to_save = text_storage.string()

		#Create and configure the save panel
		savePanel = NSSavePanel.savePanel()
		savePanel.setTitle_("Choose a location to save your Python script")
		savePanel.setCanCreateDirectories_(True)
		savePanel.setAllowedFileTypes_(['py'])
    
		#Display the panel and check the user action
		if savePanel.runModal() == 1:
			# Get the selected path
			file_path = savePanel.URL().path()

			#Save the text to the file
			try:
				with open(file_path, 'w', encoding='utf-8') as f:
					f.write(text_to_save)
				print(f"Script saved to {file_path}")
			except Exception as e:
				print(f"Failed to save the script: {e}")

	#Set a System prompt template
	@objc.IBAction
	def setSystemPromptTemplate_(self, sender):

		#Get the selected index from the popup button
		selected_index = self.systemPromptPupupButton.indexOfSelectedItem()

		#Create a key for the selected pre-made prompt
		selected_key = "com.ShotaroNakano.ChatGPTCommunicator.systemPrompt_{:02d}".format(selected_index + 1)

		#Retrieve the selected pre-made prompt
		selected_prompt = Glyphs.defaults[selected_key]

		#Update the UI element to display the selected prompt
		text_storage = self.systemPromptText.textStorage()
		text_storage.deleteCharactersInRange_((0, text_storage.length()))
		text_storage.appendAttributedString_(NSAttributedString.alloc().initWithString_(selected_prompt))

		#Update the stored current system prompt
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.systemPrompt"] = selected_prompt


	#Set a prompt template:
	@objc.IBAction
	def setPromptTemplate_(self, sender):
		#Get the selected index from the popup button
		selected_index = self.userPromptPupupButton.indexOfSelectedItem()

		#Create a key for the selected pre-made prompt
		selected_key = "com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate_{:02d}".format(selected_index + 1)

		#Retrieve the selected pre-made prompt
		selected_prompt = Glyphs.defaults[selected_key]

		#Update the stored current system prompt
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate"] = selected_prompt
		
	#Set a user imputed Prompt
	@objc.IBAction
	def setUserImputedPrompt_(self, sender):
		pass

	#Set a model
	@objc.IBAction
	def setModel_(self, sender):
		#Get the directory where the plugin.py file is located
		dir_path = os.path.dirname(os.path.realpath(__file__))

		#Create the full path to YourModelName.txt
		file_path = os.path.join(dir_path, "YourModelName.txt")


		#Get the selected index from the popup button
		#selected_index = self.modelSelected.indexOfSelectedItem()
		selected_index = int(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.historyIteration"])
 
		#Initialize the selected model variable
		selected_model = None
 
		#Map selected index to the corresponding model
		if selected_index == 0:
			selected_model = "gpt-3.5-turbo"
			Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.modelSelection"] = selected_model
		elif selected_index == 1:
			selected_model = "gpt-4"
			Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.modelSelection"] = selected_model
		elif selected_index == 2:
			# Read from 'YourModelName.txt' and get the model
			try:
				with open(file_path, "r") as f:
					selected_model = f.read().strip()

				#Remove extra spaces and line breaks
				selected_model = " ".join(selected_model.split())

				#Update the popup button's item title for index 2 (third item)
				self.modelSelected.itemAtIndex_(2).setTitle_(selected_model)

				#Update the stored current model
				Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.modelSelection"] = selected_model

			except FileNotFoundError:

				#Update the popup button's item title for index 2 (third item) to "No model"
				self.modelSelected.itemAtIndex_(2).setTitle_("Failed: gpt3.5")

				#Update the stored current model to a default value
				Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.modelSelection"] = "gpt-3.5-turbo"
		
	#Set temperature value
	@objc.IBAction
	def setTemperatureValue_(self, sender):
		#Read the current value from the slider
		slider_value = self.temperatureSlider.floatValue()
    
		#Update the text field
		updated_text = "Temp: {:.2f}".format(slider_value)
		self.temperatureText.setStringValue_(updated_text)
    
		#Update the stored value in Glyphs defaults
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.temperatureValue"] = slider_value

	#Set maximum length value
	@objc.IBAction
	def setMaxLengthValue_(self, sender):

		#Read the current value from the slider
		slider_value = int(self.maximumLengthSlider.floatValue())
    
		#Update the text field
		updated_text = f"Max length: {slider_value}"
		self.maximumLengthText.setStringValue_(updated_text)
    
		#Update the stored value in Glyphs defaults
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.maxTokensValue"] = slider_value

	#Set Top P Value
	@objc.IBAction
	def setTopPValue_(self, sender):
		#Read the current value from the slider
		slider_value = self.topPSlider.floatValue()
    
		#Update the text field
		updated_text = "Top P: {:.2f}".format(slider_value)
		self.topPText.setStringValue_(updated_text)
    
		#Update the stored value in Glyphs defaults
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.topPValue"] = slider_value

	#Set Frequency penalty Value
	@objc.IBAction
	def setFrequencyPenaltyValue_(self, sender):
		#Read the current value from the slider
		slider_value = self.frequencyPenaltySlider.floatValue()
    
		#Update the text field
		updated_text = "Frequency P.: {:.2f}".format(slider_value)
		self.frequencyPenaltyText.setStringValue_(updated_text)
    
		#Update the stored value in Glyphs defaults
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.frequencyPenaltyValue"] = slider_value

	#Set Presence penalty
	@objc.IBAction
	def setPresencePenaltyValue_(self, sender):
		#Read the current value from the slider
		slider_value = self.presencePenaltySlider.floatValue()
    
		#Update the text field
		updated_text = "Presence P.: {:.2f}".format(slider_value)
		self.presencePenaltyText.setStringValue_(updated_text)
    
		#Update the stored value in Glyphs defaults
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.presencePenaltyValue"] = slider_value

	#Send prompt through flask server
	def get_code_from_chatgpt(self, messages):
		#Get the stored selected mode
		selected_mode = str(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.modelSelection"])
		#Get the stored parameters values
		temperature = float(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.temperatureValue"])
		max_tokens = int(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.maxTokensValue"])
		top_p = float(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.topPValue"])
		frequency_penalty = float(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.frequencyPenaltyValue"])
		presence_penalty = float(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.presencePenaltyValue"])
		
        #Prepare the message payload
		payload = {
			"messages": messages,
			"mode": selected_mode,
			"temperature": temperature,
			"max_tokens": max_tokens,
			"top_p": top_p,
			"frequency_penalty": frequency_penalty,
			"presence_penalty": presence_penalty
		}

		cmd = [
			'curl', '-X', 'POST', 'http://localhost:5000/chatgpt',
			'-H', 'Content-Type: application/json',
			'-d', json.dumps(payload)
		]

		result = subprocess.check_output(cmd).decode('utf-8')
		response = json.loads(result)

		return response.get("response", "No response received.")

	#Shift history down by one index for both userPrompt and Response
	def update_history(self, promptLatest):
		#Move history backwards
		for i in reversed(range(1, 5)):
			Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i}"] = Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i - 1}"]
			Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i}"] = Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i - 1}"]

		#Set the newest data
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist0"] = promptLatest
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.Response_Hist0"] = Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.response"]

	#Construct Messages
	def construct_messages(self):
		selected_history = self.HistoryIterationPupupButton.indexOfSelectedItem()
		messages = [{"role": "system", "content": Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.systemPrompt"]}]
    
		if selected_history == 0:  # Option for -
			messages.append({"role": "user", "content": Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist0"]})
		elif selected_history == 1:  # Option for 3
			for i in range(2, -1, -1):
				if Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i}"]:
					messages.append({"role": "user", "content": Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i}"]})
				if Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i}"]:
					messages.append({"role": "assistant", "content": Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i}"]})
		elif selected_history == 2:  # Option for 5
			for i in range(4, -1, -1):
				if Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i}"]:
					messages.append({"role": "user", "content": Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.userPrompt_Hist{i}"]})
				if Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i}"]:
					messages.append({"role": "assistant", "content": Glyphs.defaults[f"com.ShotaroNakano.ChatGPTCommunicator.Response_Hist{i}"]})
		return messages

	#Fetch from GPT
	@objc.IBAction
	def fetchMain_(self, sender, *i):

		#Load System imputed prompt
		text_storage_system = self.systemPromptText.textStorage()
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt"] = text_storage_system.string()
		system_prompt = str(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt"])

		#Load user imputed prompt
		text_storage = self.userPromptText.textStorage()
		userImputedPrompt = text_storage.string()
		Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt"] = userImputedPrompt
		#Get template
		user_prompt_template = str(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPromptTemplate"])
		#Get user imputted Prompt
		user_prompt_imputed = str(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt"])
		
		#Compose final prompt
		heckbox_state = self.includeReponceToPromptCheckButtom.state()
		text_in_Response = self.responseText.string()

		if i:
			if i[0]>=1:#not to include preface for auto pilot
 				user_prompt = "\n\n" + user_prompt_imputed
			else:
				if heckbox_state:
					user_prompt =  text_in_Response + "\n\n" + user_prompt_template + "\n\n" + user_prompt_imputed
				else:
					user_prompt =  user_prompt_template + "\n\n" + user_prompt_imputed
		else:
			if heckbox_state:
				user_prompt =  text_in_Response + "\n\n" + user_prompt_template + "\n\n" + user_prompt_imputed
			else:
				user_prompt =  user_prompt_template + "\n\n" + user_prompt_imputed
  
  
		

		#Update history
		self.update_history(user_prompt)
		#Construct messages based on selected history
		messages = self.construct_messages()
        
		#Fetch the response based on the messages
		response = self.get_code_from_chatgpt(messages)


		#Store the response
		Glyphs.defaults['com.ShotaroNakano.ChatGPTCommunicator.response'] = response


		#Get the NSTextStorage object from the NSTextView
		text_storage = self.responseText.textStorage()
		#Clear any existing text
		text_storage.deleteCharactersInRange_((0, text_storage.length()))
		#Set new text from defaults
		new_Response_text = Glyphs.defaults['com.ShotaroNakano.ChatGPTCommunicator.response']
		text_storage.appendAttributedString_(NSAttributedString.alloc().initWithString_(new_Response_text))
		#self.responseText.setStringValue_(Glyphs.defaults['com.ShotaroNakano.ChatGPTCommunicator.response'])
        
	#History / Iteration
	@objc.IBAction
	def setHistoryIteration_(self, sender):
		selected_index = int(self.HistoryIterationPupupButton.indexOfSelectedItem())
		if selected_index == 0:
			Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.historyIteration"] = "1"
		elif selected_index == 1:
			Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.historyIteration"] = "3"
		elif selected_index == 2:
			Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.historyIteration"] = "5"

	#Clear History
	@objc.IBAction
	def clearHistoryIterationFromButton_(self, sender):
		self.clearHistory()


	#Button To Macro
	@objc.IBAction
	def sendResponseToMacro_(self, sender):
		#Tab object
		macroViewControllers = NSApp.delegate().macroPanelController().tabBarControl().tabItems()
		#To find the current tab
		tabBarControl = NSApp.delegate().macroPanelController().tabBarControl()

		#Choose the index of the macro panel you want to update
		selectedTab = tabBarControl.selectionIndex()

		#The text you want to set
		row_text = self.responseText.string()
		code_text = self.extractPython_(row_text)

		#Set the new text
		macroViewControllers[selectedTab].macroText().setString_(code_text)

	#Button from Macro
	@objc.IBAction
	def getContentFromMacro_(self, sender):
		#Tab object
		macroViewControllers = NSApp.delegate().macroPanelController().tabBarControl().tabItems()
		#To find the current tab
		tabBarControl = NSApp.delegate().macroPanelController().tabBarControl()

		#Choose the index of the macro panel you want to update
		selectedTab = tabBarControl.selectionIndex()
		print("selectedTab", selectedTab)

		content_macro = macroViewControllers[selectedTab].macroText().string()
		print("content_macro", content_macro)

		#Get the NSTextStorage object from the NSTextView
		text_storage = self.responseText.textStorage()
		#Clear any existing text
		text_storage.deleteCharactersInRange_((0, text_storage.length()))
		#Set new text from defaults
		text_storage.appendAttributedString_(NSAttributedString.alloc().initWithString_(content_macro))
	
        
	#Auto Driving
	@objc.IBAction
	def autoDriving_(self, sender):
		self.clearHistory()
		#Set the maximum number of iterations
		iterationCount = int(Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.historyIteration"])
		for i in range(iterationCount):
			#Fetch a prompt and run the code
			self.fetchMain_(sender, i)
			self.run_(sender)
        
			#Check if there is an error message
			if self.error_message:
				# Use the error message as the next user prompt
				Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt"] = self.error_message
				text_storage = self.userPromptText.textStorage()
				# Clear existing text
				text_storage.deleteCharactersInRange_((0, text_storage.length()))
				# Update the user prompt in the UI
				text_storage.appendAttributedString_(NSAttributedString.alloc().initWithString_(self.error_message))
			else:
				# If there is no error, break out of the loop
				break
    
	#Extract python code from the text in Response
	def extractPython_(self, row_text):

		code_text = row_text

		#Remove __doc__ lines if they exist
		code_text = re.sub(r'__doc__\s*=\s*""".*?"""', '', code_text, flags=re.DOTALL)
    
		#Check for ```python and extract the code
		match = re.search(r'```python(.*?)```', code_text, re.DOTALL)
		if match:
			code_text = match.group(1).strip()

		return code_text

	#Run the Python Code
	@objc.IBAction
	def run_(self, sender):
		#Fetch text from responseText (assuming it's a NSTextView)
		row_text = self.responseText.string()  # Replace with the appropriate method to get text

		code_text = self.extractPython_(row_text)

		#Execute the code
		try:
			exec(code_text)
			self.error_message = ""
		except Exception as e:
			self.error_message = str(e)
			print(f"An error occurred while executing the code: {e}")
			Glyphs.defaults["com.ShotaroNakano.ChatGPTCommunicator.userPrompt"] = self.error_message
			text_storage = self.userPromptText.textStorage()
			# Clear existing text
			text_storage.deleteCharactersInRange_((0, text_storage.length()))
			# Update the user prompt in the UI
			text_storage.appendAttributedString_(NSAttributedString.alloc().initWithString_(self.error_message))

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
