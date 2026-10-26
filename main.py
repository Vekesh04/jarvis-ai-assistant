import webbrowser
import pyttsx3
import speech_recognition as sr
import os
import subprocess
import pywhatkit
import openai
from dotenv import load_dotenv
import winreg

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")  # Load API key from .env file
if not openai.api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def get_installed_path(app_name):
    """Get the installed path of an application from Windows Registry."""
    try:
        # Common registry paths
        paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\Microsoft\Office\16.0\Common\InstallRoot",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                num_subkeys = winreg.QueryInfoKey(key)[0]
                
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if app_name.lower() in subkey_name.lower():
                            subkey = winreg.OpenKey(key, subkey_name)
                            installation_path = winreg.QueryValue(subkey, None)
                            if installation_path and os.path.exists(installation_path):
                                return installation_path
                    except:
                        continue
            except:
                continue
    except Exception as e:
        print(f"Error searching registry: {e}")
    return None

def find_chrome_path():
    """Find Chrome installation path."""
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def find_office_path(app_name):
    """Find Microsoft Office application path."""
    common_paths = [
        rf"C:\Program Files\Microsoft Office\root\Office16\{app_name}",
        rf"C:\Program Files (x86)\Microsoft Office\root\Office16\{app_name}",
        rf"C:\Program Files\Microsoft Office\Office16\{app_name}",
        rf"C:\Program Files (x86)\Microsoft Office\Office16\{app_name}"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def open_desktop_app(app_name):
    """Open a desktop application based on the command."""
    try:
        app_name = app_name.lower()
        
        # Dictionary mapping app names to their executables
        app_executables = {
            "excel": "EXCEL.EXE",
            "word": "WINWORD.EXE",
            "powerpoint": "POWERPNT.EXE"
        }
        
        if "notepad" in app_name:
            subprocess.Popen(["notepad.exe"])
            speak("Opening Notepad.")
        
        elif "calculator" in app_name:
            subprocess.Popen(["calc.exe"])
            speak("Opening Calculator.")
            
        elif "chrome" in app_name:
            chrome_path = find_chrome_path()
            if chrome_path:
                subprocess.Popen([chrome_path, "--profile-directory=Default", "--restore-last-session"])
                speak("Opening Google Chrome.")
            else:
                speak("Sorry, I couldn't find Google Chrome on your system.")
                
        # Handle Microsoft Office applications
        elif app_name in app_executables:
            office_path = find_office_path(app_executables[app_name])
            if office_path:
                subprocess.Popen([office_path])
                speak(f"Opening {app_name}.")
            else:
                speak(f"Sorry, I couldn't find {app_name} on your system.")
        
        elif "whatsapp" in app_name:
            webbrowser.open("https://web.whatsapp.com")
            speak("Opening WhatsApp Web.")
            
        else:
            # Try to find the application in common installation directories
            installed_path = get_installed_path(app_name)
            if installed_path:
                subprocess.Popen([installed_path])
                speak(f"Opening {app_name}.")
            else:
                speak(f"Sorry, I couldn't find {app_name} on your system.")
                
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        speak(f"Sorry, I encountered an error while trying to open {app_name}.")

def get_chatbot_response(query):
    """Get a response from OpenAI's GPT model."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "Sorry, I couldn't process your request."

def process_command(command):
    """Process user commands."""
    command = command.lower()

    if "open google" in command:
        webbrowser.open("https://google.com")
        speak("Opening Google.")
    elif "open facebook" in command:
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook.")
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube.")
    elif "open instagram" in command:
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram.")
    elif "open whatsapp" in command:
        webbrowser.open("https://web.whatsapp.com")
        speak("Opening WhatsApp.")
    elif "open github" in command:
        webbrowser.open("https://github.com")
        speak("Opening GitHub.")
    elif "search for" in command or "search" in command:
        if "youtube" in command:
            search_term = command.replace("search for", "").replace("search", "").replace("youtube", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
            speak(f"Searching for {search_term} on YouTube.")
        elif "google" in command:
            search_term = command.replace("search for", "").replace("search", "").replace("google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            speak(f"Searching for {search_term} on Google.")
    elif "play" in command:
        song_name = command.replace("play", "").strip()
        pywhatkit.playonyt(song_name)
        speak(f"Playing {song_name} on YouTube.")
    elif "who are you" in command:
        speak("I am Jarvis, your personal AI assistant. I can help you with various tasks.")
    elif "who is your creator" in command or "who created you" in command:
        speak("I was created by a software developer.")
    else:
        # Use OpenAI for general conversation
        response = get_chatbot_response(command)
        speak(response)

def listen_for_activation(recognizer):
    """Listen for the wake-up phrase 'Wake up Jarvis'."""
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for 'Wake up Jarvis'...")
                recognizer.adjust_for_ambient_noise(source, duration=2)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

                command = recognizer.recognize_google(audio).lower()
                print(f"Detected: {command}")

                if "wake up jarvis" in command:
                    speak("Jarvis is now active, waiting for your command.")
                    return True
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            continue

if __name__ == "__main__":
    speak("Initializing Jarvis...")
    print("Jarvis initialized and ready to assist.")
    
    while True:
        if listen_for_activation(recognizer):
            active = True

            while active:
                try:
                    with sr.Microphone() as source:
                        print("Jarvis Active... Listening for commands")
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

                        command = recognizer.recognize_google(audio).lower()
                        print(f"Detected command: {command}")

                        if command.startswith("jarvis"):
                            user_command = command.replace("jarvis", "").strip()
                            if "open" in user_command:
                                app_name = user_command.replace("open", "").strip()
                                open_desktop_app(app_name)
                            elif "play" in user_command:
                                song_name = user_command.replace("play", "").strip()
                                pywhatkit.playonyt(song_name)
                                speak(f"Playing {song_name} on YouTube.")
                            else:
                                process_command(user_command)
                        elif "ok jarvis" in command:
                            speak("Going idle. Say 'Wake up Jarvis' when you need me.")
                            active = False
                        elif "go to sleep jarvis" in command:
                            speak("Shutting down. Goodbye.")
                            exit()

                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Error with Google Speech Recognition: {e}")
                except sr.WaitTimeoutError:
                    continue