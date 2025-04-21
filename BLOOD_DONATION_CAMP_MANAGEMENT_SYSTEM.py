import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import re

# Color scheme
COLOR_PRIMARY = "#2c3e50"    # Dark blue
COLOR_SECONDARY = "#3498db"  # Bright blue
COLOR_LIGHT = "#ecf0f1"      # Light grey
COLOR_DARK = "#34495e"       # Dark grey
COLOR_SUCCESS = "#27ae60"    # Green
COLOR_WARNING = "#e74c3c"    # Red

# Database initialization
def init_db():
    conn = sqlite3.connect('blood_donation.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')  # Enable foreign key support
    
    # Create Organizers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Organizers (
        organizer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        organizer_name TEXT NOT NULL,
        contact_number TEXT NOT NULL
    )''')

    # Create Camps table with correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Camps (
        camp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        camp_name TEXT NOT NULL,
        location TEXT NOT NULL,
        date TEXT NOT NULL,
        organizer_id INTEGER NOT NULL,
        FOREIGN KEY (organizer_id) REFERENCES Organizers(organizer_id)
    )''')

    # Create Donor_Info table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Donor_Info (
        donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        contact_number TEXT NOT NULL
    )''')

    # Create Donations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Donations (
        donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        camp_id INTEGER NOT NULL,
        FOREIGN KEY (donor_id) REFERENCES Donor_Info(donor_id),
        FOREIGN KEY (camp_id) REFERENCES Camps(camp_id)
    )''')

    conn.commit()
    conn.close()

init_db()

class BloodDonationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Donation Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg=COLOR_PRIMARY)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_header()
        self.create_input_section()
        self.create_view_section()

    def _configure_styles(self):
        self.style.configure('TFrame', background=COLOR_LIGHT)
        self.style.configure('TLabel', background=COLOR_LIGHT, foreground=COLOR_DARK, 
                           font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6,
                           background=COLOR_SECONDARY, foreground='white')
        self.style.configure('Treeview', font=('Segoe UI', 9), rowheight=30, 
                           fieldbackground=COLOR_LIGHT, background=COLOR_LIGHT)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), 
                           background=COLOR_PRIMARY, foreground='white')
        self.style.configure('Header.TLabel', background=COLOR_PRIMARY, 
                           foreground='white', font=('Segoe UI', 14, 'bold'))
        self.style.configure('Input.TFrame', background=COLOR_LIGHT, 
                           relief=tk.RAISED, borderwidth=1)

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="Blood Donation Management System", 
                 style='Header.TLabel').pack(pady=10)

    def create_input_section(self):
        input_frame = ttk.Frame(self.main_frame, style='Input.TFrame')
        input_frame.pack(fill=tk.X, pady=5)
        
        # Camp Input
        camp_frame = ttk.LabelFrame(input_frame, text=" New Camp ", style='Input.TFrame')
        camp_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        camp_fields = [
            ("Organizer Name:", 'organizer_name'),
            ("Organizer Contact:", 'organizer_contact'),
            ("Camp Name:", 'camp_name'),
            ("Location:", 'location'),
            ("Date (YYYY-MM-DD):", 'date')
        ]
        
        for i, (text, var) in enumerate(camp_fields):
            ttk.Label(camp_frame, text=text).grid(row=i, column=0, sticky='e', padx=2, pady=2)
            entry = ttk.Entry(camp_frame, width=20, font=('Segoe UI', 9))
            entry.grid(row=i, column=1, padx=2, pady=2)
            setattr(self, f'entry_{var}', entry)
            
        ttk.Button(camp_frame, text="Add Camp", command=self.add_camp)\
            .grid(row=5, columnspan=2, pady=5)

        # Separator
        ttk.Separator(input_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Donor Input
        donor_frame = ttk.LabelFrame(input_frame, text=" New Donor ", style='Input.TFrame')
        donor_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        donor_fields = [
            ("Donor Name:", 'donor_name'),
            ("Age:", 'age'),
            ("Blood Group:", 'blood_group'),
            ("Contact:", 'donor_contact'),
            ("Camp ID:", 'camp_id')
        ]
        
        for i, (text, var) in enumerate(donor_fields):
            ttk.Label(donor_frame, text=text).grid(row=i, column=0, sticky='e', padx=2, pady=2)
            entry = ttk.Entry(donor_frame, width=20, font=('Segoe UI', 9))
            entry.grid(row=i, column=1, padx=2, pady=2)
            setattr(self, f'entry_{var}', entry)
            
        ttk.Button(donor_frame, text="Add Donor", command=self.add_donor)\
            .grid(row=5, columnspan=2, pady=5)

    def create_view_section(self):
        view_frame = ttk.Frame(self.main_frame, style='Input.TFrame')
        view_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Camps List
        camps_frame = ttk.LabelFrame(view_frame, text=" Camps ", style='Input.TFrame')
        camps_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.camps_tree = ttk.Treeview(camps_frame, columns=('ID', 'Camp Name', 'Location', 'Date', 'Organizer'), 
                                     show='headings', height=8)
        for col, width in [('ID', 50), ('Camp Name', 150), ('Location', 100), ('Date', 100), ('Organizer', 150)]:
            self.camps_tree.column(col, width=width, anchor=tk.CENTER)
            self.camps_tree.heading(col, text=col)
        self.camps_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(camps_frame, text="Refresh", command=self.view_camps)\
            .pack(pady=2)

        # Separator
        ttk.Separator(view_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Donors List
        donors_frame = ttk.LabelFrame(view_frame, text=" Donors ", style='Input.TFrame')
        donors_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.donors_tree = ttk.Treeview(donors_frame, columns=('ID', 'Name', 'Age', 'Blood Group'), 
                                      show='headings', height=8)
        for col, width in [('ID', 50), ('Name', 150), ('Age', 50), ('Blood Group', 80)]:
            self.donors_tree.column(col, width=width, anchor=tk.CENTER)
            self.donors_tree.heading(col, text=col)
        self.donors_tree.pack(fill=tk.BOTH, expand=True)
        
        search_frame = ttk.Frame(donors_frame)
        search_frame.pack(pady=2)
        ttk.Label(search_frame, text="Camp ID:").pack(side=tk.LEFT)
        self.entry_view_camp_id = ttk.Entry(search_frame, width=10, font=('Segoe UI', 9))
        self.entry_view_camp_id.pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Show", command=self.view_donors)\
            .pack(side=tk.LEFT)

    def validate_date(self, date_str):
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        return re.match(pattern, date_str) is not None

    def add_camp(self):
        organizer_name = self.entry_organizer_name.get().strip()
        organizer_contact = self.entry_organizer_contact.get().strip()
        camp_name = self.entry_camp_name.get().strip()
        location = self.entry_location.get().strip()
        date = self.entry_date.get().strip()

        if not all([organizer_name, organizer_contact, camp_name, location, date]):
            messagebox.showwarning("Error", "All camp fields are required!", parent=self.root)
            return

        if not self.validate_date(date):
            messagebox.showwarning("Error", "Invalid date format! Use YYYY-MM-DD", parent=self.root)
            return

        try:
            conn = sqlite3.connect('blood_donation.db')
            cursor = conn.cursor()
            
            # Add organizer
            cursor.execute('''
                INSERT INTO Organizers (organizer_name, contact_number)
                VALUES (?, ?)
            ''', (organizer_name, organizer_contact))
            organizer_id = cursor.lastrowid
            
            # Add camp
            cursor.execute('''
                INSERT INTO Camps (camp_name, location, date, organizer_id)
                VALUES (?, ?, ?, ?)
            ''', (camp_name, location, date, organizer_id))
            
            conn.commit()
            messagebox.showinfo("Success", "Camp added successfully!", parent=self.root)
            self.clear_camp_fields()
            self.view_camps()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}", parent=self.root)
        finally:
            conn.close()

    def add_donor(self):
        donor_name = self.entry_donor_name.get().strip()
        age = self.entry_age.get().strip()
        blood_group = self.entry_blood_group.get().strip().upper()
        contact = self.entry_donor_contact.get().strip()
        camp_id = self.entry_camp_id.get().strip()

        if not all([donor_name, age, blood_group, contact, camp_id]):
            messagebox.showwarning("Error", "All donor fields are required!", parent=self.root)
            return

        try:
            age = int(age)
            camp_id = int(camp_id)
            valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            
            if age < 18 or age > 65:
                raise ValueError("Age must be between 18-65")
            if blood_group not in valid_groups:
                raise ValueError("Invalid blood group. Valid formats: A+, B-, etc.")
            
            conn = sqlite3.connect('blood_donation.db')
            cursor = conn.cursor()
            
            # Add donor info
            cursor.execute('''
                INSERT INTO Donor_Info (donor_name, age, blood_group, contact_number)
                VALUES (?, ?, ?, ?)
            ''', (donor_name, age, blood_group, contact))
            donor_id = cursor.lastrowid
            
            # Add donation record
            cursor.execute('''
                INSERT INTO Donations (donor_id, camp_id)
                VALUES (?, ?)
            ''', (donor_id, camp_id))
            
            conn.commit()
            messagebox.showinfo("Success", "Donor added successfully!", parent=self.root)
            self.clear_donor_fields()
            self.view_donors()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve), parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}", parent=self.root)
        finally:
            conn.close()

    def view_camps(self):
        try:
            conn = sqlite3.connect('blood_donation.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.camp_id, c.camp_name, c.location, c.date, o.organizer_name
                FROM Camps c
                JOIN Organizers o ON c.organizer_id = o.organizer_id
            ''')
            
            self.camps_tree.delete(*self.camps_tree.get_children())
            for row in cursor.fetchall():
                self.camps_tree.insert('', 'end', values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}", parent=self.root)
        finally:
            conn.close()

    def view_donors(self):
        camp_id = self.entry_view_camp_id.get().strip()
        if not camp_id:
            messagebox.showwarning("Error", "Please enter Camp ID", parent=self.root)
            return

        try:
            camp_id = int(camp_id)
            conn = sqlite3.connect('blood_donation.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT d.donor_id, d.donor_name, d.age, d.blood_group
                FROM Donor_Info d
                JOIN Donations dn ON d.donor_id = dn.donor_id
                WHERE dn.camp_id = ?
            ''', (camp_id,))
            
            self.donors_tree.delete(*self.donors_tree.get_children())
            for row in cursor.fetchall():
                self.donors_tree.insert('', 'end', values=row)
        except ValueError:
            messagebox.showerror("Error", "Invalid Camp ID format", parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}", parent=self.root)
        finally:
            conn.close()

    def clear_camp_fields(self):
        self.entry_organizer_name.delete(0, tk.END)
        self.entry_organizer_contact.delete(0, tk.END)
        self.entry_camp_name.delete(0, tk.END)
        self.entry_location.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)

    def clear_donor_fields(self):
        self.entry_donor_name.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.entry_blood_group.delete(0, tk.END)
        self.entry_donor_contact.delete(0, tk.END)
        self.entry_camp_id.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BloodDonationApp(root)
    root.mainloop()
