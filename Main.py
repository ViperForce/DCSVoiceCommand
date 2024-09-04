import customtkinter as tk
from PIL import Image, ImageTk
import datetime
import speech_recognition as sr
import vgamepad as vg
import threading
import time

root = tk.CTk()
root.geometry('400x600')
root.title('DCS Voice Command')
root.resizable(False, False)
icon = Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice Command/voice-circle.png")
photo = ImageTk.PhotoImage(icon)
root.iconphoto(False, photo)

titleImage = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice Command/TitleLogo.png"),
                         size=(400, 34))
titleLabel = tk.CTkLabel(root, image=titleImage, text="")
titleLabel.pack(padx=(20, 5), pady=(20, 5))

# Divider
dividerImage = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice Command/Divider.png"),
                           size=(375, 8))
dividerLabel = tk.CTkLabel(root, image=dividerImage, text='')
dividerLabel.pack(pady=(0, 20))

# TODO:
# Test Button to Test Mic

powerIndicator = tk.CTkImage(light_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice "
                                                    "Command/PowerOffIcon.png"))
r = sr.Recognizer()
audio = ''
listening = False
testing = False
gamepad = vg.VX360Gamepad()

def listen_in_background():
    global listening
    while listening:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            recognized_text = r.recognize_sphinx(audio)
            print(f"Recognized: {recognized_text}")
            # Compare recognized_text with predefined strings and perform actions
            if "chief place" in recognized_text.lower():
                print("Phrase detected: Crew Chief place the wheel chocks")
                gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)  # press the A button
                gamepad.update()  # send the updated state to the computer
                # Restart the recognition after each recognized speech
                print('Listening reset after phrase detected.')
                restart_listening()
            elif "chief remove" in recognized_text.lower():
                print("Phrase detected: Crew Chief remove the wheel chocks")
                gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B) # press the B button
                gamepad.update()
                # Restart the recognition after each recognized speech
                print('Listening reset after phrase detected.')
                restart_listening()
            elif ("chief radio" or "chief check" or "chief i'll check") in recognized_text.lower():
                print("Phrase detected: Crew Chief radio check")
                gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
                gamepad.update()
                # Restart the recognition after each recognized speech
                print('Listening reset after phrase detected.')
                restart_listening()
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print(f"Sphinx error; {e}")
        # Restart the recognition every 10 seconds
        time.sleep(10)
        print("Listening reset after 10 seconds.")
        restart_listening()

def restart_listening():
    global listening
    if listening:
        stop_listening()
        start_listening()

def start_listening():
    global listening
    listening = True
    threading.Thread(target=listen_in_background).start()

def stop_listening():
    global listening
    listening = False

def test_listen_thread():
    global testing
    testing = True
    stop_listening()
    micIcon = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice Command/microphoneOn.png"))
    micImage.configure(image=micIcon, text='')
    root.update()
    print('Testing Microphone: ' + str(datetime.datetime.now()))
    testingText.set("Say something!")
    root.update()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        root.update()
    try:
        testingText.set("Sphinx thinks you said \n" + r.recognize_sphinx(audio))
        print(testingText.get())
    except sr.UnknownValueError:
        testingText.set("Sphinx could not understand audio")
        print(testingText.get())
    except sr.RequestError as e:
        testingText.set("Sphinx error; {0}".format(e))
        print(testingText.get())
    micIcon = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice Command/microphoneOff.png"))
    micImage.configure(image=micIcon, text='')
    root.update()
    testing = False
    start_listening()

def test_listen():
    if not testing:
        threading.Thread(target=test_listen_thread).start()

# Function to turn StT on.
def power():
    global powerIndicator
    global powerIndicatorLabel
    global r
    global audio
    status = powerBText.get()
    root.update()
    if status == 'Enable':
        print('User Enabled Speech Recognition: ' + str(datetime.datetime.now()))
        powerBText.set(value='Disable')
        powerIndicator = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice "
                                                           "Command/PowerOnIcon.png"))
        powerIndicatorLabel.configure(image=powerIndicator, text='')
        start_listening()
    else:
        print('User Disabled Speech Recognition: ' + str(datetime.datetime.now()))
        powerBText.set(value='Enable')
        powerIndicator = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice "
                                                           "Command/PowerOffIcon.png"))
        powerIndicatorLabel.configure(image=powerIndicator, text='')
        stop_listening()

# Frame for power button and status indicators
workingFrame = (tk.CTkFrame(root))
workingFrame.pack(pady=10)
# Enable/Disable Button
powerBText = tk.StringVar(value='Enable')
powerButton = tk.CTkButton(workingFrame, textvariable=powerBText, command=power)
powerButton.pack(side=tk.LEFT, padx=10, pady=5)
# Status Indicators
powerIndicatorLabel = tk.CTkLabel(workingFrame, image=powerIndicator, text='')
powerIndicatorLabel.pack(side=tk.RIGHT, padx=(0, 10))

# Frame for testing button and text field for sr feedback
testingFrame = (tk.CTkFrame(root))
testingFrame.pack(pady=10)
# Microphone Icon
micIcon = tk.CTkImage(dark_image=Image.open("C:/Users/chery/OneDrive/Documents/DCS Voice Command/microphoneOff.png"))
micImage = tk.CTkLabel(testingFrame, image=micIcon, text='')
micImage.pack(side=tk.LEFT, padx=10)
# Testing button
testingButton = tk.CTkButton(testingFrame, text='Test Microphone', command=test_listen)
testingButton.pack(side=tk.LEFT, padx=(0, 10), pady=5)
# Text Field
testingText = tk.StringVar(value='')
testingField = tk.CTkLabel(testingFrame, textvariable=testingText)
testingField.pack(side=tk.RIGHT, pady=10)

root.mainloop()
