import tkinter as tk

class CustomButton(tk.Frame):
    def __init__(self, master=None, text="Custom Button", command=None):
        super().__init__(master)
        self.master = master
        self.text = text
        self.command = command
        self.create_widgets()
        
    def create_widgets(self):
        self.button = tk.Button(self, text=self.text, command=self.command)
        self.button.pack()

class CustomLabel(tk.Frame):
    def __init__(self, master=None, text="Custom Label"):
        super().__init__(master)
        self.master = master
        self.text = text
        self.create_widgets()
        
    def create_widgets(self):
        self.label = tk.Label(self, text=self.text)
        self.label.pack()

# Create a Tkinter window
root = tk.Tk()
root.title("Custom Widget Example")

# Create an instance of the custom button widget
custom_button = CustomButton(root, text="Click Me", command=lambda: print("Custom button clicked"))
custom_button.pack()

# Create an instance of the custom label widget
custom_label = CustomLabel(root, text="This is a custom label.")
custom_label.pack()

# Start the Tkinter main loop
root.mainloop()
