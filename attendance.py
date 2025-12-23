import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

class AdvancedAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Attendance Tracker")
        self.root.geometry("950x750")

        # Database Connection
        try:
            self.db = mysql.connector.connect(
                host="localhost", user="root", password="12345", 
                database="attendance_db", autocommit=True
            )
            self.cursor = self.db.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            self.root.destroy()

        self.create_widgets()
        self.update_clock()

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill="x")
        
        tk.Label(header, text="ATTENDANCE DASHBOARD", fg="white", bg="#2c3e50", 
                 font=("Arial", 18, "bold")).pack(side="left", padx=20, pady=15)

        self.clock_label = tk.Label(header, text="", fg="#f1c40f", bg="#2c3e50", 
                                    font=("Arial", 14, "bold"))
        self.clock_label.pack(side="right", padx=20, pady=15)

        # Employee Registration Section
        reg_frame = tk.LabelFrame(self.root, text="Register New Employee", padx=10, pady=10, fg="#2980b9", font=("Arial", 10, "bold"))
        reg_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(reg_frame, text="New ID:").grid(row=0, column=0)
        self.new_id_ent = tk.Entry(reg_frame, width=10)
        self.new_id_ent.grid(row=0, column=1, padx=5)

        tk.Label(reg_frame, text="Full Name:").grid(row=0, column=2, padx=5)
        self.new_name_ent = tk.Entry(reg_frame, width=25)
        self.new_name_ent.grid(row=0, column=3, padx=5)

        tk.Button(reg_frame, text="ADD EMPLOYEE", bg="#3498db", fg="white", 
                  command=self.auto_insert_employee).grid(row=0, column=4, padx=10)

        # Control Panel (Login/Logout)
        ctrl_frame = tk.LabelFrame(self.root, text="Daily Attendance", padx=10, pady=10, fg="#27ae60", font=("Arial", 10, "bold"))
        ctrl_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(ctrl_frame, text="Employee ID:").grid(row=0, column=0)
        self.ent_id = tk.Entry(ctrl_frame, font=("Arial", 12))
        self.ent_id.grid(row=0, column=1, padx=10)

        tk.Button(ctrl_frame, text="LOGIN", bg="#27ae60", fg="white", width=10, 
                  command=self.process_login).grid(row=0, column=2, padx=5)
        tk.Button(ctrl_frame, text="LOGOUT", bg="#c0392b", fg="white", width=10, 
                  command=self.process_logout).grid(row=0, column=3, padx=5)

        # History Filters
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5)
        
        tk.Button(filter_frame, text="Today", width=12, command=lambda: self.load_data("today")).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Yesterday", width=12, command=lambda: self.load_data("yesterday")).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Full History", width=12, command=lambda: self.load_data("all")).pack(side="left", padx=5)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Date", "Login", "Logout", "Hours", "Status"), show='headings')
        for col in ("ID", "Name", "Date", "Login", "Logout", "Hours", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_data("all")

    def auto_insert_employee(self):
        eid = self.new_id_ent.get()
        ename = self.new_name_ent.get()
        if not eid or not ename:
            messagebox.showwarning("Input Error", "Provide both ID and Name.")
            return
        try:
            self.cursor.execute("INSERT INTO employees (emp_id, name) VALUES (%s, %s)", (eid, ename))
            messagebox.showinfo("Success", f"Registered {ename}")
            self.new_id_ent.delete(0, tk.END)
            self.new_name_ent.delete(0, tk.END)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Duplicate ID or Database Error: {err}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d  |  %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def load_data(self, period):
        # 1. Clear existing items in the table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. Define the SQL string (Standardize as 'query')
        if period == "today":
            query = "SELECT a.emp_id, e.name, a.date, a.login_time, a.logout_time, a.work_hours, a.status FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.date = CURDATE()"
        elif period == "yesterday":
            query = "SELECT a.emp_id, e.name, a.date, a.login_time, a.logout_time, a.work_hours, a.status FROM attendance a JOIN employees e ON a.emp_id = e.emp_id WHERE a.date = SUBDATE(CURDATE(), 1)"
        else:
            query = "SELECT a.emp_id, e.name, a.date, a.login_time, a.logout_time, a.work_hours, a.status FROM attendance a JOIN employees e ON a.emp_id = e.emp_id ORDER BY a.date DESC"

        # 3. Execute the standardized variable
        self.cursor.execute(query) 
        
        for row in self.cursor.fetchall():
            # Format times for display
            lin = row['login_time'].strftime('%I:%M %p') if row['login_time'] else "-"
            lout = row['logout_time'].strftime('%I:%M %p') if row['logout_time'] else "-"
            
            # 🕒 Convert Decimal Hours to Hours and Minutes for display
            dec_hours = float(row['work_hours'])
            h = int(dec_hours)
            m = int((dec_hours - h) * 60)
            display_duration = f"{h}h {m}m" if lout != "-" else "Active"
            
            self.tree.insert("", "end", values=(
                row['emp_id'], 
                row['name'], 
                row['date'], 
                lin, 
                lout, 
                display_duration, 
                row['status']
            ))
            
            
    def process_login(self):
        emp_id = self.ent_id.get()
        
        # 1. Check if the ID field is empty
        if not emp_id: 
            messagebox.showwarning("Input Error", "Please enter an Employee ID.")
            return

        try:
            now = datetime.now()
            # 2. Attempt to insert the login record
            self.cursor.execute(
                "INSERT INTO attendance (emp_id, date, login_time) VALUES (%s, %s, %s)", 
                (emp_id, now.date(), now)
            )
            self.db.commit() # Save changes
            
            messagebox.showinfo("Success", f"Login Recorded at {now.strftime('%H:%M:%S')}")
            self.load_data("today") # Refresh the table
            self.ent_id.delete(0, tk.END) # Clear the input box

        except mysql.connector.Error as err:
            # 3. Handle Duplicate Login Error (MySQL Error 1062)
            if err.errno == 1062:
                messagebox.showerror("Duplicate Login", 
                                     f"Employee {emp_id} has already logged in today!")
            else:
                # Handle other database errors (like ID not existing)
                messagebox.showerror("Error", f"Database Error: {err}")
                
                
    def process_logout(self):
        emp_id = self.ent_id.get()
        if not emp_id: return
        now = datetime.now()
        
        self.cursor.execute("SELECT login_time FROM attendance WHERE emp_id=%s AND date=CURDATE() AND logout_time IS NULL", (emp_id,))
        res = self.cursor.fetchone()
        
        if res:
            login_time = res['login_time']
            duration = now - login_time
            total_seconds = int(duration.total_seconds())
            
            # Calculate Hours and Minutes
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            # Display format (e.g., 08:30)
            time_str = f"{hours}h {minutes}m"
            
            # Decimal format for database (e.g., 8.5)
            work_hours_decimal = round(total_seconds / 3600, 2)
            
            # Underwork detection (less than 8 hours)
            status = "Present" if work_hours_decimal >= 8 else "Underworked"
            
            self.cursor.execute("""
                UPDATE attendance 
                SET logout_time=%s, work_hours=%s, status=%s 
                WHERE emp_id=%s AND date=CURDATE()
            """, (now, work_hours_decimal, status, emp_id))
            
            messagebox.showinfo("Success", f"Logged out!\nDuration: {time_str}\nStatus: {status}")
            self.load_data("today")
            self.ent_id.delete(0, tk.END)
        else:
            messagebox.showwarning("Error", "No active login session found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedAttendanceSystem(root)
    root.mainloop()