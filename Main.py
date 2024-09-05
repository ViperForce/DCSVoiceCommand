import customtkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import datetime
import vgamepad as vg
import threading
import time
import numpy as np
from pathlib import Path
import sounddevice as sd
import noisereduce as nr
from faster_whisper import WhisperModel
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
from Variables import *

# Initialize the Whisper model
model = WhisperModel("base", device="cpu")

def open_file_in_same_directory(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    if script_dir != cwd:
        print("Warning: the script is not running from its own directory.")
        print(f"Script Directory: {script_dir}")
        print(f"Current Working Directory: {cwd}")

    file_path = os.path.join(cwd, file_name)

    return file_path

root = tk.CTk()
root.geometry('400x600')
root.title('DCS Voice Command')
root.resizable(False, False)
icon = Image.open(open_file_in_same_directory('icon.png'))
photo = ImageTk.PhotoImage(icon)
root.iconphoto(False, photo)

titleImage = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("TitleLogo.png")),
                         size=(400, 34))
titleLabel = tk.CTkLabel(root, image=titleImage, text="")
titleLabel.pack(padx=(20, 5), pady=(20, 5))

# Divider
dividerImage = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("Divider.png")),
                           size=(375, 8))
dividerLabelOne = tk.CTkLabel(root, image=dividerImage, text='')
dividerLabelOne.pack(pady=(0, 20))

powerIndicator = tk.CTkImage(light_image=Image.open(open_file_in_same_directory("PowerOffIcon.png")))
gamepad = vg.VX360Gamepad()


def process_audio(indata):
    audio_data = np.frombuffer(indata, dtype=np.float32)
    reduced_noise = nr.reduce_noise(y=audio_data, sr=16000)

    if np.max(reduced_noise) > 0.01:  # Adjust the threshold as needed
        segments, info = model.transcribe(reduced_noise)
        for segment in segments:
            recognized_text = segment.text
            print(f"Recognized: {recognized_text}")
            return recognized_text
    return ""

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    global recognized_text
    recognized_text = process_audio(indata)
    if recognized_text:
        handle_recognition(recognized_text)

# Add a global variable to keep the reference
audio_stream = None

def start_audio_stream():
    global audio_stream
    audio_stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000, blocksize=32000)
    audio_stream.start()
    while listening.is_set():
        sd.sleep(1000)
    audio_stream.stop()
    audio_stream.close()

def handle_recognition(recognized_text):
    if ("chief place" in recognized_text.lower() or
        "chief, place" in recognized_text.lower() or
        "kerchief place" in recognized_text.lower() or
        "Crouchy place" in recognized_text.lower()):
        print("Phrase detected: Crew Chief place the wheel chocks")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
    elif ("chief remove" in recognized_text.lower() or
        "chief, remove" in recognized_text.lower() or
        "kerchief remove" in recognized_text.lower() or
        "Crouchy remove" in recognized_text.lower()):
        print("Phrase detected: Crew Chief remove the wheel chocks")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
    elif ("chief radio" in recognized_text.lower() or
          "chief, radio" in recognized_text.lower() or
          "chief check" in recognized_text.lower() or
          "radio check" in recognized_text.lower() or
          "chief i'll check" in recognized_text.lower()):
        print("Phrase detected: Crew Chief radio check")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
        gamepad.update()
    elif ("chief connect ground air" in recognized_text.lower() or
        "chief, connect ground air" in recognized_text.lower() or
        "chief connect air" in recognized_text.lower() or
        "connect air" in recognized_text.lower() or
        "connect ground air" in recognized_text.lower()):
        print("Phrase detected: Crew Chief connect ground air supply.")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        gamepad.release_button()
    elif ("chief disconnect ground air" in recognized_text.lower() or
        "chief disconnect air" in recognized_text.lower() or
        "disconnect air" in recognized_text.lower() or
        "remove air" in recognized_text.lower() or
        "chief remove air" in recognized_text.lower() or
        "chief remove ground air" in recognized_text.lower() or
        "disconnect ground air" in recognized_text.lower()):
        print("Phrase detected: Crew Chief disconnect ground air supply.")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        gamepad.update()

def listen_in_background():
    while listening.is_set():
        time.sleep(10)

def restart_listening():
    if listening.is_set():
        stop_listening()
        start_listening()

def start_listening():
    listening.set()
    threading.Thread(target=listen_in_background).start()
    threading.Thread(target=start_audio_stream).start()

def stop_listening():
    listening.clear()

def test_listen_thread():
    global testing
    testing = True
    stop_listening()
    micIcon = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("microphoneOn.png")))
    micImage.configure(image=micIcon, text='')
    root.update()
    print('Testing Microphone: ' + str(datetime.datetime.now()))
    testingText.set("Say something!")
    root.update()

    def test_audio_callback(indata, frames, time, status):
        if status:
            print(status)
        recognized_text = process_audio(indata)
        if recognized_text:
            testingText.set("Whisper thinks you said \n" + recognized_text)
        else:
            testingText.set("Whisper could not understand audio")

    with sd.InputStream(callback=test_audio_callback, channels=1, samplerate=16000, blocksize=32000):
        root.update()
        time.sleep(5)  # Wait for a few seconds to allow audio capture

    micIcon = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("microphoneOff.png")))
    micImage.configure(image=micIcon, text='')
    root.update()
    testing = False
    start_listening()

def test_listen():
    if not testing:
        threading.Thread(target=test_listen_thread).start()

def power():
    global powerIndicator
    global powerIndicatorLabel
    status = powerBText.get()
    root.update()
    if status == 'Enable':
        print('User Enabled Speech Recognition: ' + str(datetime.datetime.now()))
        powerBText.set(value='Disable')
        powerIndicator = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("PowerOnIcon.png")))
        powerIndicatorLabel.configure(image=powerIndicator, text='')
        start_listening()
    else:
        print('User Disabled Speech Recognition: ' + str(datetime.datetime.now()))
        powerBText.set(value='Enable')
        powerIndicator = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("PowerOffIcon.png")))
        powerIndicatorLabel.configure(image=powerIndicator, text='')
        stop_listening()

def on_closing():
    stop_listening()
    root.destroy()  # Close the Tkinter window

root.protocol("WM_DELETE_WINDOW", on_closing)

# Store the previous values of the bindings
previous_values = {
    "Place Chocks": wheelChocksPlaceVar.get(),
    "Remove Chocks": wheelChocksRemoveVar.get(),
    "Radio Check": radioCheckVar.get(),
    "Ground Air Connect": groundAirConnectVar.get(),
    "Ground Air Disconnect": groundAirDisconnectVar.get()
}

def combobox_callback(choice, dropdown_name):
    global previous_values
    # Check for double bindings
    bindings = {
        "Place Chocks": wheelChocksPlaceVar.get(),
        "Remove Chocks": wheelChocksRemoveVar.get(),
        "Radio Check": radioCheckVar.get(),
        "Ground Air Connect": groundAirConnectVar.get(),
        "Ground Air Disconnect": groundAirDisconnectVar.get()
    }

    for key, value in bindings.items():
        if key != dropdown_name and value == choice:
            messagebox.showwarning("Binding Error", f"{choice} is already bound to {key}. Please choose a different button.")
            # Revert to the previous value
            if dropdown_name == "Place Chocks":
                wheelChocksPlaceVar.set(previous_values["Place Chocks"])
            elif dropdown_name == "Remove Chocks":
                wheelChocksRemoveVar.set(previous_values["Remove Chocks"])
            elif dropdown_name == "Radio Check":
                radioCheckVar.set(previous_values["Radio Check"])
            elif dropdown_name == "Ground Air Connect":
                groundAirConnectVar.set(previous_values["Ground Air Connect"])
            elif dropdown_name == "Ground Air Disconnect":
                groundAirDisconnectVar.set(previous_values["Ground Air Disconnect"])
            return

    # Update the previous value
    previous_values[dropdown_name] = choice
    print(f"{dropdown_name} binding changed to {choice}")

# Frame for power button and status indicators
workingFrame = (tk.CTkFrame(root))
workingFrame.pack(pady=10)
# Enable/Disable Button
powerBText = tk.StringVar(value='Enable')
powerButton = tk.CTkButton(workingFrame, textvariable=powerBText, command=power, font=('Verdana', 12))
powerButton.pack(side=tk.RIGHT, padx=10, pady=10)
# Status Indicators
powerIndicatorLabel = tk.CTkLabel(workingFrame, image=powerIndicator, text='')
powerIndicatorLabel.pack(side=tk.LEFT, padx=(10, 0))

# Frame for testing button and text field for feedback
testingFrame = (tk.CTkFrame(root))
testingFrame.pack(pady=10)
# Microphone Icon
micIcon = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("microphoneOff.png")))
micImage = tk.CTkLabel(testingFrame, image=micIcon, text='')
micImage.pack(side=tk.LEFT, padx=10)
# Testing button
testingButton = tk.CTkButton(testingFrame, text='Test Microphone', command=test_listen, font=('Verdana', 12))
testingButton.pack(side=tk.LEFT, padx=(0, 10), pady=5)
# Text Field
testingText = tk.StringVar(value='')
testingField = tk.CTkLabel(testingFrame, textvariable=testingText)
testingField.pack(side=tk.RIGHT, pady=10)

# Divider
dividerLabelTwo = tk.CTkLabel(root, image=dividerImage, text='')
dividerLabelTwo.pack(pady=(10, 5))

# Options frame with dropdowns to choose what commands press what buttons. Ex: Radio Check: <MenuButton>
optionsFrame = (tk.CTkFrame(root))
optionsFrame.pack(pady=10)
# Options Header
optionsImage = tk.CTkImage(dark_image=Image.open(open_file_in_same_directory("OptionsHeader.png")),
                         size=(100, 34))
optionsHeader = tk.CTkLabel(optionsFrame, image=optionsImage, text="")
optionsHeader.grid(row=0, column=0, columnspan=2, padx=10, pady=(5,5))
# Command Bindings Dropdowns.
# Chocks Place
wheelChockPlaceBindDropdown = tk.CTkComboBox(optionsFrame, values=valueList, command=lambda choice: combobox_callback(choice, "Place Chocks"),
                                             state="readonly", variable=wheelChocksPlaceVar)
wheelChockPlaceBindDropdown.grid(row=1, column=1, sticky='ew', padx=5, pady=(0,5))
wheelChocksPlaceLabel = tk.CTkLabel(optionsFrame, text='Place Chocks: ', font=('Verdana Bold', 14))
wheelChocksPlaceLabel.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
# Chocks Remove
wheelChockRemoveBindDropdown = tk.CTkComboBox(optionsFrame, values=valueList, command=lambda choice: combobox_callback(choice, "Remove Chocks"),
                                             state="readonly", variable=wheelChocksRemoveVar)
wheelChockRemoveBindDropdown.grid(row=2, column=1, sticky='ew', padx=5, pady=(0,5))
wheelChocksRemoveLabel = tk.CTkLabel(optionsFrame, text='Remove Chocks: ', font=('Verdana Bold', 14))
wheelChocksRemoveLabel.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
# Radio Check
radioCheckBindDropdown = tk.CTkComboBox(optionsFrame, values=valueList, command=lambda choice: combobox_callback(choice, "Radio Check"),
                                             state="readonly", variable=radioCheckVar)
radioCheckBindDropdown.grid(row=3, column=1, sticky='ew', padx=5, pady=(0,5))
radioCheckLabel = tk.CTkLabel(optionsFrame, text='Radio Check: ', font=('Verdana Bold', 14))
radioCheckLabel.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
# Ground Air Connect
groundAirConnectBindDropdown = tk.CTkComboBox(optionsFrame, values=valueList, command=lambda choice: combobox_callback(choice, "Ground Air Connect"),
                                             state="readonly", variable=groundAirConnectVar)
groundAirConnectBindDropdown.grid(row=4, column=1, sticky='ew', padx=5, pady=(0,5))
groundAirConnectLabel = tk.CTkLabel(optionsFrame, text='Ground Air Connect: ', font=('Verdana Bold', 14))
groundAirConnectLabel.grid(row=4, column=0, sticky='ew', padx=5, pady=5)
# Ground Air Disconnect
groundAirDisconnectBindDropdown = tk.CTkComboBox(optionsFrame, values=valueList, command=lambda choice: combobox_callback(choice, "Ground Air Disconnect"),
                                             state="readonly", variable=groundAirDisconnectVar)
groundAirDisconnectBindDropdown.grid(row=5, column=1, sticky='ew', padx=5, pady=(0,5))
groundAirDisconnectLabel = tk.CTkLabel(optionsFrame, text='Ground Air Disconnect: ', font=('Verdana Bold', 14))
groundAirDisconnectLabel.grid(row=5, column=0, sticky='ew', padx=5, pady=5)

root.mainloop()
