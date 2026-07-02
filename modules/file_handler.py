from tkinter import filedialog
import pandas as pd

# Open file dialog
def select_file():
    path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
    )
    return path

# Load file using pandas
def load_file(file_path):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    return df