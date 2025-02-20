import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

# Constants for Styling
BG_COLOR = "#82B1FF"
BUTTON_COLORS = ["#4CAF50", "#F44336", "#2196F3", "#FFC107", "#9C27B0"]
HEADING_FONT = ("Helvetica", 16, "bold")
LABEL_FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 12)
TITLE_FONT = ("Helvetica", 20, "bold")

def create_db():
    conn = sqlite3.connect('students.db')  # Create a new database (or connect if it exists)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Function to verify login against the database
def verify_login():
    username = entry_username.get()
    password = entry_password.get()

    # Connect to the database
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # Query the database for the username and password
    cursor.execute('SELECT * FROM students WHERE username=? AND password=?', (username, password))
    result = cursor.fetchone()  # Fetch the first matching result

    if result:  # If a match is found
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        open_platform()  # Open the next window after successful login
    else:  # If no match found
        messagebox.showerror("Login Failed", "Invalid username or password.")

    conn.close()

# Function to toggle the password visibility
def toggle_password():
    if show_password_var.get():  # If the checkbox is checked
        entry_password.config(show="")  # Show the password
    else:
        entry_password.config(show="*")  # Hide the password

# Function to open the main platform window
def open_platform():
    # Close the login window
    login_window.destroy()

# Set up the main login window
login_window = tk.Tk()
login_window.title("Student Login")
login_window.geometry("600x600")

# Load and set the background image
background_image_path = r"C:\Users\adeline lambin\Downloads\télécharger.jpg"
image = Image.open(background_image_path)
resized_image = image.resize((600, 600), Image.Resampling.LANCZOS)
background_image = ImageTk.PhotoImage(resized_image)
background_label = tk.Label(login_window, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Calculate the center positions dynamically
window_width = 600
window_height = 600
center_x = window_width // 2
center_y = window_height // 2

# Adjustments for field positioning
label_offset_y = -50
entry_offset_y = -20
button_offset_y = 30

# Create and place the username and password labels and entry fields
label_username = tk.Label(login_window, text="Username:", font=("Arial", 14), bg="white")
label_username.place(x=center_x - 100, y=center_y + label_offset_y)

entry_username = tk.Entry(login_window, font=("Arial", 14))
entry_username.place(x=center_x, y=center_y + label_offset_y, width=200)

label_password = tk.Label(login_window, text="Password:", font=("Arial", 14), bg="white")
label_password.place(x=center_x - 100, y=center_y + entry_offset_y)

entry_password = tk.Entry(login_window, show="*", font=("Arial", 14))  # Hide password characters
entry_password.place(x=center_x, y=center_y + entry_offset_y, width=200)

# Add "Show Password" checkbox
show_password_var = tk.BooleanVar()
show_password_checkbox = tk.Checkbutton(
    login_window,
    text="Show Password",
    variable=show_password_var,
    command=toggle_password,
    bg="white",
    font=("Arial", 12)
)
show_password_checkbox.place(x=center_x - 50, y=center_y + entry_offset_y + 30)

# Create and place the login button
login_button = tk.Button(login_window, text="Login", command=verify_login, font=("Arial", 14))
login_button.place(x=center_x - 50, y=center_y + button_offset_y + 30, width=100)

# Initialize database (create table and sample data)
create_db()

# Start the Tkinter event loop for the login window
login_window.mainloop()

# Database Setup
def connect_db():
    return sqlite3.connect('marks.db')


def create_tables():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT,
            gender TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            module_code TEXT PRIMARY KEY,
            module_name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            student_id TEXT,
            module_code TEXT,
            coursework1 REAL,
            coursework2 REAL,
            coursework3 REAL,
            date_of_entry TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(module_code) REFERENCES modules(module_code)
        )
    ''')
    conn.commit()
    conn.close()


# Utility Functions
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()


def validate_entries(entries):
    """Validate all form entries."""
    for label, widget in entries.items():
        if isinstance(widget, tk.Entry) and not widget.get().strip():
            messagebox.showerror('Validation Error', f'{label} cannot be empty')
            return False
        if label.startswith('Coursework') and not widget.get().isdigit():
            messagebox.showerror('Validation Error', f'{label} must be a number')
            return False
    return True


def validate_module_code(module_code):
    """Validate if the Module Code is not empty and properly formatted."""
    if not module_code.strip():
        messagebox.showerror('Validation Error', 'Module Code cannot be empty')
        return False
    if len(module_code) > 10:
        messagebox.showerror('Validation Error', 'Module Code is too long (max 10 characters)')
        return False
    return True

# Home Page with Stats
def show_home():
    clear_frame()
    tk.Label(content_frame, text='Records and Statistics', font=TITLE_FONT, bg=BG_COLOR).pack(pady=10)
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Total Students and Modules
        cursor.execute('SELECT COUNT(DISTINCT student_id) FROM marks')
        total_students = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT module_code) FROM marks')
        total_modules = cursor.fetchone()[0]
        
        # Average, Highest, and Lowest Marks
        cursor.execute('SELECT AVG(coursework1 + coursework2 + coursework3) FROM marks')
        avg_marks = cursor.fetchone()[0] or 0
        cursor.execute('SELECT MAX(coursework1 + coursework2 + coursework3) FROM marks')
        max_marks = cursor.fetchone()[0] or 0
        cursor.execute('SELECT MIN(coursework1 + coursework2 + coursework3) FROM marks')
        min_marks = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Display Dashboard Stats
        stats = [
            f"Total Students: {total_students}",
            f"Total Modules: {total_modules}",
            f"Average Marks: {avg_marks:.2f}",
            f"Highest Marks: {max_marks}",
            f"Lowest Marks: {min_marks}"
        ]
        
        for stat in stats:
            tk.Label(content_frame, text=stat, font=LABEL_FONT, bg=BG_COLOR).pack(pady=5)
    
    except Exception as e:
        messagebox.showerror('Error', f'Database Error: {e}')

# Input Marks Page
def input_mark_page():
    clear_frame()
    
    # Main Title
    tk.Label(content_frame, text="Input Marks", font=("Helvetica", 18, "bold"), bg=BG_COLOR).pack(pady=3)
    
    # Centered Form Frame
    form_frame = tk.Frame(content_frame, bg=BG_COLOR)
    form_frame.pack(expand=True, pady=0)
    form_frame.pack_propagate(False)
    form_frame.config(height=900, width=200) 
    
    entries = {}
    labels = [
        'Student ID', 'Student Name', 'Module Code', 'Module Name',
        'Coursework Mark 1', 'Coursework Mark 2', 'Coursework Mark 3',
        'Gender', 'Date of Entry'
    ]
    
    for label in labels:
        # Label
        tk.Label(form_frame, text=label + ":", font=("Helvetica", 10), bg=BG_COLOR, anchor='w').pack(pady=3)
        
        # Input Fields
        if label == 'Gender':
            gender_var = tk.StringVar(value="Select Gender")
            combobox = ttk.Combobox(form_frame, textvariable=gender_var, values=["Male", "Female"], font=("Helvetica", 10))
            combobox.pack(pady=3, ipadx=5, ipady=2)
            entries['Gender'] = gender_var
        
        elif label == 'Date of Entry':
            date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd', font=("Helvetica", 10))
            date_entry.pack(pady=3, ipadx=5, ipady=2)
            entries['Date of Entry'] = date_entry
        
        else:
            entry = tk.Entry(form_frame, font=("Helvetica", 10), relief='solid')
            entry.pack(pady=3, ipadx=5, ipady=2)
            entries[label] = entry
    
    # Button Frame
    button_frame = tk.Frame(form_frame, bg=BG_COLOR)
    button_frame.pack(pady=10)
    
    # Submit Button
    tk.Button(
        button_frame, 
        text='Submit', 
        command=lambda: submit_marks(entries), 
        bg=BUTTON_COLORS[2], 
        fg="white", 
        font=("Helvetica", 10),
        relief='flat',
        width=12
    ).grid(row=0, column=0, padx=5)
    
    # Reset Button
    tk.Button(
        button_frame, 
        text='Reset', 
        command=lambda: reset_form(entries), 
        bg=BUTTON_COLORS[1], 
        fg="white", 
        font=("Helvetica", 10),
        relief='flat',
        width=12
    ).grid(row=0, column=1, padx=5)


def validate_marks(entries):
    """Validate if coursework marks are between 0 and 100."""
    try:
        cw1 = float(entries['Coursework Mark 1'].get())
        cw2 = float(entries['Coursework Mark 2'].get())
        cw3 = float(entries['Coursework Mark 3'].get())
        
        if not (0 <= cw1 <= 100):
            raise ValueError("Coursework Mark 1 must be between 0 and 100.")
        if not (0 <= cw2 <= 100):
            raise ValueError("Coursework Mark 2 must be between 0 and 100.")
        if not (0 <= cw3 <= 100):
            raise ValueError("Coursework Mark 3 must be between 0 and 100.")
        
        return True  # Validation passed
    
    except ValueError as e:
        messagebox.showerror('Validation Error', str(e))
        return False

def submit_marks(entries):
    """Handle submission of marks."""
    # Validate inputs
    if not all(entries[label].get().strip() for label in entries if isinstance(entries[label], tk.Entry)):
        messagebox.showerror('Validation Error', 'All fields must be filled out.')
        return

    if not validate_marks(entries):
        return  # Stop submission if marks are invalid

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Check if the student ID already exists
        cursor.execute('SELECT student_name FROM students WHERE student_id = ?', (entries['Student ID'].get(),))
        student = cursor.fetchone()

        if student:
            # Notify the user that the Student ID already exists
            student_name = student[0]
            messagebox.showinfo(
                'Student Exists',
                f"Student ID '{entries['Student ID'].get()}' already exists for '{student_name}'."
            )
            return  # Stop further execution if the student already exists

        # Insert new student if it doesn't exist
        cursor.execute('''
            INSERT INTO students (student_id, student_name, gender)
            VALUES (?, ?, ?)
        ''', (
            entries['Student ID'].get(),
            entries['Student Name'].get(),
            entries['Gender'].get()
        ))
        print(f"New student with ID {entries['Student ID'].get()} added.")

        # Check if the module already exists
        cursor.execute('SELECT module_name FROM modules WHERE module_code = ?', (entries['Module Code'].get(),))
        module = cursor.fetchone()

        if not module:
            # Insert new module if it doesn't exist
            cursor.execute('''
                INSERT INTO modules (module_code, module_name)
                VALUES (?, ?)
            ''', (
                entries['Module Code'].get(),
                entries['Module Name'].get()
            ))
            print(f"New module with code {entries['Module Code'].get()} added.")
        else:
            print(f"Module with code {entries['Module Code'].get()} already exists.")

        # Check if the marks for this student and module already exist
        cursor.execute('''
            SELECT 1 FROM marks WHERE student_id = ? AND module_code = ?
        ''', (entries['Student ID'].get(), entries['Module Code'].get()))
        mark_exists = cursor.fetchone()

        if not mark_exists:
            # Insert marks if they don't already exist
            cursor.execute('''
                INSERT INTO marks (student_id, module_code, coursework1, coursework2, coursework3, date_of_entry)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entries['Student ID'].get(),
                entries['Module Code'].get(),
                float(entries['Coursework Mark 1'].get()),
                float(entries['Coursework Mark 2'].get()),
                float(entries['Coursework Mark 3'].get()),
                entries['Date of Entry'].get()
            ))
            conn.commit()
            messagebox.showinfo('Success', 'Records added successfully!')
        else:
            messagebox.showwarning(
                'Duplicate Marks',
                f"Marks for Student ID '{entries['Student ID'].get()}' and Module Code '{entries['Module Code'].get()}' already exist."
            )

    except sqlite3.IntegrityError as e:
        messagebox.showerror('Integrity Error', str(e))
    except ValueError:
        messagebox.showerror('Input Error', 'Coursework Marks must be valid numbers.')
    except Exception as e:
        messagebox.showerror('Database Error', str(e))
    finally:
        conn.close()

def reset_form(entries):
    """Reset all form fields."""
    for label, widget in entries.items():
        if isinstance(widget, tk.Entry):
            widget.delete(0, 'end')
        elif isinstance(widget, ttk.Combobox):
            widget.set('Select Gender')
        elif isinstance(widget, DateEntry):
            widget.set_date('2000-01-01')

# Update Marks Page
def update_mark_page():
    clear_frame()
    
    # Main Title
    tk.Label(content_frame, text="Update Marks", font=("Helvetica", 18, "bold"), bg=BG_COLOR).pack(pady=3)
    
    # Centered Form Frame
    form_frame = tk.Frame(content_frame, bg=BG_COLOR)
    form_frame.pack(expand=True, pady=4)
    
    entries = {}
    labels = [
        'Module Code', 'Student ID', 'Date of Entry',
        'Course Work 1', 'Course Work 2', 'Course Work 3'
    ]
    
    for label in labels:
        # Label
        tk.Label(form_frame, text=label + ":", font=("Helvetica", 10), bg=BG_COLOR, anchor='w').pack(pady=0)
        
        # Input Fields
        if label == 'Date of Entry':
            date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd', font=("Helvetica", 10))
            date_entry.pack(pady=0, ipadx=2, ipady=2)
            entries['Date of Entry'] = date_entry
        else:
            entry = tk.Entry(form_frame, font=("Helvetica", 10), relief='solid')
            entry.pack(pady=1, ipadx=5, ipady=2)
            entries[label] = entry
    
    # Button Frame
    button_frame = tk.Frame(form_frame, bg=BG_COLOR)
    button_frame.pack(pady=9)
    
    # Search Button
    tk.Button(
        button_frame, 
        text='Search', 
        command=lambda: search_marks(entries), 
        bg=BUTTON_COLORS[1], 
        fg="white", 
        font=("Helvetica", 10),
        relief='flat',
        width=10
    ).grid(row=0, column=0, padx=5)
    
    # Update Button
    tk.Button(
        button_frame, 
        text='Update', 
        command=lambda: update_marks(entries), 
        bg=BUTTON_COLORS[2], 
        fg="white", 
        font=("Helvetica", 10),
        relief='flat',
        width=10
    ).grid(row=0, column=1, padx=5)
    
    # Reset Button
    tk.Button(
        button_frame, 
        text='Reset', 
        command=lambda: reset_form(entries), 
        bg=BUTTON_COLORS[3], 
        fg="white", 
        font=("Helvetica", 10),
        relief='flat',
        width=10
    ).grid(row=0, column=2, padx=5)

# Search Marks Function
def search_marks(entries):
    """Search for marks based on Student ID, Module Code, and Date."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT coursework1, coursework2, coursework3
            FROM marks 
            WHERE student_id = ? AND module_code = ? AND date_of_entry = ?
        ''', (
            entries['Student ID'].get(),
            entries['Module Code'].get(),
            entries['Date of Entry'].get()
        ))
        result = cursor.fetchone()
        
        if result:
            entries['Course Work 1'].delete(0, 'end')
            entries['Course Work 2'].delete(0, 'end')
            entries['Course Work 3'].delete(0, 'end')
            
            entries['Course Work 1'].insert(0, result[0])
            entries['Course Work 2'].insert(0, result[1])
            entries['Course Work 3'].insert(0, result[2])
            
            messagebox.showinfo('Success', 'Record found!')
        else:
            messagebox.showwarning('Not Found', 'No record matches the search criteria.')
    except Exception as e:
        messagebox.showerror('Error', f'Database Error: {e}')
    finally:
        conn.close()

# Update Marks Function
def update_marks(entries):
    """Update marks in the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE marks
            SET coursework1 = ?, coursework2 = ?, coursework3 = ?
            WHERE student_id = ? AND module_code = ? AND date_of_entry = ?
        ''', (
            float(entries['Course Work 1'].get()),
            float(entries['Course Work 2'].get()),
            float(entries['Course Work 3'].get()),
            entries['Student ID'].get(),
            entries['Module Code'].get(),
            entries['Date of Entry'].get()
        ))
        
        if cursor.rowcount > 0:
            conn.commit()
            messagebox.showinfo('Success', 'Marks updated successfully!')
        else:
            messagebox.showwarning('Update Failed', 'No matching record found to update.')
    except ValueError:
        messagebox.showerror('Input Error', 'Coursework Marks must be valid numbers.')
    except Exception as e:
        messagebox.showerror('Error', f'Database Error: {e}')
    finally:
        conn.close()

# Reset Form Function
def reset_form(entries):
    """Reset all form fields."""
    for label, widget in entries.items():
        if isinstance(widget, tk.Entry):
            widget.delete(0, 'end')
        elif isinstance(widget, DateEntry):
            widget.set_date('2000-01-01')

def view_mark_page():
    clear_frame()
    tk.Label(content_frame, text="View Marks", font=HEADING_FONT, bg=BG_COLOR).pack(pady=10)
    
    # 🌟 Frame for Input and Button
    input_frame = tk.Frame(content_frame, bg=BG_COLOR)
    input_frame.pack(pady=5)

    tk.Label(input_frame, text='Module Code:', font=LABEL_FONT, bg=BG_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky='e')
    module_code_entry = tk.Entry(input_frame, font=LABEL_FONT, width=20)
    module_code_entry.grid(row=0, column=1, padx=5, pady=5)

    def view_marks():
        module_code = module_code_entry.get().strip()
        if not validate_module_code(module_code):
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.student_id, s.student_name, m.coursework1, m.coursework2, m.coursework3,
                       (m.coursework1 + m.coursework2 + m.coursework3) AS total_marks
                FROM marks m
                JOIN students s ON m.student_id = s.student_id
                WHERE m.module_code = ?
            ''', (module_code,))
            
            rows = cursor.fetchall()
            tree.delete(*tree.get_children())  # Clear previous entries
            
            if rows:
                for index, row in enumerate(rows):
                    tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                    tree.insert('', 'end', values=row, tags=(tag,))
                messagebox.showinfo('Success', f'{len(rows)} records found for Module Code: {module_code}')
            else:
                messagebox.showwarning('No Records', f'No records found for Module Code: {module_code}')
        except Exception as e:
            messagebox.showerror('Error', f'Database Error: {e}')
        finally:
            conn.close()
    
    tk.Button(
        input_frame, text='View', command=view_marks,
        bg=BUTTON_COLORS[1], fg="white", font=BUTTON_FONT, width=10
    ).grid(row=0, column=2, padx=5, pady=5)

    # 🌟 Table Frame for Centered Table
    table_frame = tk.Frame(content_frame, bg=BG_COLOR, height=500, width=1000)
    table_frame.pack(pady=10)
    table_frame.pack_propagate(False)

    # 🌟 Scrollable Canvas for Table
    canvas = tk.Canvas(table_frame, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(side='left', fill='both', expand=True)
    
    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')
    
    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
    canvas.create_window((0, 0), window=scrollable_frame, anchor='n')
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # 🌟 Table Configuration
    columns = ('Student ID', 'Student Name', 'Coursework 1', 'Coursework 2', 'Coursework 3', 'Total Marks')
    column_widths = [150, 200, 150, 150, 150, 200]  # Adjustable column widths
    
    tree = ttk.Treeview(scrollable_frame, columns=columns, show='headings', height=15)
    tree.pack(fill='both', expand=True)
    
    for col, width in zip(columns, column_widths):
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=width)

    # 🌟 Styling for Table
    style = ttk.Style()
    style.theme_use("clam")  # Clean theme for better visuals

    ## 📊 Header Styling
    style.configure(
        "Treeview.Heading",
        font=("Helvetica", 12, "bold"),
        background="#2C3E50",
        foreground="#FFFFFF",
        relief="raised"
    )

    ## 📊 Row Styling
    style.configure(
        "Treeview",
        font=("Helvetica", 11),
        rowheight=30,
        fieldbackground="#F5F5F5",
        background="#FFFFFF",
    )
    style.map(
        "Treeview",
        background=[('selected', '#26A69A')],
        foreground=[('selected', '#FFFFFF')]
    )

    ## 📊 Row Tag Styling
    tree.tag_configure('evenrow', background='#D0F0C0')
    tree.tag_configure('oddrow', background='#F9F9F9')

    ## 📊 Scrollbar Styling
    style.configure(
        "Vertical.TScrollbar",
        background="#D7CCC8",
        troughcolor="#EFEBE9",
        bordercolor="#5D4037"
    )

    # Adjust spacing to ensure alignment
    input_frame.columnconfigure(0, weight=1)
    input_frame.columnconfigure(1, weight=1)
    input_frame.columnconfigure(2, weight=1)
    table_frame.columnconfigure(0, weight=1)

def show_visualization():
    """Displays the Visualization page with data read from the SQLite database."""
    clear_frame()
    tk.Label(content_frame, text="Visualization", font=HEADING_FONT, bg=BG_COLOR).pack(pady=0)
    
    # 🌟 Dropdown to select visualization type
    options = [
        "Module Registrations", "Student Performance", "Date of Entry",
        "Coursework Distribution (Box Plot)", "Gender Distribution (Pie Chart)"
    ]
    selected_option = tk.StringVar(value=options[0])
    
    dropdown_frame = tk.Frame(content_frame, bg=BG_COLOR)
    dropdown_frame.pack(pady=10)
    
    tk.Label(dropdown_frame, text="Select Visualization Type:", font=LABEL_FONT, bg=BG_COLOR).grid(row=0, column=0, padx=7)
    dropdown = ttk.Combobox(dropdown_frame, textvariable=selected_option, values=options, font=LABEL_FONT, state='readonly')
    dropdown.grid(row=0, column=1, padx=5)

    # 🌟 Canvas Frame for displaying the chart
    canvas_frame = tk.Frame(content_frame, bg=BG_COLOR, width=800, height=200)
    canvas_frame.pack(pady=10, fill="both", expand=True)
    canvas_frame.pack_propagate(False)

     # 🌟 Generate Visualization Button
    def generate_visualization():
        """Generates and displays the selected visualization based on SQLite data."""
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        
        conn = None
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 📊 Module Registrations
            if selected_option.get() == "Module Registrations":
                cursor.execute('SELECT module_code, COUNT(*) FROM marks GROUP BY module_code')
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showinfo("No Data", "No data available for Module Registrations.")
                    return
                labels, values = zip(*rows)
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.bar(labels, values, color="mediumseagreen")
                ax.set_title("Module Registrations", fontsize=12)
                ax.set_xlabel("Modules")
                ax.set_ylabel("Registrations")

            # 📊 Student Performance
            elif selected_option.get() == "Student Performance":
                cursor.execute('''
                    SELECT s.student_name, AVG(m.coursework1 + m.coursework2 + m.coursework3) / 3 AS average_marks
                    FROM marks m
                    JOIN students s ON m.student_id = s.student_id
                    GROUP BY s.student_name
                ''')
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showinfo("No Data", "No data available for Student Performance.")
                    return
                labels, values = zip(*rows)
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.bar(labels, values, color="dodgerblue")
                ax.set_title("Student Performance", fontsize=12)
                ax.set_xlabel("Students")
                ax.set_ylabel("Average Marks (%)")
                ax.tick_params(axis='x', rotation=45)

            # 📊 Date of Entry
            elif selected_option.get() == "Date of Entry":
                cursor.execute('SELECT date_of_entry, COUNT(*) FROM marks GROUP BY date_of_entry')
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showinfo("No Data", "No data available for Date of Entry.")
                    return
                labels, values = zip(*rows)
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(labels, values, marker="o", linestyle="-", color="darkorange")
                ax.set_title("Entries by Date", fontsize=12)
                ax.set_xlabel("Dates")
                ax.set_ylabel("Number of Entries")
                fig.autofmt_xdate(rotation=45)

            # 📊 Coursework Distribution
            elif selected_option.get() == "Coursework Distribution (Box Plot)":
                cursor.execute('SELECT coursework1, coursework2, coursework3 FROM marks')
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showinfo("No Data", "No data available for Coursework Distribution.")
                    return
                df = pd.DataFrame(rows, columns=['Coursework 1', 'Coursework 2', 'Coursework 3'])
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.boxplot(data=df, ax=ax, palette="coolwarm")
                ax.set_title("Coursework Distribution (Box Plot)", fontsize=12)
                ax.set_xlabel("Coursework")
                ax.set_ylabel("Marks")

            # 📊 Gender Distribution
            elif selected_option.get() == "Gender Distribution (Pie Chart)":
                cursor.execute('SELECT gender, COUNT(*) FROM students GROUP BY gender')
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showinfo("No Data", "No data available for Gender Distribution.")
                    return
                labels, values = zip(*rows)
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                ax.set_title("Gender Distribution", fontsize=12)

            else:
                messagebox.showerror("Error", "Invalid visualization type selected.")
                return

            # 🌟 Display Chart in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

            messagebox.showinfo("Success", f"{selected_option.get()} visualization displayed successfully!")

        except sqlite3.Error as db_err:
            messagebox.showerror("Database Error", f"Failed to query database: {db_err}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate visualization. Error: {e}")

        finally:
            if conn:
                conn.close()

    # 🌟 Button to Generate Visualization
    button_frame = tk.Frame(content_frame, bg="#FFE0B2")
    button_frame.pack(pady=5)

    tk.Button(
        button_frame,
        text="Generate Visualization",
        font=("Helvetica", 12),
        bg="#81C784",
        fg="white",
        command=generate_visualization,
        width=20
    ).pack()

# Main Window
root = tk.Tk()
root.title('Student  Mark  Management')
root.geometry('900x600')
root.config(bg=BG_COLOR)

# Global Widget Styling
root.option_add('*Entry.background', 'white')
root.option_add('*Entry.foreground', 'black')
root.option_add('*DateEntry.background', 'white')
root.option_add('*DateEntry.foreground', 'black')

tk.Label(root, text='Student Mark System', font=("Helvetica", 30, "bold"), bg=BG_COLOR).pack(pady=2)

nav_frame = tk.Frame(root, bg=BG_COLOR)
nav_frame.pack(pady=30)

buttons = [
    ('Home', show_home),
    ('Input Marks', input_mark_page),
    ('Update Marks', update_mark_page),
    ('View Marks', view_mark_page),
     ("Visualization", show_visualization),
]

for i, (text, command) in enumerate(buttons):
    tk.Button(
        nav_frame,
        text=text,
        command=command,
        bg=BUTTON_COLORS[i % len(BUTTON_COLORS)],
        fg="white",
        font=("Helvetica", 12, "bold"),  # Increased font size
        width=12,  # Increased button width
        height=1,  # Increased button height
        relief="raised",
        borderwidth=2
    ).pack(side='left', padx=10)  

content_frame = tk.Frame(root, bg=BG_COLOR)
content_frame.pack(expand=True, fill='both', padx=20, pady=10)

create_tables()
show_home()
root.mainloop()