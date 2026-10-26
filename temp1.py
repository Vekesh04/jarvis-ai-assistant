import webbrowser
import pyttsx3
import speech_recognition as sr
import os
import subprocess
import pywhatkit
import openai
from dotenv import load_dotenv
import platform

# NOTE: winreg is a Windows-specific module. It must be removed for macOS.
# import winreg 

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    # A cleaner way to handle API key failure in a GUI application might be a QMessageBox, 
    # but raising an exception is fine for a script's initialization phase.
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
# Note: pyttsx3 works differently on macOS, often using the 'nsspeech' driver.
engine = pyttsx3.init() 

def speak(text):
    """Convert text to speech."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech error: {e}")

def find_program_path(program_name):
    """Find program path based on operating system."""
    system = platform.system().lower()
    program_name = program_name.lower().strip()
    
    # --- Start macOS/Linux specific search ---
    if system == "darwin":  # macOS
        # Common macOS application locations
        common_locations = [
            f"/Applications/{program_name}.app",
            f"{os.path.expanduser('~/Applications')}/{program_name}.app"
        ]
        # Also check common executable paths
        common_executables = [
            f"/usr/bin/{program_name}",
            f"/usr/local/bin/{program_name}"
        ]
        
        for location in common_locations + common_executables:
            # Check for the directory/file
            if os.path.exists(location):
                return location
                
    elif system == "linux":  # Linux
        # Common Linux executable paths
        common_locations = [
            f"/usr/bin/{program_name}",
            f"/usr/local/bin/{program_name}"
        ]
        for location in common_locations:
            if os.path.exists(location):
                return location
                
    # --- Windows specific search (Kept for completeness, but won't run on Mac) ---
    elif system == "windows":
        # Simplified Windows search without winreg for cross-platform ease (optional to keep)
        program_name_exe = program_name + '.exe' if not program_name.endswith('.exe') else program_name
        common_locations = [
            os.path.join(os.environ.get('ProgramFiles', ''), program_name_exe),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), program_name_exe),
        ]
        for location in common_locations:
            if os.path.exists(location):
                return location
    
    return None

def open_desktop_app(app_name):
    """Open desktop applications for macOS/Linux."""
    try:
        app_name = app_name.lower().strip()
        print(f"Attempting to open: {app_name}")
        
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # Use the 'open' command which handles both .app bundles and executables
            # Special case for Chrome to use its common app path if found
            if app_name == "chrome":
                path = "/Applications/Google Chrome.app"
                if os.path.exists(path):
                    subprocess.run(["open", path])
                    speak("Opening Google Chrome.")
                    return
            
            # Use 'open -a' to try and launch by application name
            subprocess.run(["open", "-a", app_name])
            speak(f"Opening {app_name}")
            return

        elif system == "linux":  # Linux
            # Directly use the app name as a command
            subprocess.Popen([app_name])
            speak(f"Opening {app_name}")
            return
            
        elif system == "windows":
             # Placeholder for Windows logic if you want to run it there later
             # You might need to re-implement some Windows logic here if the caller expects a return
             # In the original temp1.py, this section was more complex with find_program_path and os.startfile
             speak(f"Cannot open desktop app on this OS: {system}")
             return


        # Fallback for systems not explicitly handled or if initial attempts fail
        # Try finding the program path and launching it
        program_path = find_program_path(app_name)
        if program_path:
            if system == "darwin":
                subprocess.run(["open", program_path])
            elif system == "linux":
                subprocess.run([program_path])
            else:
                 # This should ideally not be reached if platform check is thorough
                subprocess.run([program_path])
            speak(f"Opening {app_name}")
            return
            
        speak(f"Sorry, I couldn't find or open {app_name}")
            
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        speak(f"Sorry, I encountered an error while trying to open {app_name}")


def get_chatbot_response(prompt):
    """Get response from OpenAI ChatGPT."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant named Jarvis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I encountered an error: {str(e)}"

def process_command(command, is_voice=True):
    """Process user commands and return response string."""
    try:
        command = command.lower().strip()
        # print(f"Processing command: {command}") # Debug print

        # Website commands (These are platform-independent)
        websites = {
            "open google": "https://google.com",
            "open facebook": "https://facebook.com",
            "open youtube": "https://youtube.com",
            "open instagram": "https://www.instagram.com",
            "open whatsapp": "https://web.whatsapp.com",
            "open github": "https://github.com"
        }

        # Check website commands
        for key, url in websites.items():
            if key in command:
                webbrowser.open(url)
                response = f"Opening {key.replace('open ', '')}"
                if is_voice:
                    speak(response)
                return response

        # Handle song playback (pywhatkit is platform-independent)
        if command.startswith("play"):
            song_name = command.replace("play", "").strip()
            song_name = " ".join(song_name.split())
            # print(f"Attempting to play song: {song_name}") # Debug print
            try:
                pywhatkit.playonyt(song_name)
                response = f"Playing {song_name} on YouTube"
                if is_voice:
                    speak(response)
                return response
            except Exception as e:
                response = f"Sorry, I couldn't play that song: {str(e)}"
                if is_voice:
                    speak(response)
                return response

        # Search commands (webbrowser is platform-independent)
        if "search for" in command or "search" in command:
            search_term = command.replace("search for", "").replace("search", "").strip()
            response = ""
            if "youtube" in command:
                search_term = search_term.replace("youtube", "").strip()
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
                response = f"Searching for {search_term} on YouTube"
            elif "google" in command:
                search_term = search_term.replace("google", "").strip()
                webbrowser.open(f"https://www.google.com/search?q={search_term}")
                response = f"Searching for {search_term} on Google"
            else:
                 # Default to Google search if no platform is specified
                 webbrowser.open(f"https://www.google.com/search?q={search_term}")
                 response = f"Searching for {search_term} on Google"
                 
            if is_voice:
                speak(response)
            return response

        # Open app command (platform-specific logic handled inside the function)
        if command.startswith("open "):
            app_name = command.replace("open ", "").strip()
            open_desktop_app(app_name) # This function handles its own speaking/printing
            return None # Return None as open_desktop_app handles the user feedback

        # Handle ChatGPT responses for everything else
        if command not in ["exit", "quit", "go to sleep"]:
            try:
                response = get_chatbot_response(command)
                if is_voice:
                    speak(response)
                return response
            except Exception as e:
                response = f"Sorry, I couldn't get a response from ChatGPT: {str(e)}"
                if is_voice:
                    speak(response)
                return response

        # If it's a known exit command, return a message to stop the main loop
        if command in ["exit", "quit", "go to sleep"]:
            response = "Goodbye!"
            if is_voice:
                speak(response)
            return response

        # Default response if no conditions are met
        response = "I didn't understand that command. Please try again."
        if is_voice:
            speak(response)
        return response

    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        if is_voice:
            speak(error_msg)
        return error_msg

def listen_for_activation(recognizer):
    """Listen for the activation phrase 'Wake up Jarvis'."""
    try:
        with sr.Microphone() as source:
            print("Waiting for activation phrase 'Wake up Jarvis'...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            # Use a longer timeout and phrase limit for activation
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5) 
            command = recognizer.recognize_google(audio).lower()
            return "wake up jarvis" in command
    except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
        return False

def get_text_input():
    """Get command from text input."""
    try:
        command = input("Enter your command (or 'exit' to quit): ").strip()
        if command.lower() in ['exit', 'quit']:
            print("Goodbye!")
            exit()
        return command
    except KeyboardInterrupt:
        print("\nGoodbye!")
        exit()

def main():
    """Main function for the CLI version."""
    speak("Initializing Jarvis...")
    print("Jarvis initialized and ready to assist.")
    
    print("\nHow would you like to interact with Jarvis?")
    print("1. Voice commands")
    print("2. Text commands")
    
    while True:
        try:
            choice = input("Enter your choice (1 or 2): ").strip()
            if choice in ['1', '2']:
                break
            print("Please enter either 1 or 2.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()

    if choice == '1':
        print("Voice mode activated. Say 'Wake up Jarvis' to start.")
        speak("Voice mode activated. Say 'Wake up Jarvis' to start.")
        
        while True:
            if listen_for_activation(recognizer):
                speak("Jarvis is now active, waiting for your command.")
                active = True
                
                while active:
                    try:
                        with sr.Microphone() as source:
                            print("Jarvis Active... Listening for commands")
                            recognizer.adjust_for_ambient_noise(source, duration=1)
                            # Listen for the actual command
                            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5) 

                        try:
                            user_command = recognizer.recognize_google(audio).lower()
                            print(f"Command detected: {user_command}")
                            
                            if "go to sleep" in user_command or "stop listening" in user_command:
                                speak("Going idle. Say 'Wake up Jarvis' when you need me.")
                                active = False
                                continue
                            
                            response = process_command(user_command, is_voice=True)
                            
                        except sr.UnknownValueError:
                            speak("Sorry, I didn't catch that. Could you repeat?")
                        except sr.RequestError:
                            speak("Sorry, there was an error with the speech recognition service.")
                        except sr.WaitTimeoutError:
                             # Go idle if no command is heard after activation
                            speak("Going idle due to inactivity.")
                            active = False
                            
                    except KeyboardInterrupt:
                        print("\nGoodbye!")
                        exit()
                    except Exception as e:
                        print(f"Error: {e}")
                        
    else: # Text commands
        print("\nJarvis is ready for text commands!")
        print("Type your commands (type 'exit' or 'quit' to exit)")
        while True:
            command = get_text_input()
            response = process_command(command, is_voice=False)
            if response:
                print(f"Jarvis: {response}")

if __name__ == "__main__":
    main()