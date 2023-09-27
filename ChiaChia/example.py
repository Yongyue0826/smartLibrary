import tkinter as tk
import cv2
import csv
from PIL import Image, ImageTk
from tkinter import ttk  # Import the ttk module for Treeview
from tkinter import filedialog
import shutil
import os

# Create a Tkinter window
root = tk.Tk()
root.title("Scaled Video and CSV Data Display")

# Create a Label widget for video display
video_label = tk.Label(root)
video_label.pack()

# Open the video file using OpenCV
video_capture = cv2.VideoCapture('library.mp4')

# Function to update and display the scaled video frame
def update_frame():
    ret, frame = video_capture.read()
    if ret:
        # Convert the frame from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Resize the frame to the desired size
        scaled_frame = cv2.resize(frame_rgb, (320, 240))  # Adjust the dimensions as needed
        # Convert to a PIL Image
        pil_image = Image.fromarray(scaled_frame)
        # Convert to a PhotoImage object for displaying in Tkinter
        photo = ImageTk.PhotoImage(image=pil_image)
        video_label.config(image=photo)
        video_label.photo = photo
        root.after(10, update_frame)  # Update frame every 10 milliseconds

def create_table_with_buttons():

    # Create a Treeview widget for the table
    columns = ("Attribute1", "Attribute2", "Attribute3", "View")
    data_tree = ttk.Treeview(root, columns=columns, show="headings")

    # Define your CSV file path
    csv_file = 'test.csv'

    # Function to load and display CSV data in the table
    def load_csv_data():
        # Clear existing data in the table
        data_tree.delete(*data_tree.get_children())

        with open(csv_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)  # Read the header row
            for col in columns[:-1]:  # Exclude the last column ('View')
                data_tree.heading(f"#{columns.index(col) + 1}", text=col)  # Set column headings

            for row in csvreader:
                # Insert each row as a new item in the Treeview
                item_values = row[:3] + ['View']  # Display the first three attributes and add 'View' button
                data_tree.insert('', 'end', values=item_values)

        # Add a column for the 'View' buttons
        data_tree.column("View", width=100)  # Adjust the width as needed

    # Create a button to load and display CSV data in the table
    load_button = tk.Button(root, text="Load CSV Data", command=load_csv_data)
    load_button.pack()

    # Function to handle button clicks (you can customize this)
    def handle_button_click(event):
        item = data_tree.selection()[0]
        item_values = data_tree.item(item, 'values')
        if item_values[-1] == 'View':
            # Perform an action when 'View' button is clicked (customize as needed)
            print("View button clicked for row:", item_values[:-1])

    # Configure the rectangular button appearance using a custom cell renderer
    style = ttk.Style()
    style.configure(
        "Button.Treeview",
        font=("Arial", 12),
        background="blue",  # Button background color (blue)
        foreground="white",  # Text color (white)
        padding=(10, 2),     # Padding (adjust as needed)
        relief="raised"      # Border style
    )

    # Apply the custom cell renderer to the "View" column
    data_tree.tag_configure("Button.Treeview", font=("Arial", 12), background="blue", foreground="white")

    data_tree.heading("#1", text="Attribute1")
    data_tree.heading("#2", text="Attribute2")
    data_tree.heading("#3", text="Attribute3")
    data_tree.heading("#4", text="View")

    # Bind button click events to the custom cell renderer
    data_tree.tag_bind("Button.Treeview", "<ButtonRelease-1>", handle_button_click)

    # Pack the Treeview widget
    data_tree.pack()



# Call the method to create the table with buttons
create_table_with_buttons()

# Function to handle video file selection and copy
def browse_and_copy_video():
    # Specify the subdirectory name where the video will be copied
    target_directory = "videos"
    
    # Set the initial directory for file selection
    initial_dir = os.path.expanduser("~")
    
    file_path = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4 *.avi *.mkv")],
        initialdir=initial_dir
    )
    
    if file_path:
        # Create the target directory if it doesn't exist
        target_dir = os.path.join(os.getcwd(), target_directory)
        os.makedirs(target_dir, exist_ok=True)
        
        # Copy the selected video to the target directory
        video_name = os.path.basename(file_path)
        target_path = os.path.join(target_dir, video_name)
        
        try:
            shutil.copyfile(file_path, target_path)
            print(f"Video '{video_name}' copied to '{target_path}'")
        except Exception as e:
            print(f"Error copying video: {str(e)}")

# Create a button to browse and copy the video
copy_button = tk.Button(root, text="Browse and Copy Video", command=browse_and_copy_video)
copy_button.pack()

# Start video playback
update_frame()

# Start the Tkinter main loop
root.mainloop()
