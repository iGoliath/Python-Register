import tkinter as tk

def report_key(event):
    # Clear the label and update with new key info
    label.config(text=f"keysym: {event.keysym}\nchar: {repr(event.char)}\nkeycode: {event.keycode}")
    print(f"Keysym: {event.keysym} | Char: {repr(event.char)} | Keycode: {event.keycode}")

root = tk.Tk()
root.title("Tkinter Keysym Tester")
root.geometry("300x200")

label = tk.Label(root, text="Press any key", font=("Helvetica", 16), pady=40)
label.pack(expand=True)

# Bind all key presses to the report_key function
root.bind("<Key>", report_key)

root.mainloop()
