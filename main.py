import customtkinter as ctk
from tkinter import messagebox
from modules.file_handler import select_file, load_file
from modules.data_processor import generate_report

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= SETTINGS =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================= GLOBAL =================
df = None
result_df = None
history = []

# ================= FUNCTIONS =================

def browse_file():
    path = select_file()
    if path:
        file_entry.delete(0, "end")
        file_entry.insert(0, path)


def read_data():
    global df

    path = file_entry.get()
    if not path:
        messagebox.showerror("Error", "Select file first")
        return

    df = load_file(path)

    output_label.configure(
        text=f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns"
    )

    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    group_combo.configure(values=text_cols)
    value_combo.configure(values=num_cols)

    group_combo.set("Select Column")
    value_combo.set("Select Numeric")
    agg_combo.set("Select Operation")
    chart_combo.set("Select Chart")

    status.configure(text="Data Loaded")
    reset_status()


def generate_report_ui():
    global df, result_df

    if df is None:
        messagebox.showerror("Error", "Load data first")
        return

    group = group_combo.get()
    value = value_combo.get()
    agg = agg_combo.get()
    if group == "Select" or value == "Select" or agg == "Select":
        messagebox.showerror("Error", "Please select options")
        return

    if group == "Select Column" or value == "Select Numeric" or agg == "Select Operation":
        messagebox.showerror("Error", "Please select valid options")
        return

    if group not in df.columns or value not in df.columns:
        messagebox.showerror("Error", "Invalid column selected")
        return

    history.append(("report", result_df.copy() if result_df is not None else None))

    result_df = generate_report(df, group, value, agg)

    for widget in table_frame.winfo_children():
        widget.destroy()

    for col_i, col in enumerate(result_df.columns):
        ctk.CTkLabel(table_frame, text=col, font=("Arial", 14, "bold")).grid(row=0, column=col_i)

    for row_i, row in result_df.iterrows():
        for col_i, val in enumerate(row):
            if isinstance(val, float):
                val = round(val, 2)

            ctk.CTkLabel(
                table_frame,
                text=str(val),
                fg_color="#2b2b2b",
                corner_radius=6,
                padx=8,
                pady=4
            ).grid(row=row_i+1, column=col_i, padx=5, pady=3)

    status.configure(text="Report Generated")
    reset_status()


def draw_chart():
    global result_df

    if result_df is None:
        messagebox.showerror("Error", "Generate report first")
        return

    chart_type = chart_combo.get()
    if chart_type == "Select Chart":
        messagebox.showerror("Error", "Select chart type")
        return

    history.append(("chart", None))

    for widget in chart_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(5, 4))

    x = result_df.iloc[:, 0]
    y = result_df.iloc[:, 1]

    if chart_type == "bar":
        ax.bar(x, y)
    elif chart_type == "line":
        ax.plot(x, y, marker='o')
    elif chart_type == "pie":
        ax.pie(y, labels=x, autopct="%1.1f%%")

    ax.set_title("Chart View")

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    status.configure(text="Chart Displayed")
    reset_status()


def clear_table():
    for widget in table_frame.winfo_children():
        widget.destroy()
    status.configure(text="Table Cleared")
    reset_status()


def clear_chart():
    for widget in chart_frame.winfo_children():
        widget.destroy()
    status.configure(text="Chart Cleared")
    reset_status()


def reset_app():
    global df, result_df

    df = None
    result_df = None

    file_entry.delete(0, "end")
    output_label.configure(text="No file loaded")

    clear_table()
    clear_chart()

    status.configure(text="Reset Complete")
    reset_status()


def export_report():
    global result_df

    if result_df is None:
        messagebox.showerror("Error", "No report to export")
        return

    result_df.to_excel("report.xlsx", index=False)
    messagebox.showinfo("Success", "Saved as report.xlsx")

    status.configure(text="Report Exported")
    reset_status()


def undo_action():
    global result_df

    if not history:
        messagebox.showinfo("Undo", "Nothing to undo")
        return

    action, data = history.pop()

    if action == "report":
        result_df = data
        clear_table()

    elif action == "chart":
        clear_chart()

    status.configure(text="Undo Done")
    reset_status()


def toggle_theme():
    mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("light" if mode == "Dark" else "dark")


def reset_status():
    app.after(3000, lambda: status.configure(text="Ready"))


# ================= UI =================

app = ctk.CTk()
app.geometry("1150x650")
app.title("Smart Data Analyzer")

# ---------- MAIN CONTAINER ----------
container = ctk.CTkFrame(app)
container.pack(fill="both", expand=True)

# ---------- SIDEBAR ----------
sidebar = ctk.CTkFrame(container, width=180)
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="Analyzer", font=("Arial", 18, "bold")).pack(pady=20)
ctk.CTkButton(sidebar, text="Toggle Theme", command=toggle_theme).pack(pady=10)

# ---------- MAIN AREA ----------
main = ctk.CTkFrame(container)
main.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ---------- TOP ----------
top_frame = ctk.CTkFrame(main)
top_frame.pack(fill="x", pady=5)

file_entry = ctk.CTkEntry(top_frame, width=300, placeholder_text="Select CSV or Excel file...")
file_entry.grid(row=0, column=0, padx=5)

ctk.CTkButton(top_frame, text="Browse", command=browse_file).grid(row=0, column=1)
ctk.CTkButton(top_frame, text="Load Data", command=read_data).grid(row=0, column=2)

output_label = ctk.CTkLabel(top_frame, text="No file loaded")
output_label.grid(row=0, column=3, padx=10)

# ---------- CONTROLS ----------
control_frame = ctk.CTkFrame(main)
control_frame.pack(fill="x", pady=5)

# ===== LABELS (BACK TO CLEAN VERSION) =====
ctk.CTkLabel(control_frame, text="Group By").grid(row=0, column=0, pady=2)
ctk.CTkLabel(control_frame, text="Numeric Column").grid(row=0, column=1, pady=2)
ctk.CTkLabel(control_frame, text="Aggregation").grid(row=0, column=2, pady=2)
ctk.CTkLabel(control_frame, text="Chart Type").grid(row=0, column=3, pady=2)

# ===== COMBO BOXES =====
group_combo = ctk.CTkComboBox(control_frame, width=150, values=[])
group_combo.set("Select")
group_combo.grid(row=1, column=0, padx=5)

value_combo = ctk.CTkComboBox(control_frame, width=150, values=[])
value_combo.set("Select")
value_combo.grid(row=1, column=1, padx=5)

agg_combo = ctk.CTkComboBox(
    control_frame,
    values=["sum", "mean", "max", "min", "count"],
    width=130
)
agg_combo.set("Select")
agg_combo.grid(row=1, column=2, padx=5)

chart_combo = ctk.CTkComboBox(
    control_frame,
    values=["bar", "line", "pie"],
    width=130
)
chart_combo.set("Select")
chart_combo.grid(row=1, column=3, padx=5)

# ===== BUTTON FRAME =====
btn_frame = ctk.CTkFrame(control_frame)
btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

# ROW 1
ctk.CTkButton(btn_frame, text="Generate", width=120, command=generate_report_ui).grid(row=0, column=0, padx=5)
ctk.CTkButton(btn_frame, text="Chart", width=120, command=draw_chart).grid(row=0, column=1, padx=5)
ctk.CTkButton(btn_frame, text="Export", width=120, command=export_report).grid(row=0, column=2, padx=5)

# ROW 2
ctk.CTkButton(btn_frame, text="Clear Table", width=120, command=clear_table).grid(row=1, column=0, padx=5, pady=5)
ctk.CTkButton(btn_frame, text="Clear Chart", width=120, command=clear_chart).grid(row=1, column=1, padx=5, pady=5)
ctk.CTkButton(btn_frame, text="Undo", width=120, command=undo_action).grid(row=1, column=2, padx=5, pady=5)
ctk.CTkButton(btn_frame, text="Reset", width=120, command=reset_app).grid(row=1, column=3, padx=5, pady=5)

# ---------- OUTPUT ----------
bottom = ctk.CTkFrame(main)
bottom.pack(fill="both", expand=True)

table_frame = ctk.CTkScrollableFrame(bottom)
table_frame.pack(side="left", fill="both", expand=True, padx=5)

chart_frame = ctk.CTkFrame(bottom)
chart_frame.pack(side="right", fill="both", expand=True, padx=5)

# ---------- STATUS BAR ----------
status_frame = ctk.CTkFrame(app, height=25)
status_frame.pack(side="bottom", fill="x")

status = ctk.CTkLabel(status_frame, text="Ready", anchor="w")
status.pack(fill="both", padx=10)

# ---------- RUN ----------
app.mainloop()