# modules needed
# pip install SpeechRecognition pyttsx3 pyaudio webbrowser

import speech_recognition as sr
import pyttsx3, os
from langchain_google_genai import ChatGoogleGenerativeAI
import pyautogui as pag
import webbrowser
import re
import time

from dotenv import load_dotenv
load_dotenv()

# Initialize the LLM model
model = ChatGoogleGenerativeAI(model='gemini-1.5-flash')

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

history = [
    """
    system : you are a helpful assistant that responds with very little text and accurate answers that sound like a friend or a teacher.
    using emojis is your style in answers. also you can open any app in the computer of the user if the user wants it for that you have to use a special token
    that is <open>notepad<close> and this will open notepad for the user other apps have their names also, this method calls a os.system function that opens the app
    other apps are like 
    <open>start chrome<close> for opening chrome 
    <open>notepad<close> for opening notepad
     <open>Camera<close> for opening Camera
    <open>mspaint<close> for opening paint
    <open>code<close> for opening vs code
    <open>start excel<close> for opening MS Excel
    <open>start powerpnt<close> for opening PowerPoint
    <open>start winword<close> for opening MS Word
    <open>start microsoft.windows.camera:<close> for opening camera
    <open>start ms-windows-store:<close> for opening MS Store
    for youtube use <open>https://www.youtube.com/results?search_query=song_name<close> where song_name is the name of the song the user wants to play
    for google use <open>https://www.google.com/search?q=search_query<close> where search_query is what the user wants to search
    <open>start spotify<close> for opening Spotify
    <open>start cmd<close> for opening command prompt
    <open>start explorer<close> for opening file explorer
    <open>start ms-settings:<close> for opening settings
    <open>start ms-settings:bluetooth<close> for opening bluetooth settings
    <open>start ms-settings:windowsupdate<close> for opening windows update settings
    <open>start ms-settings:personalization<close> for opening personalization settings
    <open>start ms-settings:apps<close> for opening apps settings
    <open>start ms-settings:time-date<close> for opening time and date settings
    if the user says stop, respond with "Namaste, have a great day" and exit the program
    your name is Ojas and when the user calls you by name, respond with "Yes, how can I help you?"
    also if you have to write something then use <write>this is to write<close> and if you have to press any key like space or enter then say <press>enter<close> or <press>space<close>. 
    and always keep in mind in one response you can only use <open> or <write> or <press> only single time not twice or two different commands in same response is not allowed. use enter character instead of \\n.
    """
]

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Flag to check if assistant is in active listening mode
listening_mode = True

# Main loop
while True:
    try:
        # Capture voice input
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        print("Converting to Text ...")
        # Convert voice input to text
        inp = recognizer.recognize_google(audio)
        print(f"You: {inp}")
        
        # Check if user wants to stop
        if "stop" in inp.lower():
            print("AI: Namaste, have a great day")
            speak("Namaste, have a great day")
            break
        
        # Check if user called the assistant by name "Ojas"
        if "ojas" in inp.lower():
            print("AI: Yes, how can I help you?")
            speak("Yes, how can I help you?")
            listening_mode = True
            continue
            
        # Only process commands if in active listening mode
        if listening_mode:
            history.append(str("user :"+ inp))

            response = model.invoke(history)

            # Get the LLM's response
            ai_response = response.content
            ai_response = str(ai_response).lower()

            if "<open>" in ai_response:
                ai_response = ai_response.replace("<open>", "|")
                ai_response = ai_response.replace("<close>", "|")
                start = ai_response.find("|")
                end = ai_response.find("|", start+1)
                program = ai_response[start+1:end]

                try:
                    # Handle web URLs differently
                    if program.startswith("http"):
                        webbrowser.open(program)
                    else:
                        os.system(program)
                except Exception as e:
                    print(f"Error in opening: {e}")
            
            if "<write>" in ai_response:
                ai_response = ai_response.replace("<write>", "|")
                ai_response = ai_response.replace("<close>", "|")
                start = ai_response.find("|")
                end = ai_response.find("|", start+1)
                write = ai_response[start+1:end]

                try:
                    print("Writing: ", write)
                    pag.typewrite(write, 0.1)
                except Exception as e:
                    print(f"Error in writing: {e}")

            if "<press>" in ai_response:
                ai_response = ai_response.replace("<press>", "|")
                ai_response = ai_response.replace("<close>", "|")
                start = ai_response.find("|")
                end = ai_response.find("|", start+1)
                key = ai_response[start+1:end]

                try:
                    pag.press(key)
                except Exception as e:
                    print(f"Error pressing key: {e}")
            
            # Clean up the response for speaking (remove tags)
            clean_response = re.sub(r'\|.*?\|', '', ai_response)
            
            print("AI:", clean_response)
            history.append(str("AI :"+ ai_response))

            # Read out the LLM's response
            speak(clean_response)
        
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio. Please try again.")
        speak("Sorry, I could not understand the audio. Please try again.")
    except sr.RequestError as e:
        print(f"Could not request results from the speech recognition service; {e}")
        speak("There was an error with the speech recognition service.")
    except Exception as e:
        print(f"An error occurred: {e}")
        speak("An error occurred. Please try again.")
