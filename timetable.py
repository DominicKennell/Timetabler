import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from typing import List, Dict, Set, Tuple, Optional
import copy
import random
from collections import defaultdict
from datetime import datetime
import os

# PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ ReportLab not installed. PDF export will not be available.")
    print("To enable PDF export, run: pip install reportlab")


class ConstraintsDialog:
    """Dialog for configuring dynamic constraints"""
    
    def __init__(self, parent, current_constraints):
        self.result = None
        self.current_constraints = current_constraints
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Configure Schedule Constraints")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Configure All Schedule Parameters", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab 1: Subject Requirements
        req_frame = ttk.Frame(notebook, padding="10")
        notebook.add(req_frame, text="📚 Subjects & Hours")
        self.setup_requirements_tab(req_frame)
        
        # Tab 2: Faculty
        faculty_frame = ttk.Frame(notebook, padding="10")
        notebook.add(faculty_frame, text="🎓 Faculty/Departments")
        self.setup_faculty_tab(faculty_frame)
        
        # Tab 3: Courses/Levels
        courses_frame = ttk.Frame(notebook, padding="10")
        notebook.add(courses_frame, text="📖 Courses/Levels")
        self.setup_courses_tab(courses_frame)
        
        # Tab 4: Student Groups/Classes
        groups_frame = ttk.Frame(notebook, padding="10")
        notebook.add(groups_frame, text="👥 Student Groups")
        self.setup_groups_tab(groups_frame)
        
        # Tab 5: Days & Time Slots
        schedule_frame = ttk.Frame(notebook, padding="10")
        notebook.add(schedule_frame, text="📅 Days & Time Slots")
        self.setup_schedule_tab(schedule_frame)
        
        # Tab 6: Classrooms
        rooms_frame = ttk.Frame(notebook, padding="10")
        notebook.add(rooms_frame, text="🏫 Classrooms")
        self.setup_rooms_tab(rooms_frame)
        
        # Tab 7: Group Day-Off
        dayoff_frame = ttk.Frame(notebook, padding="10")
        notebook.add(dayoff_frame, text="🌴 Group Day-Off")
        self.setup_dayoff_tab(dayoff_frame)
        
        # Tab 8: Apply Configuration
        apply_frame = ttk.Frame(notebook, padding="20")
        notebook.add(apply_frame, text="✅ Apply Configuration")
        self.setup_apply_tab(apply_frame)
    
    def setup_requirements_tab(self, parent):
        """Tab for configuring subject requirements per class"""
        ttk.Label(parent, text="Define how many sessions of each subject are required per class:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        # Frame for requirements
        req_frame = ttk.LabelFrame(parent, text="Subject Requirements", padding="10")
        req_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable frame
        canvas = tk.Canvas(req_frame)
        scrollbar = ttk.Scrollbar(req_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        ttk.Label(scrollable_frame, text="Subject", font=("Arial", 10, "bold"), width=15).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Sessions per Class", font=("Arial", 10, "bold"), width=15).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Actions", font=("Arial", 10, "bold"), width=10).grid(row=0, column=2, padx=5, pady=5)
        
        self.requirements_vars = {}
        current_reqs = self.current_constraints.get('requirements', {
            "Maths": 4, "English": 4, "VOC": 4, "PBL": 4, "Tutorial": 1
        })
        
        row = 1
        for subject, count in current_reqs.items():
            self.add_requirement_row(scrollable_frame, row, subject, count)
            row += 1
        
        self.req_row_counter = row
        self.req_scrollable_frame = scrollable_frame
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add new subject button
        ttk.Button(parent, text="➕ Add Subject", 
                  command=self.add_new_subject).pack(pady=10)
    
    def add_requirement_row(self, parent, row, subject, count):
        """Add a row for a subject requirement"""
        subject_var = tk.StringVar(value=subject)
        count_var = tk.IntVar(value=count)
        
        ttk.Entry(parent, textvariable=subject_var, width=15).grid(row=row, column=0, padx=5, pady=2)
        ttk.Spinbox(parent, from_=0, to=10, textvariable=count_var, width=13).grid(row=row, column=1, padx=5, pady=2)
        
        ttk.Button(parent, text="🗑️", width=3,
                  command=lambda r=row: self.remove_requirement_row(r)).grid(row=row, column=2, padx=5, pady=2)
        
        self.requirements_vars[row] = {'subject': subject_var, 'count': count_var}
    
    def setup_faculty_tab(self, parent):
        """Tab for configuring faculty/departments"""
        ttk.Label(parent, text="Define your faculty/departments:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        info_label = ttk.Label(parent, 
                              text="e.g., Performing Arts, Art, Media, DCC, Music etc.\n"
                              "Teachers can be assigned to faculties for better organization",
                              font=("Arial", 9, "italic"),
                              foreground="gray")
        info_label.pack(pady=(0, 15))
        
        # Frame for faculty
        faculty_frame = ttk.LabelFrame(parent, text="Faculty/Departments", padding="10")
        faculty_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(faculty_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.faculty_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=12, font=("Arial", 10))
        self.faculty_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.faculty_listbox.yview)
        
        # Populate with current faculty
        current_faculty = self.current_constraints.get('faculty', 
                                                       ["Performing Arts", "Art", "Media", "DCC", "Music"])
        
        for faculty in current_faculty:
            self.faculty_listbox.insert(tk.END, faculty)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Faculty", 
                  command=self.add_faculty).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Edit Selected", 
                  command=self.edit_faculty).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Remove Selected", 
                  command=self.remove_faculty).pack(side=tk.LEFT, padx=5)
    
    def add_faculty(self):
        """Add a new faculty"""
        faculty = simpledialog.askstring("New Faculty/Department", 
                                        "Enter faculty/department name:\n(e.g., Performing Arts, Art, Media, DCC, Music)", 
                                        parent=self.dialog)
        if faculty and faculty.strip():
            self.faculty_listbox.insert(tk.END, faculty.strip())
    
    def edit_faculty(self):
        """Edit selected faculty"""
        selection = self.faculty_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a faculty to edit!", parent=self.dialog)
            return
        
        idx = selection[0]
        current = self.faculty_listbox.get(idx)
        
        new_faculty = simpledialog.askstring("Edit Faculty/Department", 
                                            "Edit faculty/department name:", 
                                            initialvalue=current,
                                            parent=self.dialog)
        if new_faculty and new_faculty.strip():
            self.faculty_listbox.delete(idx)
            self.faculty_listbox.insert(idx, new_faculty.strip())
    
    def remove_faculty(self):
        """Remove selected faculty"""
        selection = self.faculty_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a faculty to remove!", parent=self.dialog)
            return
        
        self.faculty_listbox.delete(selection[0])
    
    def setup_courses_tab(self, parent):
        """Tab for configuring courses/levels"""
        ttk.Label(parent, text="Define your courses/levels:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        info_label = ttk.Label(parent, 
                              text="e.g., Level 1, Level 2. Level 3 etc.\n"
                              "Teachers can be assigned to specific courses/levels they teach",
                              font=("Arial", 9, "italic"),
                              foreground="gray")
        info_label.pack(pady=(0, 15))
        
        # Frame for courses
        courses_frame = ttk.LabelFrame(parent, text="Courses/Levels", padding="10")
        courses_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(courses_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.courses_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=12, font=("Arial", 10))
        self.courses_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.courses_listbox.yview)
        
        # Populate with current courses
        current_courses = self.current_constraints.get('courses', 
                                                       ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"])
        
        for course in current_courses:
            self.courses_listbox.insert(tk.END, course)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Course/Level", 
                  command=self.add_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Edit Selected", 
                  command=self.edit_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Remove Selected", 
                  command=self.remove_course).pack(side=tk.LEFT, padx=5)
    
    def add_course(self):
        """Add a new course"""
        course = simpledialog.askstring("New Course/Level", 
                                       "Enter course/level name:\n(e.g., Level 1, Beginner, Year 2)", 
                                       parent=self.dialog)
        if course and course.strip():
            self.courses_listbox.insert(tk.END, course.strip())
    
    def edit_course(self):
        """Edit selected course"""
        selection = self.courses_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a course to edit!", parent=self.dialog)
            return
        
        idx = selection[0]
        current = self.courses_listbox.get(idx)
        
        new_course = simpledialog.askstring("Edit Course/Level", 
                                           "Edit course/level name:", 
                                           initialvalue=current,
                                           parent=self.dialog)
        if new_course and new_course.strip():
            self.courses_listbox.delete(idx)
            self.courses_listbox.insert(idx, new_course.strip())
    
    def remove_course(self):
        """Remove selected course"""
        selection = self.courses_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a course to remove!", parent=self.dialog)
            return
        
        self.courses_listbox.delete(selection[0])
    
    def setup_groups_tab(self, parent):
        """Tab for configuring student groups/classes with faculty and retake subjects"""
        ttk.Label(parent, text="Define your student groups/classes:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        info_label = ttk.Label(parent, 
                              text="Configure each student group with their faculty and which subjects they need\n"
                              "(e.g., Music students only get Music faculty teachers)",
                              font=("Arial", 9, "italic"),
                              foreground="gray")
        info_label.pack(pady=(0, 15))
        
        # Frame for groups with scrolling
        groups_frame = ttk.LabelFrame(parent, text="Student Groups Configuration", padding="10")
        groups_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(groups_frame)
        scrollbar = ttk.Scrollbar(groups_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="Group Name", font=("Arial", 9, "bold"), width=25).grid(row=0, column=0, padx=5)
        ttk.Label(header_frame, text="Faculty", font=("Arial", 9, "bold"), width=20).grid(row=0, column=1, padx=5)
        ttk.Label(header_frame, text="Actions", font=("Arial", 9, "bold"), width=10).grid(row=0, column=2, padx=5)
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Container for group rows
        self.groups_container = ttk.Frame(scrollable_frame)
        self.groups_container.pack(fill=tk.BOTH, expand=True)
        
        self.group_rows = {}
        self.group_row_counter = 0
        
        # Load existing groups or create defaults
        current_classes = self.current_constraints.get('classes', 
                                                       ["L1A", "L2A", "L2B", "L2C", "L3A", "L3B", "L3C"])
        current_faculty = self.current_constraints.get('faculty', 
                                                      ["Performing Arts", "Art", "Media", "DCC", "Music"])
        
        # Get group configurations if they exist
        group_configs = self.current_constraints.get('group_configs', {})
        
        for group_name in current_classes:
            config = group_configs.get(group_name, {
                'faculty': current_faculty[0] if current_faculty else ''
            })
            self.add_group_row(group_name, config.get('faculty', ''))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Student Group", 
                  command=self.add_new_group_row).pack(side=tk.LEFT, padx=5)
    
    def add_group_row(self, group_name='', faculty=''):
        """Add a row for a student group configuration"""
        row_frame = ttk.Frame(self.groups_container)
        row_frame.pack(fill=tk.X, pady=2)
        
        row_id = self.group_row_counter
        self.group_row_counter += 1
        
        # Group name
        name_var = tk.StringVar(value=group_name)
        name_entry = ttk.Entry(row_frame, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=0, padx=5, pady=2)
        
        # Faculty dropdown
        current_faculty = []
        if hasattr(self, 'faculty_listbox'):
            for i in range(self.faculty_listbox.size()):
                current_faculty.append(self.faculty_listbox.get(i))
        else:
            current_faculty = self.current_constraints.get('faculty', 
                                                          ["Performing Arts", "Art", "Media", "DCC", "Music"])
        
        # Add English and Maths as faculty options for resit classes
        all_faculties = ['English', 'Maths'] + current_faculty
        
        faculty_var = tk.StringVar(value=faculty if faculty else (all_faculties[0] if all_faculties else ''))
        faculty_combo = ttk.Combobox(row_frame, textvariable=faculty_var, 
                                    values=all_faculties, width=20, state='readonly')
        faculty_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Remove button
        remove_btn = ttk.Button(row_frame, text="🗑️", width=3,
                               command=lambda: self.remove_group_row(row_id))
        remove_btn.grid(row=0, column=2, padx=5, pady=2)
        
        # Store row data
        self.group_rows[row_id] = {
            'frame': row_frame,
            'name_var': name_var,
            'faculty_var': faculty_var
        }
    
    def add_new_group_row(self):
        """Add a new empty group row"""
        current_faculty = []
        if hasattr(self, 'faculty_listbox'):
            for i in range(self.faculty_listbox.size()):
                current_faculty.append(self.faculty_listbox.get(i))
        
        default_faculty = current_faculty[0] if current_faculty else ''
        self.add_group_row('', default_faculty)
    
    def remove_group_row(self, row_id):
        """Remove a group row"""
        if row_id in self.group_rows:
            self.group_rows[row_id]['frame'].destroy()
            del self.group_rows[row_id]
    
    def setup_schedule_tab(self, parent):
        """Tab for configuring days and time slots"""
        # Days section
        ttk.Label(parent, text="School Days:", font=("Arial", 11, "bold")).pack(pady=(0, 5))
        
        days_frame = ttk.LabelFrame(parent, text="Select Active Days", padding="10")
        days_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Checkboxes for days
        self.days_vars = {}
        current_days = self.current_constraints.get('days', 
                                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day in enumerate(all_days):
            var = tk.BooleanVar(value=(day in current_days))
            self.days_vars[day] = var
            ttk.Checkbutton(days_frame, text=day, variable=var).grid(row=i//4, column=i%4, sticky=tk.W, padx=10, pady=2)
        
        # Time slots section
        ttk.Label(parent, text="Time Slots:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        
        slots_frame = ttk.LabelFrame(parent, text="Class Time Slots", padding="10")
        slots_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(slots_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timeslots_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, font=("Arial", 10))
        self.timeslots_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.timeslots_listbox.yview)
        
        # Populate with current time slots
        current_slots = self.current_constraints.get('time_slots', [
            "09:00-10:00", "10:10-11:10", "11:30-12:30", 
            "13:30-14:30", "14:40-15:40", "15:50-16:50"
        ])
        
        for slot in current_slots:
            self.timeslots_listbox.insert(tk.END, slot)
        
        # Buttons
        btn_frame = ttk.Frame(slots_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="➕ Add", 
                  command=self.add_timeslot).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="✏️ Edit", 
                  command=self.edit_timeslot).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="🗑️ Remove", 
                  command=self.remove_timeslot).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(slots_frame, text="Format: HH:MM-HH:MM (e.g., 09:00-10:00)", 
                 font=("Arial", 8, "italic"), foreground="gray").pack()
    
    def add_timeslot(self):
        """Add a new time slot"""
        slot = simpledialog.askstring("New Time Slot", 
                                     "Enter time slot (HH:MM-HH:MM):", 
                                     parent=self.dialog)
        if slot and slot.strip():
            self.timeslots_listbox.insert(tk.END, slot.strip())
    
    def edit_timeslot(self):
        """Edit selected time slot"""
        selection = self.timeslots_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a time slot to edit!", parent=self.dialog)
            return
        
        idx = selection[0]
        current = self.timeslots_listbox.get(idx)
        
        new_slot = simpledialog.askstring("Edit Time Slot", 
                                         "Edit time slot:", 
                                         initialvalue=current,
                                         parent=self.dialog)
        if new_slot and new_slot.strip():
            self.timeslots_listbox.delete(idx)
            self.timeslots_listbox.insert(idx, new_slot.strip())
    
    def remove_timeslot(self):
        """Remove selected time slot"""
        selection = self.timeslots_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a time slot to remove!", parent=self.dialog)
            return
        
        self.timeslots_listbox.delete(selection[0])
    
    def setup_rooms_tab(self, parent):
        """Tab for configuring classrooms"""
        ttk.Label(parent, text="Define available classrooms:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        # Frame for rooms
        rooms_frame = ttk.LabelFrame(parent, text="Classrooms", padding="10")
        rooms_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(rooms_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.rooms_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=12, font=("Arial", 10))
        self.rooms_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.rooms_listbox.yview)
        
        # Populate with current rooms
        current_rooms = self.current_constraints.get('rooms', [
            "Room A101", "Room A102", "Room A103", "Room B201", "Room B202", 
            "Room B203", "Room C301", "Room C302", "Room D401", "Room D402"
        ])
        
        for room in current_rooms:
            self.rooms_listbox.insert(tk.END, room)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Classroom", 
                  command=self.add_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Edit Selected", 
                  command=self.edit_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Remove Selected", 
                  command=self.remove_room).pack(side=tk.LEFT, padx=5)
    
    def add_room(self):
        """Add a new classroom"""
        room = simpledialog.askstring("New Classroom", 
                                     "Enter classroom name:\n(e.g., Room A101, Lab-201, Hall-Main)", 
                                     parent=self.dialog)
        if room and room.strip():
            self.rooms_listbox.insert(tk.END, room.strip())
    
    def edit_room(self):
        """Edit selected classroom"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a classroom to edit!", parent=self.dialog)
            return
        
        idx = selection[0]
        current = self.rooms_listbox.get(idx)
        
        new_room = simpledialog.askstring("Edit Classroom", 
                                         "Edit classroom name:", 
                                         initialvalue=current,
                                         parent=self.dialog)
        if new_room and new_room.strip():
            self.rooms_listbox.delete(idx)
            self.rooms_listbox.insert(idx, new_room.strip())
    
    def remove_room(self):
        """Remove selected classroom"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a classroom to remove!", parent=self.dialog)
            return
        
        self.rooms_listbox.delete(selection[0])
    
    def setup_dayoff_tab(self, parent):
        """Tab for configuring group day-off assignments"""
        ttk.Label(parent, text="Group Day-Off Scheduling:", 
                 font=("Arial", 11, "bold")).pack(pady=(0, 10))
        
        info_text = ("Assign which day each group has off.\n"
                    "Groups are identified by the last character of the student group name.\n"
                    "Leave blank if a group should have no day off.")
        ttk.Label(parent, text=info_text, 
                 font=("Arial", 9, "italic"), foreground="gray").pack(pady=(0, 15))
        
        # Get current data
        current_days = self.current_constraints.get('days', 
                                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        current_dayoff = self.current_constraints.get('group_day_off', {
            'A': 'Monday', 'B': 'Tuesday', 'C': 'Wednesday', 'D': 'Thursday'
        })
        
        # Create scrollable frame
        canvas = tk.Canvas(parent, height=300)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="Group ID", font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT, padx=10)
        ttk.Label(header_frame, text="Day Off", font=("Arial", 10, "bold"), width=18).pack(side=tk.LEFT, padx=10)
        ttk.Label(header_frame, text="Student Groups with this ID", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        self.dayoff_vars = {}
        
        # Create entries for A-Z groups
        all_group_ids = [chr(i) for i in range(ord('A'), ord('Z')+1)]
        
        for group_id in all_group_ids:
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"Group {group_id}", width=12).pack(side=tk.LEFT, padx=10)
            
            var = tk.StringVar(value=current_dayoff.get(group_id, ''))
            combo = ttk.Combobox(row_frame, textvariable=var, 
                                values=[''] + current_days, width=15, state='readonly')
            combo.pack(side=tk.LEFT, padx=10)
            self.dayoff_vars[group_id] = var
            
            # Placeholder for classes (will be updated during save)
            ttk.Label(row_frame, text="-", font=("Arial", 9, "italic"), 
                     foreground="gray").pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_apply_tab(self, parent):
        """Tab for reviewing and applying configuration"""
        # Title
        title_label = ttk.Label(parent, 
                               text="Review & Apply Configuration", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ttk.Label(parent, 
                                   text="Review your settings and apply when ready", 
                                   font=("Arial", 10, "italic"),
                                   foreground="gray")
        subtitle_label.pack(pady=(0, 30))
        
        # Summary frame
        summary_frame = ttk.LabelFrame(parent, text="Configuration Summary", padding="20")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 30))
        
        # Create text widget for summary
        summary_text = tk.Text(summary_frame, height=15, width=60, wrap=tk.WORD, 
                              font=("Arial", 10), relief=tk.FLAT, background="#f5f5f5")
        summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Generate summary
        self.generate_summary_text(summary_text)
        
        summary_text.config(state=tk.DISABLED)
        
        # Buttons frame - centered with larger buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)
        
        # Apply button - large and prominent
        apply_btn = ttk.Button(button_frame, 
                              text="💾 SAVE & APPLY CONFIGURATION", 
                              command=self.save,
                              width=35)
        apply_btn.pack(pady=10)
        
        # Style the apply button
        style = ttk.Style()
        style.configure('Apply.TButton', font=('Arial', 12, 'bold'))
        apply_btn.configure(style='Apply.TButton')
        
        # Secondary buttons
        secondary_frame = ttk.Frame(button_frame)
        secondary_frame.pack()
        
        ttk.Button(secondary_frame, text="↺ Reset to Defaults", 
                  command=self.reset_defaults, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(secondary_frame, text="✗ Cancel", 
                  command=self.cancel, width=15).pack(side=tk.LEFT, padx=5)
    
    def generate_summary_text(self, text_widget):
        """Generate a summary of current configuration"""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        # Subjects
        text_widget.insert(tk.END, "📚 SUBJECTS & REQUIREMENTS:\n", "bold")
        if hasattr(self, 'requirements_vars') and self.requirements_vars:
            for row_data in self.requirements_vars.values():
                subject = row_data['subject'].get().strip()
                count = row_data['count'].get()
                if subject:
                    text_widget.insert(tk.END, f"  • {subject}: {count} hours per class\n")
        else:
            text_widget.insert(tk.END, "  (Using defaults)\n")
        
        # Faculty
        text_widget.insert(tk.END, "\n🎓 FACULTY/DEPARTMENTS:\n", "bold")
        if hasattr(self, 'faculty_listbox'):
            faculty_count = self.faculty_listbox.size()
            text_widget.insert(tk.END, f"  • {faculty_count} faculty/departments defined\n")
            if faculty_count <= 10:
                for i in range(faculty_count):
                    text_widget.insert(tk.END, f"    - {self.faculty_listbox.get(i)}\n")
        
        # Courses
        text_widget.insert(tk.END, "\n📖 COURSES/LEVELS:\n", "bold")
        if hasattr(self, 'courses_listbox'):
            courses_count = self.courses_listbox.size()
            text_widget.insert(tk.END, f"  • {courses_count} courses/levels defined\n")
            if courses_count <= 10:
                for i in range(courses_count):
                    text_widget.insert(tk.END, f"    - {self.courses_listbox.get(i)}\n")
        
        # Student Groups
        text_widget.insert(tk.END, "\n👥 STUDENT GROUPS:\n", "bold")
        if hasattr(self, 'groups_listbox'):
            groups_count = self.groups_listbox.size()
            text_widget.insert(tk.END, f"  • {groups_count} student groups defined\n")
            if groups_count <= 15:
                for i in range(groups_count):
                    text_widget.insert(tk.END, f"    - {self.groups_listbox.get(i)}\n")
        
        # Days
        text_widget.insert(tk.END, "\n📅 SCHOOL DAYS:\n", "bold")
        if hasattr(self, 'days_vars'):
            days = [day for day, var in self.days_vars.items() if var.get()]
            text_widget.insert(tk.END, f"  • {len(days)} days: {', '.join(days)}\n")
        
        # Time Slots
        text_widget.insert(tk.END, "\n⏰ TIME SLOTS:\n", "bold")
        if hasattr(self, 'timeslots_listbox'):
            slots_count = self.timeslots_listbox.size()
            text_widget.insert(tk.END, f"  • {slots_count} time slots per day\n")
        
        # Classrooms
        text_widget.insert(tk.END, "\n🏫 CLASSROOMS:\n", "bold")
        if hasattr(self, 'rooms_listbox'):
            rooms_count = self.rooms_listbox.size()
            text_widget.insert(tk.END, f"  • {rooms_count} classrooms available\n")
        
        # Day-off
        text_widget.insert(tk.END, "\n🌴 GROUP DAY-OFF:\n", "bold")
        if hasattr(self, 'dayoff_vars'):
            dayoff_count = sum(1 for var in self.dayoff_vars.values() if var.get().strip())
            text_widget.insert(tk.END, f"  • {dayoff_count} groups with assigned day-off\n")
        
        # Configure tag for bold text
        text_widget.tag_configure("bold", font=("Arial", 10, "bold"))
        
        text_widget.config(state=tk.DISABLED)
    
    def add_new_subject(self):
        """Add a new subject requirement"""
        subject = simpledialog.askstring("New Subject", "Enter subject name:", parent=self.dialog)
        if subject and subject.strip():
            self.add_requirement_row(self.req_scrollable_frame, self.req_row_counter, subject.strip(), 1)
            self.req_row_counter += 1
    
    def remove_requirement_row(self, row):
        """Remove a requirement row"""
        if row in self.requirements_vars:
            del self.requirements_vars[row]
            # Find and destroy widgets in that row
            for widget in self.req_scrollable_frame.grid_slaves(row=row):
                widget.destroy()
    
    def setup_timeslots_tab(self, parent):
        """Tab for configuring time slots"""
        ttk.Label(parent, text="Define the time slots for each day:", 
                 font=("Arial", 10)).pack(pady=(0, 10))
        
        # Frame for time slots
        slots_frame = ttk.LabelFrame(parent, text="Time Slots", padding="10")
        slots_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(slots_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timeslots_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.timeslots_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.timeslots_listbox.yview)
        
        # Populate with current time slots
        current_slots = self.current_constraints.get('time_slots', [
            "09:00-10:00", "10:10-11:10", "11:30-12:30", 
            "13:30-14:30", "14:40-15:40", "15:50-16:50"
        ])
        
        for slot in current_slots:
            self.timeslots_listbox.insert(tk.END, slot)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add Time Slot", 
                  command=self.add_timeslot).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Edit Selected", 
                  command=self.edit_timeslot).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Remove Selected", 
                  command=self.remove_timeslot).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(parent, text="Format: HH:MM-HH:MM (e.g., 09:00-10:00)", 
                 font=("Arial", 9, "italic")).pack()
    
    def add_timeslot(self):
        """Add a new time slot"""
        slot = simpledialog.askstring("New Time Slot", 
                                     "Enter time slot (HH:MM-HH:MM):", 
                                     parent=self.dialog)
        if slot and slot.strip():
            self.timeslots_listbox.insert(tk.END, slot.strip())
    
    def edit_timeslot(self):
        """Edit selected time slot"""
        selection = self.timeslots_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a time slot to edit!")
            return
        
        idx = selection[0]
        current = self.timeslots_listbox.get(idx)
        
        new_slot = simpledialog.askstring("Edit Time Slot", 
                                         "Edit time slot:", 
                                         initialvalue=current,
                                         parent=self.dialog)
        if new_slot and new_slot.strip():
            self.timeslots_listbox.delete(idx)
            self.timeslots_listbox.insert(idx, new_slot.strip())
    
    def remove_timeslot(self):
        """Remove selected time slot"""
        selection = self.timeslots_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a time slot to remove!")
            return
        
        self.timeslots_listbox.delete(selection[0])
    
    def setup_days_tab(self, parent):
        """Tab for configuring days and day-off assignments"""
        # Days section
        ttk.Label(parent, text="School Days:", font=("Arial", 11, "bold")).pack(pady=(0, 5))
        
        days_frame = ttk.LabelFrame(parent, text="Active Days", padding="10")
        days_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Checkboxes for days
        self.days_vars = {}
        current_days = self.current_constraints.get('days', 
                                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day in enumerate(all_days):
            var = tk.BooleanVar(value=(day in current_days))
            self.days_vars[day] = var
            ttk.Checkbutton(days_frame, text=day, variable=var).grid(row=i//4, column=i%4, sticky=tk.W, padx=10, pady=2)
        
        # Day-off assignments section
        ttk.Label(parent, text="Group Day-Off Assignments:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        ttk.Label(parent, text="Assign which day each group has off (leave blank for no day off)", 
                 font=("Arial", 9, "italic")).pack()
        
        dayoff_frame = ttk.LabelFrame(parent, text="Day-Off by Group", padding="10")
        dayoff_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Headers
        ttk.Label(dayoff_frame, text="Group", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(dayoff_frame, text="Day Off", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(dayoff_frame, text="Classes in Group", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, pady=5)
        
        current_dayoff = self.current_constraints.get('group_day_off', {
            'A': 'Monday', 'B': 'Tuesday', 'C': 'Wednesday', 'D': 'Thursday'
        })
        
        self.dayoff_vars = {}
        groups = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        for i, group in enumerate(groups):
            ttk.Label(dayoff_frame, text=f"Group {group}").grid(row=i+1, column=0, padx=10, pady=2)
            
            var = tk.StringVar(value=current_dayoff.get(group, ''))
            combo = ttk.Combobox(dayoff_frame, textvariable=var, 
                                values=[''] + all_days, width=15)
            combo.grid(row=i+1, column=1, padx=10, pady=2)
            self.dayoff_vars[group] = var
            
            # Show which classes would be in this group
            current_classes = self.current_constraints.get('classes', [])
            classes_in_group = [c for c in current_classes if c.endswith(group)]
            ttk.Label(dayoff_frame, text=', '.join(classes_in_group) if classes_in_group else '-',
                     font=("Arial", 9, "italic")).grid(row=i+1, column=2, padx=10, pady=2)
    
    def setup_classes_tab(self, parent):
        """Tab for configuring classes and rooms"""
        # Classes section
        ttk.Label(parent, text="Student Classes:", font=("Arial", 11, "bold")).pack(pady=(0, 5))
        
        classes_frame = ttk.LabelFrame(parent, text="Classes", padding="10")
        classes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox for classes
        list_frame = ttk.Frame(classes_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.classes_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=8)
        self.classes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.classes_listbox.yview)
        
        # Populate with current classes
        current_classes = self.current_constraints.get('classes', 
                                                       ["L1A", "L2A", "L2B", "L2C", "L3A", "L3B", "L3C"])
        
        for cls in current_classes:
            self.classes_listbox.insert(tk.END, cls)
        
        # Buttons for classes
        cls_btn_frame = ttk.Frame(classes_frame)
        cls_btn_frame.pack(pady=5)
        
        ttk.Button(cls_btn_frame, text="➕ Add", 
                  command=self.add_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(cls_btn_frame, text="✏️ Edit", 
                  command=self.edit_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(cls_btn_frame, text="🗑️ Remove", 
                  command=self.remove_class).pack(side=tk.LEFT, padx=2)
        
        # Rooms section
        ttk.Label(parent, text="Rooms:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        
        rooms_frame = ttk.LabelFrame(parent, text="Rooms", padding="10")
        rooms_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox for rooms
        list_frame2 = ttk.Frame(rooms_frame)
        list_frame2.pack(fill=tk.BOTH, expand=True)
        
        scrollbar2 = ttk.Scrollbar(list_frame2)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.rooms_listbox = tk.Listbox(list_frame2, yscrollcommand=scrollbar2.set, height=8)
        self.rooms_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.rooms_listbox.yview)
        
        # Populate with current rooms
        current_rooms = self.current_constraints.get('rooms', [
            "Room A101", "Room A102", "Room A103", "Room B201", "Room B202", 
            "Room B203", "Room C301", "Room C302", "Room D401", "Room D402"
        ])
        
        for room in current_rooms:
            self.rooms_listbox.insert(tk.END, room)
        
        # Buttons for rooms
        room_btn_frame = ttk.Frame(rooms_frame)
        room_btn_frame.pack(pady=5)
        
        ttk.Button(room_btn_frame, text="➕ Add", 
                  command=self.add_room).pack(side=tk.LEFT, padx=2)
        ttk.Button(room_btn_frame, text="✏️ Edit", 
                  command=self.edit_room).pack(side=tk.LEFT, padx=2)
        ttk.Button(room_btn_frame, text="🗑️ Remove", 
                  command=self.remove_room).pack(side=tk.LEFT, padx=2)
    
    def reset_defaults(self):
        """Reset all constraints to default values"""
        if messagebox.askyesno("Reset to Defaults", 
                              "Are you sure you want to reset all constraints to default values?",
                              parent=self.dialog):
            # This will reload the dialog with default values
            self.dialog.destroy()
            default_constraints = {
                'requirements': {"Maths": 4, "English": 4, "VOC": 4, "PBL": 4, "Tutorial": 1},
                'time_slots': ["09:00-10:00", "10:10-11:10", "11:30-12:30", 
                              "13:30-14:30", "14:40-15:40", "15:50-16:50"],
                'days': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                'group_day_off': {'A': 'Monday', 'B': 'Tuesday', 'C': 'Wednesday', 'D': 'Thursday'},
                'classes': ["L1A", "L2A", "L2B", "L2C", "L3A", "L3B", "L3C"],
                'rooms': ["Room A101", "Room A102", "Room A103", "Room B201", "Room B202", 
                         "Room B203", "Room C301", "Room C302", "Room D401", "Room D402"]
            }
            self.__init__(self.dialog.master, default_constraints)
    
    def save(self):
        """Save and validate all constraints"""
        try:
            # Collect requirements
            requirements = {}
            for row_data in self.requirements_vars.values():
                subject = row_data['subject'].get().strip()
                count = row_data['count'].get()
                if subject:
                    requirements[subject] = count
            
            if not requirements:
                messagebox.showerror("Error", "Please define at least one subject requirement!", 
                                   parent=self.dialog)
                return
            
            # Collect faculty
            faculty = []
            for i in range(self.faculty_listbox.size()):
                faculty.append(self.faculty_listbox.get(i))
            
            if not faculty:
                messagebox.showwarning("Warning", "No faculty defined. Teachers won't have faculty assignments.", 
                                     parent=self.dialog)
            
            # Collect courses
            courses = []
            for i in range(self.courses_listbox.size()):
                courses.append(self.courses_listbox.get(i))
            
            if not courses:
                messagebox.showwarning("Warning", "No courses defined. Teachers won't have course/level assignments.", 
                                     parent=self.dialog)
            
            # Collect student groups/classes with configurations
            classes = []
            group_configs = {}
            
            for row_id, row_data in self.group_rows.items():
                group_name = row_data['name_var'].get().strip()
                if group_name:
                    classes.append(group_name)
                    group_configs[group_name] = {
                        'faculty': row_data['faculty_var'].get()
                    }
            
            if not classes:
                messagebox.showerror("Error", "Please define at least one student group!", 
                                   parent=self.dialog)
                return
            
            # Collect days
            days = [day for day, var in self.days_vars.items() if var.get()]
            
            if not days:
                messagebox.showerror("Error", "Please select at least one day!", 
                                   parent=self.dialog)
                return
            
            # Collect time slots
            time_slots = []
            for i in range(self.timeslots_listbox.size()):
                time_slots.append(self.timeslots_listbox.get(i))
            
            if not time_slots:
                messagebox.showerror("Error", "Please define at least one time slot!", 
                                   parent=self.dialog)
                return
            
            # Collect rooms
            rooms = []
            for i in range(self.rooms_listbox.size()):
                rooms.append(self.rooms_listbox.get(i))
            
            if not rooms:
                messagebox.showerror("Error", "Please define at least one classroom!", 
                                   parent=self.dialog)
                return
            
            # Collect day-off assignments (only for groups that have student classes)
            group_day_off = {}
            # Extract unique group IDs from classes
            groups_in_use = set()
            for cls in classes:
                if cls:
                    group_id = cls[-1]
                    if group_id.isalpha():
                        groups_in_use.add(group_id.upper())
            
            # Only save day-off for groups actually in use
            for group_id, var in self.dayoff_vars.items():
                if group_id in groups_in_use:
                    day_off = var.get().strip()
                    if day_off:
                        if day_off not in days:
                            messagebox.showwarning("Warning", 
                                                 f"Group {group_id}'s day off ({day_off}) is not an active day!\n"
                                                 f"This setting will be ignored.",
                                                 parent=self.dialog)
                        else:
                            group_day_off[group_id] = day_off
            
            # Calculate total hours needed
            total_req_hours = sum(requirements.values())
            total_hours_needed = len(classes) * total_req_hours
            
            # Build result
            self.result = {
                'requirements': requirements,
                'faculty': faculty,
                'courses': courses,
                'classes': classes,
                'group_configs': group_configs,
                'days': days,
                'time_slots': time_slots,
                'rooms': rooms,
                'group_day_off': group_day_off,
                'total_hours_per_class': total_req_hours,
                'total_hours_needed': total_hours_needed
            }
            
            # Show summary
            summary = (f"Configuration Summary:\n\n"
                      f"✓ {len(requirements)} subjects defined\n"
                      f"✓ {len(faculty)} faculty/departments\n"
                      f"✓ {len(courses)} courses/levels\n"
                      f"✓ {len(classes)} student groups\n"
                      f"✓ {len(days)} school days\n"
                      f"✓ {len(time_slots)} time slots per day\n"
                      f"✓ {len(rooms)} classrooms\n"
                      f"✓ {len(group_day_off)} groups with day-off\n\n"
                      f"Total hours per class: {total_req_hours}\n"
                      f"Total hours needed: {total_hours_needed}")
            
            messagebox.showinfo("Configuration Ready", summary, parent=self.dialog)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save constraints:\n{str(e)}", 
                               parent=self.dialog)
            import traceback
            traceback.print_exc()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()


class PerfectAIScheduler:
    """
    Perfect AI Scheduler - One-click solution with DYNAMIC CONSTRAINTS
    """
    
    def __init__(self, teachers_data, constraints):
        self.teachers_data = teachers_data
        self.constraints = constraints
        
        # Extract constraints
        self.classes = constraints['classes']
        self.subjects = list(constraints['requirements'].keys())
        self.days = constraints['days']
        self.time_slots = constraints['time_slots']
        self.rooms = constraints['rooms']
        self.requirements = constraints['requirements']
        self.group_day_off = constraints['group_day_off']
        
        # Build teacher lookup
        self.teacher_lookup = {t['name']: t for t in teachers_data}
    
    def get_class_group(self, class_name):
        """Extract group letter from class name (last character)"""
        return class_name[-1] if class_name else ''
    
    def get_available_days_for_class(self, class_name):
        """Get available days for a class (excluding their day off)"""
        group = self.get_class_group(class_name)
        day_off = self.group_day_off.get(group)
        
        if day_off and day_off in self.days:
            return [day for day in self.days if day != day_off]
        return self.days
        
    def generate_and_schedule_perfect(self):
        """
        ONE-CLICK SOLUTION: Generate classes and create perfect schedule
        """
        print("\n🎯 Perfect AI Scheduler - One Click Solution (Dynamic Constraints)")
        print("=" * 70)
        
        # Display constraints
        print(f"\n📊 Constraints:")
        print(f"  Classes: {len(self.classes)}")
        print(f"  Days: {len(self.days)} ({', '.join(self.days)})")
        print(f"  Time Slots: {len(self.time_slots)}")
        print(f"  Hours per class: {sum(self.requirements.values())}")
        print(f"  Total hours needed: {len(self.classes) * sum(self.requirements.values())}")
        
        # Display day-off schedule
        if self.group_day_off:
            print("\n📅 Group Day-Off Schedule:")
            for group, day_off in sorted(self.group_day_off.items()):
                classes_in_group = [c for c in self.classes if self.get_class_group(c) == group]
                if classes_in_group:
                    print(f"  Group {group} ({', '.join(classes_in_group)}): {day_off} OFF")
        
        # Step 1: Auto-generate classes
        classes_to_schedule = self.auto_generate_classes()
        
        if not classes_to_schedule:
            print("❌ Failed to generate classes")
            return None
        
        # Step 2: Create perfect schedule
        schedule = self.create_perfect_schedule(classes_to_schedule)
        
        return schedule
    
    def auto_generate_classes(self):
        """
        Automatically generate classes based on teacher hours and dynamic requirements
        WITH SMART DISTRIBUTION - considers faculty matching and optional English/Maths per group
        """
        print("\n📋 Step 1: Auto-Generating Classes with Faculty Matching...")
        print("-" * 70)
        
        # Get group configurations
        group_configs = self.constraints.get('group_configs', {})
        
        # Calculate totals accounting for optional subjects
        total_teacher_hours = sum(t['max_hours'] for t in self.teachers_data)
        total_class_hours = self.constraints.get('total_hours_needed', 0)
        
        print(f"Teacher hours available: {total_teacher_hours}")
        print(f"Class hours needed: {total_class_hours}")
        print(f"  (Varies by group based on English/Maths needs)")
        
        if total_teacher_hours != total_class_hours:
            print(f"⚠️ WARNING: Mismatch! {total_teacher_hours} vs {total_class_hours}")
            print("Using teacher hours as target...")
        
        # Get teachers by subject WITH FACULTY
        subject_teachers = defaultdict(list)
        subject_teachers_by_faculty = defaultdict(lambda: defaultdict(list))
        
        for teacher_data in self.teachers_data:
            teacher_faculty = teacher_data.get('faculty', '')
            for subject in teacher_data['subjects']:
                subject_teachers[subject].append(teacher_data)
                if teacher_faculty:
                    subject_teachers_by_faculty[subject][teacher_faculty].append(teacher_data)
        
        # Check if we have teachers for all required subjects
        for subject in self.requirements.keys():
            if subject not in subject_teachers or not subject_teachers[subject]:
                print(f"❌ ERROR: No teachers available for required subject: {subject}")
                return None
        
        classes_to_schedule = []
        teacher_hours_used = defaultdict(int)
        room_idx = 0
        
        print("\n🎯 Smart Distribution Strategy:")
        print("  • Match teachers' faculty with student groups' faculty")
        print("  • Only assign English/Maths to groups that need them")
        print("  • Balance workload across teachers")
        print("  • Respect day-off constraints")
        
        # Phase 1: Assign with faculty matching and optional subjects
        print(f"\nPhase 1: Smart assignment with faculty matching...")
        
        for class_name in self.classes:
            group = self.get_class_group(class_name)
            day_off = self.group_day_off.get(group, 'None')
            
            # Get group config
            group_config = group_configs.get(class_name, {
                'faculty': ''
            })
            
            group_faculty = group_config.get('faculty', '')
            
            print(f"  {class_name} (Faculty: {group_faculty}, OFF: {day_off}):")
            
            hours_assigned = 0
            
            for subject, count in self.requirements.items():
                # Get teachers for this subject
                # Prioritize teachers from the same faculty
                faculty_teachers = []
                if group_faculty and subject in subject_teachers_by_faculty:
                    faculty_teachers = subject_teachers_by_faculty[subject].get(group_faculty, [])
                
                # If no faculty match or faculty not set, use all teachers for subject
                if not faculty_teachers:
                    teachers = subject_teachers[subject]
                else:
                    # Prefer faculty match, but fall back to any teacher if needed
                    teachers = faculty_teachers + [t for t in subject_teachers[subject] if t not in faculty_teachers]
                
                for _ in range(count):
                    # SMART SELECTION: Score teachers
                    teacher_scores = []
                    
                    for teacher_data in teachers:
                        teacher_name = teacher_data['name']
                        score = 0
                        
                        # Factor 1: Faculty match (HUGE bonus)
                        teacher_faculty = teacher_data.get('faculty', '')
                        if teacher_faculty and teacher_faculty == group_faculty:
                            score += 100  # Strong faculty match!
                        
                        # Factor 2: Remaining capacity
                        remaining = teacher_data['max_hours'] - teacher_hours_used[teacher_name]
                        if remaining > 0:
                            score += remaining * 10
                        
                        # Factor 3: Course/Level match
                        teacher_courses = teacher_data.get('courses', [])
                        if teacher_courses:
                            for course in teacher_courses:
                                if any(char.isdigit() for char in course) and any(char.isdigit() for char in class_name):
                                    class_nums = ''.join(c for c in class_name if c.isdigit())
                                    course_nums = ''.join(c for c in course if c.isdigit())
                                    if class_nums and course_nums and class_nums[0] == course_nums[0]:
                                        score += 50
                                        break
                            else:
                                score += 10
                        
                        # Factor 4: Underutilization
                        hours_used = teacher_hours_used[teacher_name]
                        if hours_used < teacher_data['max_hours'] * 0.5:
                            score += 20
                        
                        # Factor 5: Day availability
                        class_days = self.get_available_days_for_class(class_name)
                        teacher_days = teacher_data['days']
                        available_days = [d for d in teacher_days if d in class_days]
                        score += len(available_days) * 2
                        
                        teacher_scores.append((teacher_data, score, available_days))
                    
                    # Sort by score (highest first)
                    teacher_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Pick best teacher
                    best_teacher_data, best_score, available_days = teacher_scores[0]
                    teacher_name = best_teacher_data['name']
                    teacher_faculty = best_teacher_data.get('faculty', '')
                    
                    room = self.rooms[room_idx % len(self.rooms)]
                    room_idx += 1
                    
                    if not available_days:
                        available_days = self.get_available_days_for_class(class_name)
                    
                    class_info = {
                        'teacher': teacher_name,
                        'class': class_name,
                        'subject': subject,
                        'room': room,
                        'days': available_days
                    }
                    
                    classes_to_schedule.append(class_info)
                    teacher_hours_used[teacher_name] += 1
                    hours_assigned += 1
                    
                    # Show faculty match indicator
                    faculty_match = "✓" if teacher_faculty == group_faculty else "○"
                    print(f"    {faculty_match} {subject}: {teacher_name} ({teacher_faculty})")
            
            print(f"    Total: {hours_assigned} hours assigned")
        
        # Phase 2: Intelligent Redistribution
        print("\nPhase 2: Intelligent Redistribution...")
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            over_allocated = []
            under_allocated = []
            
            for teacher_data in self.teachers_data:
                teacher_name = teacher_data['name']
                current = teacher_hours_used[teacher_name]
                target = teacher_data['max_hours']
                
                if current > target:
                    over_allocated.append({
                        'name': teacher_name,
                        'excess': current - target,
                        'data': teacher_data
                    })
                elif current < target:
                    under_allocated.append({
                        'name': teacher_name,
                        'needed': target - current,
                        'data': teacher_data
                    })
            
            if not over_allocated or not under_allocated:
                print("  ✓ Perfect balance achieved!")
                break
            
            redistributed = False
            
            for over_info in over_allocated:
                if over_info['excess'] == 0:
                    continue
                
                over_teacher = over_info['name']
                
                for i, class_info in enumerate(classes_to_schedule):
                    if class_info['teacher'] == over_teacher:
                        subject = class_info['subject']
                        class_name = class_info['class']
                        
                        # Get group faculty for matching
                        group_config = group_configs.get(class_name, {})
                        group_faculty = group_config.get('faculty', '')
                        
                        for under_info in under_allocated:
                            if under_info['needed'] > 0 and subject in under_info['data']['subjects']:
                                under_teacher = under_info['name']
                                under_teacher_faculty = under_info['data'].get('faculty', '')
                                
                                # Prefer faculty match in redistribution
                                faculty_match = (not group_faculty or under_teacher_faculty == group_faculty)
                                
                                class_days = self.get_available_days_for_class(class_name)
                                under_days = under_info['data']['days']
                                available_days = [d for d in under_days if d in class_days]
                                
                                if available_days and faculty_match:
                                    classes_to_schedule[i]['teacher'] = under_teacher
                                    classes_to_schedule[i]['days'] = available_days
                                    
                                    teacher_hours_used[over_teacher] -= 1
                                    teacher_hours_used[under_teacher] += 1
                                    
                                    over_info['excess'] -= 1
                                    under_info['needed'] -= 1
                                    
                                    redistributed = True
                                    break
                        
                        if over_info['excess'] == 0:
                            break
            
            if not redistributed:
                print("  ⚠️ Could not redistribute further")
                break
        
        # Verify
        print("\n✅ Classes Generated with Faculty Matching!")
        print("Teacher assignments:")
        all_perfect = True
        for teacher_data in self.teachers_data:
            teacher_name = teacher_data['name']
            hours = teacher_hours_used[teacher_name]
            target = teacher_data['max_hours']
            faculty = teacher_data.get('faculty', '')
            status = "✅" if hours == target else "❌"
            
            print(f"  {status} {teacher_name} ({faculty}): {hours}/{target}")
            if hours != target:
                all_perfect = False
        
        if all_perfect:
            print("\n🎉 Perfect distribution with faculty matching achieved!")
        else:
            print("\n⚠️ Some teachers not at target")
        
        print(f"\nTotal classes: {len(classes_to_schedule)}")
        
        return classes_to_schedule
        """
        Automatically generate classes based on teacher hours and dynamic requirements
        WITH SMART DISTRIBUTION - considers faculty and courses for better matching
        """
        print("\n📋 Step 1: Auto-Generating Classes with Smart Distribution...")
        print("-" * 70)
        
        # Calculate totals
        hours_per_class = sum(self.requirements.values())
        total_teacher_hours = sum(t['max_hours'] for t in self.teachers_data)
        total_class_hours = len(self.classes) * hours_per_class
        
        print(f"Teacher hours available: {total_teacher_hours}")
        print(f"Class hours needed: {total_class_hours}")
        print(f"  (Each class: {hours_per_class} hours)")
        
        if total_teacher_hours != total_class_hours:
            print(f"⚠️ WARNING: Mismatch! {total_teacher_hours} vs {total_class_hours}")
            print("Using teacher hours as target...")
        
        # Get teachers by subject WITH SCORING
        subject_teachers = defaultdict(list)
        for teacher_data in self.teachers_data:
            for subject in teacher_data['subjects']:
                # Add teacher with metadata for smart matching
                subject_teachers[subject].append(teacher_data)
        
        # Check if we have teachers for all required subjects
        for subject in self.requirements.keys():
            if subject not in subject_teachers or not subject_teachers[subject]:
                print(f"❌ ERROR: No teachers available for required subject: {subject}")
                return None
        
        classes_to_schedule = []
        teacher_hours_used = defaultdict(int)
        room_idx = 0
        
        print("\n🎯 Smart Distribution Strategy:")
        print("  • Match teachers with relevant faculty/courses to student groups")
        print("  • Balance workload across teachers")
        print("  • Respect day-off constraints")
        
        # Phase 1: Assign base requirements with smart matching
        print(f"\nPhase 1: Smart assignment ({hours_per_class} hours per class)...")
        
        for class_name in self.classes:
            group = self.get_class_group(class_name)
            day_off = self.group_day_off.get(group, 'None')
            print(f"  {class_name} (OFF: {day_off}):", end=" ")
            
            for subject, count in self.requirements.items():
                teachers = subject_teachers[subject]
                
                for _ in range(count):
                    # SMART SELECTION: Score teachers based on multiple factors
                    teacher_scores = []
                    
                    for teacher_data in teachers:
                        teacher_name = teacher_data['name']
                        score = 0
                        
                        # Factor 1: Remaining capacity (higher is better)
                        remaining = teacher_data['max_hours'] - teacher_hours_used[teacher_name]
                        if remaining > 0:
                            score += remaining * 10
                        
                        # Factor 2: Course/Level match (bonus if teacher teaches relevant courses)
                        # Extract level from class name if possible (e.g., T4A -> Level 4)
                        teacher_courses = teacher_data.get('courses', [])
                        if teacher_courses:
                            # Simple heuristic: look for numbers in class name and course names
                            for course in teacher_courses:
                                if any(char.isdigit() for char in course) and any(char.isdigit() for char in class_name):
                                    # Extract numbers
                                    class_nums = ''.join(c for c in class_name if c.isdigit())
                                    course_nums = ''.join(c for c in course if c.isdigit())
                                    if class_nums and course_nums and class_nums[0] == course_nums[0]:
                                        score += 50  # Strong match!
                                        break
                            else:
                                score += 10  # Has courses defined
                        
                        # Factor 3: Underutilization penalty (prefer teachers with fewer hours assigned)
                        hours_used = teacher_hours_used[teacher_name]
                        if hours_used < teacher_data['max_hours'] * 0.5:
                            score += 20  # Bonus for underutilized teachers
                        
                        # Factor 4: Day availability
                        class_days = self.get_available_days_for_class(class_name)
                        teacher_days = teacher_data['days']
                        available_days = [d for d in teacher_days if d in class_days]
                        score += len(available_days) * 2  # More available days = higher score
                        
                        teacher_scores.append((teacher_data, score, available_days))
                    
                    # Sort by score (highest first)
                    teacher_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Pick best teacher
                    best_teacher_data, best_score, available_days = teacher_scores[0]
                    teacher_name = best_teacher_data['name']
                    
                    room = self.rooms[room_idx % len(self.rooms)]
                    room_idx += 1
                    
                    if not available_days:
                        available_days = self.get_available_days_for_class(class_name)
                    
                    class_info = {
                        'teacher': teacher_name,
                        'class': class_name,
                        'subject': subject,
                        'room': room,
                        'days': available_days
                    }
                    
                    classes_to_schedule.append(class_info)
                    teacher_hours_used[teacher_name] += 1
            
            print(f"{hours_per_class} hours ✓")
        
        # Phase 2: Intelligent Redistribution
        print("\nPhase 2: Intelligent Redistribution...")
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            over_allocated = []
            under_allocated = []
            
            for teacher_data in self.teachers_data:
                teacher_name = teacher_data['name']
                current = teacher_hours_used[teacher_name]
                target = teacher_data['max_hours']
                
                if current > target:
                    over_allocated.append({
                        'name': teacher_name,
                        'excess': current - target,
                        'data': teacher_data
                    })
                elif current < target:
                    under_allocated.append({
                        'name': teacher_name,
                        'needed': target - current,
                        'data': teacher_data
                    })
            
            if not over_allocated or not under_allocated:
                print("  ✓ Perfect balance achieved!")
                break
            
            redistributed = False
            
            for over_info in over_allocated:
                if over_info['excess'] == 0:
                    continue
                
                over_teacher = over_info['name']
                print(f"  Redistributing from {over_teacher} ({over_info['excess']} excess)...")
                
                for i, class_info in enumerate(classes_to_schedule):
                    if class_info['teacher'] == over_teacher:
                        subject = class_info['subject']
                        class_name = class_info['class']
                        
                        for under_info in under_allocated:
                            if under_info['needed'] > 0 and subject in under_info['data']['subjects']:
                                under_teacher = under_info['name']
                                
                                class_days = self.get_available_days_for_class(class_name)
                                under_days = under_info['data']['days']
                                available_days = [d for d in under_days if d in class_days]
                                
                                if available_days:
                                    print(f"    → {subject} for {class_name}: {over_teacher} → {under_teacher}")
                                    classes_to_schedule[i]['teacher'] = under_teacher
                                    classes_to_schedule[i]['days'] = available_days
                                    
                                    teacher_hours_used[over_teacher] -= 1
                                    teacher_hours_used[under_teacher] += 1
                                    
                                    over_info['excess'] -= 1
                                    under_info['needed'] -= 1
                                    
                                    redistributed = True
                                    break
                        
                        if over_info['excess'] == 0:
                            break
            
            if not redistributed:
                print("  ⚠️ Could not redistribute further")
                break
        
        # Verify
        print("\n✅ Classes Generated with Smart Distribution!")
        print("Teacher assignments:")
        all_perfect = True
        for teacher_data in self.teachers_data:
            teacher_name = teacher_data['name']
            hours = teacher_hours_used[teacher_name]
            target = teacher_data['max_hours']
            faculty = teacher_data.get('faculty', '')
            courses = teacher_data.get('courses', [])
            status = "✅" if hours == target else "❌"
            
            extra_info = f" ({faculty}" if faculty else " (No faculty"
            if courses:
                extra_info += f", {', '.join(courses[:2])})"
            else:
                extra_info += ")"
            
            print(f"  {status} {teacher_name}: {hours}/{target}{extra_info}")
            if hours != target:
                all_perfect = False
        
        if all_perfect:
            print("\n🎉 Perfect distribution achieved with smart matching!")
        else:
            print("\n⚠️ Some teachers not at target")
        
        print(f"\nTotal classes: {len(classes_to_schedule)}")
        
        return classes_to_schedule
    
    def create_perfect_schedule(self, classes_to_schedule):
        """
        Create perfect schedule with zero conflicts and subject variety
        WITH STAGGERING - Groups sharing teachers get different time slots
        """
        print("\n📅 Step 2: Creating Perfect Schedule with Faculty Staggering...")
        print("-" * 70)
        
        schedule = []
        
        # Track usage
        teacher_schedule = defaultdict(lambda: defaultdict(set))
        class_schedule = defaultdict(lambda: defaultdict(set))
        room_schedule = defaultdict(lambda: defaultdict(set))
        class_day_subjects = defaultdict(lambda: defaultdict(list))
        
        # Group classes by faculty for staggering
        group_configs = self.constraints.get('group_configs', {})
        classes_by_faculty = defaultdict(list)
        for class_name in self.classes:
            config = group_configs.get(class_name, {})
            faculty = config.get('faculty', 'Unknown')
            classes_by_faculty[faculty].append(class_name)
        
        # Sort by class
        classes_by_student = defaultdict(list)
        for c in classes_to_schedule:
            classes_by_student[c['class']].append(c)
        
        print("\n  Strategy: Staggering groups within same faculty to avoid teacher conflicts...")
        
        # Process each faculty separately with staggering
        for faculty, faculty_classes in classes_by_faculty.items():
            print(f"\n  📚 Faculty: {faculty} - Groups: {', '.join(faculty_classes)}")
            
            stagger_offset = 0
            
            for student_class in faculty_classes:
                sessions = classes_by_student[student_class]
                group = self.get_class_group(student_class)
                day_off = self.group_day_off.get(group, 'None')
                
                print(f"\n    {student_class} (OFF: {day_off}, Stagger: {stagger_offset}): {len(sessions)} sessions")
                
                # Group by subject for distribution
                sessions_by_subject = defaultdict(list)
                for session in sessions:
                    sessions_by_subject[session['subject']].append(session)
                
                # Round-robin distribution
                all_sessions_list = []
                max_count = max(len(s) for s in sessions_by_subject.values()) if sessions_by_subject else 0
                
                for i in range(max_count):
                    for subject in sorted(self.subjects):
                        if subject in sessions_by_subject and i < len(sessions_by_subject[subject]):
                            all_sessions_list.append(sessions_by_subject[subject][i])
                
                class_available_days = self.get_available_days_for_class(student_class)
                
                for session in all_sessions_list:
                    teacher = session['teacher']
                    subject = session['subject']
                    room = session['room']
                    available_days = session['days']
                    
                    valid_days = [d for d in available_days if d in class_available_days]
                    
                    if not valid_days:
                        valid_days = class_available_days
                    
                    assigned = False
                    
                    # Prioritize days with fewer of this subject
                    day_priority = []
                    for day in valid_days:
                        subject_count = class_day_subjects[student_class][day].count(subject)
                        day_priority.append((day, subject_count))
                    
                    day_priority.sort(key=lambda x: x[1])
                    
                    for day, _ in day_priority:
                        if assigned:
                            break
                        
                        # STAGGERING: Rotate time slots based on stagger offset
                        # This ensures groups in same faculty start at different times
                        staggered_time_slots = self.time_slots[stagger_offset:] + self.time_slots[:stagger_offset]
                        
                        for time in staggered_time_slots:
                            if (time not in teacher_schedule[teacher][day] and
                                time not in class_schedule[student_class][day] and
                                time not in room_schedule[room][day]):
                                
                                assignment = {
                                    'teacher': teacher,
                                    'class': student_class,
                                    'subject': subject,
                                    'day': day,
                                    'time': time,
                                    'room': room
                                }
                                schedule.append(assignment)
                                
                                teacher_schedule[teacher][day].add(time)
                                class_schedule[student_class][day].add(time)
                                room_schedule[room][day].add(time)
                                class_day_subjects[student_class][day].append(subject)
                                
                                assigned = True
                                print(f"      ✓ {subject}: {day} {time}")
                                break
                    
                    if not assigned:
                        print(f"      ❌ Could not assign {subject}")
                        return None
                
                # Increment stagger offset for next group in this faculty
                stagger_offset = (stagger_offset + 1) % len(self.time_slots)
        
        # Verify day-off constraint
        print("\n  📅 Verifying day-off constraint...")
        day_off_violations = False
        for student_class in self.classes:
            group = self.get_class_group(student_class)
            day_off = self.group_day_off.get(group)
            
            if day_off:
                sessions_on_day_off = [s for s in schedule if s['class'] == student_class and s['day'] == day_off]
                
                if sessions_on_day_off:
                    print(f"    ❌ {student_class} has {len(sessions_on_day_off)} sessions on {day_off}")
                    day_off_violations = True
                else:
                    print(f"    ✅ {student_class}: {day_off} is free")
        
        if not day_off_violations:
            print("  ✅ All day-off constraints satisfied!")
        
        # Verify no teacher conflicts (CRITICAL CHECK)
        print("\n  👥 Verifying no teacher conflicts...")
        teacher_conflicts = []
        for teacher in teacher_schedule.keys():
            for day in teacher_schedule[teacher].keys():
                for time in teacher_schedule[teacher][day]:
                    # Count how many sessions this teacher has at this time
                    sessions_at_time = [s for s in schedule 
                                       if s['teacher'] == teacher 
                                       and s['day'] == day 
                                       and s['time'] == time]
                    
                    if len(sessions_at_time) > 1:
                        classes_str = ', '.join([s['class'] for s in sessions_at_time])
                        teacher_conflicts.append(f"{teacher} at {day} {time}: {classes_str}")
                        print(f"    ❌ {teacher} teaching {len(sessions_at_time)} classes at {day} {time}")
        
        if teacher_conflicts:
            print(f"\n  ❌ TEACHER CONFLICTS DETECTED: {len(teacher_conflicts)}")
            for conflict in teacher_conflicts[:5]:  # Show first 5
                print(f"     - {conflict}")
            print("\n  ⚠️ Staggering did not fully prevent conflicts!")
            print("     Solutions:")
            print("     1. Add more teachers for this faculty")
            print("     2. Increase time slots per day")
            print("     3. Reduce sessions per group")
            return None
        else:
            print("  ✅ No teacher conflicts - staggering successful!")
        
        print(f"\n✅ Schedule created: {len(schedule)} assignments")
        
        return schedule


class TeacherInputDialog:
    """Dialog for inputting teacher information"""
    
    def __init__(self, parent, edit_teacher=None, available_days=None, available_subjects=None, 
                 available_faculty=None, available_courses=None):
        self.result = None
        self.edit_teacher = edit_teacher
        self.available_days = available_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.available_subjects = available_subjects or ["Maths", "English", "Tutorial", "PBL", "VOC"]
        self.available_faculty = available_faculty or ["Performing Arts", "Art", "Media", "DCC", "Music"]
        self.available_courses = available_courses or ["Level 1", "Level 2", "Level 3"]
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Teacher" if not edit_teacher else "Edit Teacher")
        self.dialog.geometry("550x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        if edit_teacher:
            self.name_var.set(edit_teacher['name'])
            self.max_hours_var.set(str(edit_teacher['max_hours']))
            
            # Set faculty if exists
            if 'faculty' in edit_teacher and edit_teacher['faculty']:
                self.faculty_var.set(edit_teacher['faculty'])
            
            # Set courses if exists
            if 'courses' in edit_teacher:
                for course in edit_teacher['courses']:
                    if course in self.available_courses:
                        idx = self.available_courses.index(course)
                        self.course_vars[idx].set(True)
            
            for day in edit_teacher['days']:
                if day in self.available_days:
                    idx = self.available_days.index(day)
                    self.day_vars[idx].set(True)
            
            for subject in edit_teacher['subjects']:
                if subject in self.available_subjects:
                    idx = self.available_subjects.index(subject)
                    self.subject_vars[idx].set(True)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="Teacher Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        name_entry.focus()
        
        # Max Hours
        ttk.Label(main_frame, text="Maximum Hours per Week:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.max_hours_var = tk.StringVar(value="20")
        hours_entry = ttk.Entry(main_frame, textvariable=self.max_hours_var, width=10)
        hours_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 15))
        
        # Faculty
        ttk.Label(main_frame, text="Faculty/Department:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.faculty_var = tk.StringVar()
        faculty_combo = ttk.Combobox(main_frame, textvariable=self.faculty_var, 
                                     values=self.available_faculty, width=27, state='readonly')
        faculty_combo.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        if self.available_faculty:
            faculty_combo.set(self.available_faculty[0])
        
        # Courses/Levels
        ttk.Label(main_frame, text="Courses/Levels Can Teach:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        courses_frame = ttk.Frame(main_frame)
        courses_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.course_vars = []
        for i, course in enumerate(self.available_courses):
            var = tk.BooleanVar(value=False)
            self.course_vars.append(var)
            cb = ttk.Checkbutton(courses_frame, text=course, variable=var)
            cb.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=5, pady=2)
        
        # Available Days
        ttk.Label(main_frame, text="Available Days:", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        days_frame = ttk.Frame(main_frame)
        days_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.day_vars = []
        for i, day in enumerate(self.available_days):
            var = tk.BooleanVar(value=True)
            self.day_vars.append(var)
            cb = ttk.Checkbutton(days_frame, text=day, variable=var)
            cb.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=5, pady=2)
        
        # Subjects
        ttk.Label(main_frame, text="Subjects Can Teach:", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky=tk.W, pady=(0, 5))
        
        subjects_frame = ttk.Frame(main_frame)
        subjects_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.subject_vars = []
        for i, subject in enumerate(self.available_subjects):
            var = tk.BooleanVar(value=False)
            self.subject_vars.append(var)
            cb = ttk.Checkbutton(subjects_frame, text=subject, variable=var)
            cb.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="✓ Save", command=self.save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✗ Cancel", command=self.cancel, width=15).pack(side=tk.LEFT, padx=5)
        
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def save(self):
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter teacher name!", parent=self.dialog)
            return
        
        try:
            max_hours = int(self.max_hours_var.get())
            if max_hours <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for hours!", parent=self.dialog)
            return
        
        # Get faculty
        faculty = self.faculty_var.get().strip()
        
        # Get selected courses
        courses = [self.available_courses[i] for i, var in enumerate(self.course_vars) if var.get()]
        
        # Get selected days
        days = [self.available_days[i] for i, var in enumerate(self.day_vars) if var.get()]
        if not days:
            messagebox.showerror("Error", "Please select at least one day!", parent=self.dialog)
            return
        
        # Get selected subjects
        subjects = [self.available_subjects[i] for i, var in enumerate(self.subject_vars) if var.get()]
        if not subjects:
            messagebox.showerror("Error", "Please select at least one subject!", parent=self.dialog)
            return
        
        self.result = {
            'name': name,
            'max_hours': max_hours,
            'faculty': faculty,
            'courses': courses,
            'days': days,
            'subjects': subjects
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Dynamic Perfect AI Scheduler")
        self.root.geometry("1400x700")
        
        # Initialize with default constraints
        self.constraints = {
            'requirements': {"Maths": 4, "English": 4, "VOC": 4, "PBL": 4, "Tutorial": 1},
            'faculty': ["Performing Arts", "Art", "Media", "DCC", "Music"],
            'courses': ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
            'time_slots': ["09:00-10:00", "10:10-11:10", "11:30-12:30", 
                          "13:30-14:30", "14:40-15:40", "15:50-16:50"],
            'days': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            'group_day_off': {'A': 'Monday', 'B': 'Tuesday', 'C': 'Wednesday', 'D': 'Thursday'},
            'classes': ["L1A", "L2A", "L2B", "L2C", "L3A", "L3B", "L3C"],
            'group_configs': {
                'L1A': {'faculty': 'Faculty'},
                'L2A': {'faculty': 'Faculty'},
                'L2B': {'faculty': 'Faculty'},
                'L2C': {'faculty': 'Faculty'},
                'L3A': {'faculty': 'Faculty'},
                'L3B': {'faculty': 'Faculty'},
                'L3C': {'faculty': 'Faculty'},
            },
            'rooms': ["Room A101", "Room A102", "Room A103", "Room B201", "Room B202", 
                     "Room B203", "Room C301", "Room C302", "Room D401", "Room D402"],
            'total_hours_per_class': 17,
            'total_hours_needed': 136
        }
        
        self.teachers_data = []
        self.schedule = []
        
        self.setup_ui()
        self.update_requirements_display()
    
    def setup_ui(self):
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT PANEL
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        title_label = ttk.Label(left_panel, text="👨‍🏫 Teacher Management", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Configure Constraints button - prominent placement
        config_btn_frame = ttk.Frame(left_panel)
        config_btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(config_btn_frame, text="⚙️ CONFIGURE CONSTRAINTS", 
                  command=self.configure_constraints,
                  style='Big.TButton',
                  width=35).pack()
        
        ttk.Label(config_btn_frame, 
                 text="(Configure subjects, groups, days, time slots, rooms)",
                 font=("Arial", 8, "italic"),
                 foreground="gray").pack(pady=(5, 0))
        
        # Teacher list
        list_frame = ttk.LabelFrame(left_panel, text="Teachers", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Name', 'Hours', 'Faculty', 'Courses', 'Days', 'Subjects')
        self.teacher_tree = ttk.Treeview(list_scroll_frame, columns=columns, show='headings', height=10)
        
        self.teacher_tree.heading('Name', text='Name')
        self.teacher_tree.heading('Hours', text='Max Hours')
        self.teacher_tree.heading('Faculty', text='Faculty')
        self.teacher_tree.heading('Courses', text='Courses/Levels')
        self.teacher_tree.heading('Days', text='Available Days')
        self.teacher_tree.heading('Subjects', text='Subjects')
        
        self.teacher_tree.column('Name', width=100)
        self.teacher_tree.column('Hours', width=70)
        self.teacher_tree.column('Faculty', width=100)
        self.teacher_tree.column('Courses', width=120)
        self.teacher_tree.column('Days', width=120)
        self.teacher_tree.column('Subjects', width=150)
        
        tree_scroll = ttk.Scrollbar(list_scroll_frame, orient=tk.VERTICAL, command=self.teacher_tree.yview)
        self.teacher_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.teacher_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Teacher buttons
        teacher_btn_frame = ttk.Frame(left_panel)
        teacher_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(teacher_btn_frame, text="➕ Add Teacher", 
                  command=self.add_teacher, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(teacher_btn_frame, text="✏️ Edit Teacher", 
                  command=self.edit_teacher, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(teacher_btn_frame, text="🗑️ Remove Teacher", 
                  command=self.remove_teacher, width=20).pack(side=tk.LEFT, padx=5)
        
        # Summary
        self.summary_label = ttk.Label(left_panel, text="Total Teachers: 0 | Total Hours: 0", 
                                      font=("Arial", 10, "bold"))
        self.summary_label.pack(pady=5)
        
        # Requirements display
        req_frame = ttk.LabelFrame(left_panel, text="Current Constraints", padding="10")
        req_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.req_text = tk.Text(req_frame, height=15, width=40, wrap=tk.WORD)
        self.req_text.pack()
        self.req_text.config(state=tk.DISABLED)
        
        # RIGHT PANEL
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)
        
        title_label2 = ttk.Label(right_panel, text="🎯 Schedule Generation", 
                                font=("Arial", 16, "bold"))
        title_label2.pack(pady=(0, 10))
        
        subtitle = ttk.Label(right_panel, 
                            text="Click 'CONFIGURE CONSTRAINTS' to set up subjects, groups, days & rooms, then add teachers",
                            font=("Arial", 10, "italic"))
        subtitle.pack()
        
        # Generate button
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(pady=20)
        
        self.generate_btn = ttk.Button(btn_frame, 
                                   text="🎯 GENERATE PERFECT SCHEDULE",
                                   command=self.generate_schedule,
                                   width=40,
                                   state=tk.DISABLED)
        self.generate_btn.pack(pady=10)
        
        style = ttk.Style()
        style.configure('Big.TButton', font=('Arial', 14, 'bold'))
        self.generate_btn.configure(style='Big.TButton')
        
        # Export and Clear buttons
        button_row = ttk.Frame(btn_frame)
        button_row.pack()
        
        if PDF_AVAILABLE:
            ttk.Button(button_row, text="📄 Export to PDF", 
                      command=self.export_to_pdf,
                      width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_row, text="🗑️ Clear Schedule", 
                  command=self.clear_schedule,
                  width=15).pack(side=tk.LEFT, padx=5)
        
        # Schedule output
        output_frame = ttk.LabelFrame(right_panel, text="Generated Schedule", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.schedule_text = scrolledtext.ScrolledText(output_frame, width=80, height=25, wrap=tk.WORD)
        self.schedule_text.pack(fill=tk.BOTH, expand=True)
    
    def configure_constraints(self):
        """Open constraints configuration dialog"""
        dialog = ConstraintsDialog(self.root, self.constraints)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.constraints = dialog.result
            self.update_requirements_display()
            self.refresh_teacher_list()
            messagebox.showinfo("Success", "Constraints updated successfully!\n\n"
                              f"Hours per class: {self.constraints['total_hours_per_class']}\n"
                              f"Total hours needed: {self.constraints['total_hours_needed']}")
    
    def update_requirements_display(self):
        """Update the requirements display"""
        self.req_text.config(state=tk.NORMAL)
        self.req_text.delete(1.0, tk.END)
        
        self.req_text.insert(tk.END, "📚 REQUIREMENTS PER CLASS:\n")
        for subject, count in self.constraints['requirements'].items():
            self.req_text.insert(tk.END, f"  • {count}x {subject}\n")
        
        total = sum(self.constraints['requirements'].values())
        self.req_text.insert(tk.END, f"  ─────────────────\n")
        self.req_text.insert(tk.END, f"  Base: {total} hours per class\n")
        self.req_text.insert(tk.END, f"  (varies by group needs)\n\n")
        
        # Show group configurations
        group_configs = self.constraints.get('group_configs', {})
        if group_configs:
            self.req_text.insert(tk.END, "👥 STUDENT GROUPS:\n")
            for class_name in self.constraints['classes']:
                config = group_configs.get(class_name, {})
                faculty = config.get('faculty', '-')
                self.req_text.insert(tk.END, f"  • {class_name}: {faculty}\n")
            self.req_text.insert(tk.END, "\n")
        
        self.req_text.insert(tk.END, f"📅 DAYS: {len(self.constraints['days'])}\n")
        self.req_text.insert(tk.END, f"  {', '.join(self.constraints['days'])}\n\n")
        
        self.req_text.insert(tk.END, f"⏰ TIME SLOTS: {len(self.constraints['time_slots'])}\n")
        for slot in self.constraints['time_slots'][:3]:
            self.req_text.insert(tk.END, f"  • {slot}\n")
        if len(self.constraints['time_slots']) > 3:
            self.req_text.insert(tk.END, f"  ... and {len(self.constraints['time_slots'])-3} more\n")
        
        if self.constraints['group_day_off']:
            self.req_text.insert(tk.END, f"\n📅 GROUP DAY-OFF:\n")
            shown = 0
            for group, day_off in sorted(self.constraints['group_day_off'].items()):
                classes = [c for c in self.constraints['classes'] if c.endswith(group)]
                if classes and shown < 3:
                    self.req_text.insert(tk.END, f"  • Group {group}: {day_off}\n")
                    shown += 1
            if len(self.constraints['group_day_off']) > 3:
                self.req_text.insert(tk.END, f"  ... and {len(self.constraints['group_day_off'])-3} more\n")
        
        self.req_text.config(state=tk.DISABLED)
    
    def add_teacher(self):
        dialog = TeacherInputDialog(self.root, 
                                    available_days=self.constraints['days'],
                                    available_subjects=list(self.constraints['requirements'].keys()),
                                    available_faculty=self.constraints.get('faculty', []),
                                    available_courses=self.constraints.get('courses', []))
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if any(t['name'].lower() == dialog.result['name'].lower() for t in self.teachers_data):
                messagebox.showerror("Error", "A teacher with this name already exists!")
                return
            
            self.teachers_data.append(dialog.result)
            self.refresh_teacher_list()
            messagebox.showinfo("Success", f"Teacher '{dialog.result['name']}' added successfully!")
    
    def edit_teacher(self):
        selected = self.teacher_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a teacher to edit!")
            return
        
        item = self.teacher_tree.item(selected[0])
        teacher_name = item['values'][0]
        
        teacher_data = next((t for t in self.teachers_data if t['name'] == teacher_name), None)
        if not teacher_data:
            return
        
        dialog = TeacherInputDialog(self.root, 
                                    edit_teacher=teacher_data,
                                    available_days=self.constraints['days'],
                                    available_subjects=list(self.constraints['requirements'].keys()),
                                    available_faculty=self.constraints.get('faculty', []),
                                    available_courses=self.constraints.get('courses', []))
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if dialog.result['name'] != teacher_name:
                if any(t['name'].lower() == dialog.result['name'].lower() for t in self.teachers_data):
                    messagebox.showerror("Error", "A teacher with this name already exists!")
                    return
            
            idx = self.teachers_data.index(teacher_data)
            self.teachers_data[idx] = dialog.result
            self.refresh_teacher_list()
            messagebox.showinfo("Success", f"Teacher '{dialog.result['name']}' updated successfully!")
    
    def remove_teacher(self):
        selected = self.teacher_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a teacher to remove!")
            return
        
        item = self.teacher_tree.item(selected[0])
        teacher_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove teacher '{teacher_name}'?"):
            self.teachers_data = [t for t in self.teachers_data if t['name'] != teacher_name]
            self.refresh_teacher_list()
            messagebox.showinfo("Success", f"Teacher '{teacher_name}' removed successfully!")
    
    def refresh_teacher_list(self):
        for item in self.teacher_tree.get_children():
            self.teacher_tree.delete(item)
        
        for teacher in self.teachers_data:
            days_str = ", ".join([d[:3] for d in teacher['days']])
            subjects_str = ", ".join(teacher['subjects'])
            faculty_str = teacher.get('faculty', '-')
            courses = teacher.get('courses', [])
            courses_str = ", ".join(courses) if courses else '-'
            
            self.teacher_tree.insert('', tk.END, values=(
                teacher['name'],
                teacher['max_hours'],
                faculty_str,
                courses_str,
                days_str,
                subjects_str
            ))
        
        total_teachers = len(self.teachers_data)
        total_hours = sum(t['max_hours'] for t in self.teachers_data)
        required_hours = self.constraints['total_hours_needed']
        
        self.summary_label.config(
            text=f"Total Teachers: {total_teachers} | Total Hours: {total_hours} | Required: {required_hours}"
        )
        
        if self.teachers_data and total_hours > 0:
            self.generate_btn.config(state=tk.NORMAL)
        else:
            self.generate_btn.config(state=tk.DISABLED)
    
    def clear_schedule(self):
        self.schedule = []
        self.schedule_text.delete(1.0, tk.END)
    
    def generate_schedule(self):
        """Generate perfect schedule with dynamic constraints"""
        if not self.teachers_data:
            messagebox.showwarning("No Teachers", "Please add teachers before generating schedule!")
            return
        
        # Validate teachers for all subjects
        required_subjects = set(self.constraints['requirements'].keys())
        available_subjects = set()
        for teacher in self.teachers_data:
            available_subjects.update(teacher['subjects'])
        
        missing_subjects = required_subjects - available_subjects
        if missing_subjects:
            messagebox.showerror("Missing Subjects", 
                               f"No teachers available for: {', '.join(missing_subjects)}\n\n"
                               "Please add teachers who can teach these subjects!")
            return
        
        self.schedule_text.delete(1.0, tk.END)
        self.schedule_text.insert(tk.END, "🎯 Generating Perfect Schedule (Dynamic Constraints)...\n")
        self.schedule_text.insert(tk.END, "=" * 80 + "\n\n")
        self.root.update()
        
        # Initialize AI scheduler
        self.ai_scheduler = PerfectAIScheduler(self.teachers_data, self.constraints)
        
        # Generate schedule
        self.schedule = self.ai_scheduler.generate_and_schedule_perfect()
        
        if self.schedule:
            self.display_schedule()
        else:
            self.schedule_text.insert(tk.END, "❌ Could not generate perfect schedule\n")
            messagebox.showerror("Failed", "Could not generate schedule. Please check constraints and teacher availability.")
    
    def display_schedule(self):
        self.schedule_text.delete(1.0, tk.END)
        self.schedule_text.insert(tk.END, "🎯 PERFECT SCHEDULE GENERATED!\n")
        self.schedule_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # Show constraints
        self.schedule_text.insert(tk.END, f"📊 Applied Constraints:\n")
        self.schedule_text.insert(tk.END, f"  Classes: {len(self.constraints['classes'])}\n")
        self.schedule_text.insert(tk.END, f"  Days: {len(self.constraints['days'])}\n")
        self.schedule_text.insert(tk.END, f"  Time Slots: {len(self.constraints['time_slots'])}\n")
        self.schedule_text.insert(tk.END, f"  Hours per Class: {self.constraints['total_hours_per_class']}\n\n")
        
        # Show day-off
        if self.constraints['group_day_off']:
            self.schedule_text.insert(tk.END, "📅 Group Day-Off Schedule:\n")
            for group, day_off in sorted(self.constraints['group_day_off'].items()):
                classes_in_group = [c for c in self.constraints['classes'] if c.endswith(group)]
                if classes_in_group:
                    self.schedule_text.insert(tk.END, f"  Group {group} ({', '.join(classes_in_group)}): {day_off} OFF\n")
            self.schedule_text.insert(tk.END, "\n")
        
        # Group by day
        schedule_by_day = defaultdict(list)
        for assignment in self.schedule:
            schedule_by_day[assignment["day"]].append(assignment)
        
        # Display by day
        for day in self.constraints['days']:
            if day not in schedule_by_day:
                continue
            
            self.schedule_text.insert(tk.END, f"📅 {day}\n")
            self.schedule_text.insert(tk.END, "-" * 80 + "\n")
            
            day_schedule = sorted(schedule_by_day[day], 
                                key=lambda x: self.constraints['time_slots'].index(x['time']))
            
            for assignment in day_schedule:
                line = (f"  {assignment['time']} | {assignment['class']:6} | "
                       f"{assignment['subject']:10} | {assignment['teacher']:15} | "
                       f"{assignment['room']}\n")
                self.schedule_text.insert(tk.END, line)
            
            self.schedule_text.insert(tk.END, "\n")
        
        # Verification
        self.schedule_text.insert(tk.END, "\n📊 VERIFICATION\n")
        self.schedule_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # Day-off verification
        if self.constraints['group_day_off']:
            self.schedule_text.insert(tk.END, "📅 Day-Off Verification:\n")
            day_off_perfect = True
            for class_name in self.constraints['classes']:
                group = class_name[-1] if class_name else ''
                day_off = self.constraints['group_day_off'].get(group)
                
                if day_off:
                    sessions_on_day_off = [s for s in self.schedule if s['class'] == class_name and s['day'] == day_off]
                    
                    if sessions_on_day_off:
                        self.schedule_text.insert(tk.END, f"  ❌ {class_name}: {len(sessions_on_day_off)} sessions on {day_off}\n")
                        day_off_perfect = False
                    else:
                        self.schedule_text.insert(tk.END, f"  ✅ {class_name}: {day_off} is free\n")
            
            if day_off_perfect:
                self.schedule_text.insert(tk.END, "  ✅ All day-off constraints satisfied!\n")
            self.schedule_text.insert(tk.END, "\n")
        
        # Class breakdown
        class_subjects = defaultdict(lambda: defaultdict(int))
        class_hours = defaultdict(int)
        for assignment in self.schedule:
            class_subjects[assignment['class']][assignment['subject']] += 1
            class_hours[assignment['class']] += 1
        
        self.schedule_text.insert(tk.END, "📚 Class Requirements:\n")
        all_classes_perfect = True
        for class_name in self.constraints['classes']:
            subjects = class_subjects[class_name]
            total = class_hours[class_name]
            
            # Check requirements
            all_ok = True
            for subject, required_count in self.constraints['requirements'].items():
                if subjects[subject] < required_count:
                    all_ok = False
                    break
            
            status = "✅" if all_ok else "❌"
            
            if not all_ok:
                all_classes_perfect = False
            
            subject_str = " ".join([f"{s[:1]}:{subjects[s]}" for s in self.constraints['requirements'].keys()])
            self.schedule_text.insert(tk.END, f"  {status} {class_name}: {total:2}h - {subject_str}\n")
        
        # Teacher hours
        teacher_hours = defaultdict(int)
        for assignment in self.schedule:
            teacher_hours[assignment['teacher']] += 1
        
        teacher_max = {t['name']: t['max_hours'] for t in self.teachers_data}
        
        self.schedule_text.insert(tk.END, "\n👨‍🏫 Teacher Hours:\n")
        all_teachers_perfect = True
        for teacher_data in self.teachers_data:
            teacher = teacher_data['name']
            hours = teacher_hours.get(teacher, 0)
            max_hours = teacher_max[teacher]
            status = "✅" if hours == max_hours else "❌"
            
            if hours != max_hours:
                all_teachers_perfect = False
            
            self.schedule_text.insert(tk.END, f"  {status} {teacher}: {hours}/{max_hours}\n")
        
        # Final verdict
        self.schedule_text.insert(tk.END, "\n")
        day_off_ok = not self.constraints['group_day_off'] or day_off_perfect
        
        if all_teachers_perfect and all_classes_perfect and day_off_ok:
            self.schedule_text.insert(tk.END, "🎉 PERFECT! All constraints satisfied!\n")
            messagebox.showinfo("🎉 SUCCESS!", 
                              f"✅ PERFECT SCHEDULE!\n\n"
                              f"✓ All teachers at exact hours\n"
                              f"✓ All classes have correct requirements\n"
                              f"✓ All day-off constraints satisfied\n"
                              f"✓ Zero conflicts\n\n"
                              f"Total: {len(self.schedule)} assignments")
        else:
            self.schedule_text.insert(tk.END, "⚠️ Some constraints not perfectly met\n")
            messagebox.showinfo("Partial Success", 
                              f"Schedule created: {len(self.schedule)} assignments\n"
                              f"Some constraints may need adjustment")
    
    def export_to_pdf(self):
        """Export schedule to PDF"""
        if not self.schedule:
            messagebox.showwarning("No Schedule", "Please generate a schedule first!")
            return
        
        if not PDF_AVAILABLE:
            messagebox.showerror("PDF Not Available", 
                               "ReportLab library not installed.\n\n"
                               "To enable PDF export, run:\npip install reportlab")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"schedule_{timestamp}.pdf"
            
            if os.name == 'nt':
                downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            else:
                downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            
            pdf_path = os.path.join(downloads_path, pdf_filename)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a5490'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            elements.append(Paragraph("Perfect Class Schedule", title_style))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                                     styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary
            summary_text = f"""
            <b>Configuration:</b><br/>
            Classes: {len(self.constraints['classes'])}<br/>
            Days: {len(self.constraints['days'])}<br/>
            Time Slots: {len(self.constraints['time_slots'])}<br/>
            Hours per Class: {self.constraints['total_hours_per_class']}<br/>
            Total Sessions: {len(self.schedule)}
            """
            elements.append(Paragraph(summary_text, styles['Normal']))
            elements.append(PageBreak())
            
            # Schedule by class
            schedule_by_class = defaultdict(list)
            for assignment in self.schedule:
                schedule_by_class[assignment['class']].append(assignment)
            
            for class_name in sorted(self.constraints['classes']):
                if class_name not in schedule_by_class:
                    continue
                
                elements.append(Paragraph(f"<b>{class_name} Schedule</b>", styles['Heading2']))
                
                table_data = [['Day', 'Time', 'Subject', 'Teacher', 'Room']]
                
                class_schedule_by_day = defaultdict(list)
                for assignment in schedule_by_class[class_name]:
                    class_schedule_by_day[assignment['day']].append(assignment)
                
                for day in self.constraints['days']:
                    if day in class_schedule_by_day:
                        day_sessions = sorted(class_schedule_by_day[day],
                                            key=lambda x: self.constraints['time_slots'].index(x['time']))
                        
                        for i, session in enumerate(day_sessions):
                            if i == 0:
                                table_data.append([
                                    day[:3],
                                    session['time'],
                                    session['subject'],
                                    session['teacher'],
                                    session['room']
                                ])
                            else:
                                table_data.append([
                                    '',
                                    session['time'],
                                    session['subject'],
                                    session['teacher'],
                                    session['room']
                                ])
                
                table = Table(table_data, colWidths=[0.8*inch, 1.3*inch, 1.0*inch, 1.5*inch, 1.2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 20))
            
            doc.build(elements)
            
            messagebox.showinfo("PDF Exported!", 
                              f"✅ PDF exported successfully!\n\n"
                              f"📄 File: {pdf_filename}\n"
                              f"📁 Location: Downloads folder\n"
                              f"🗂️ Full path:\n{pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF:\n\n{str(e)}")
            import traceback
            traceback.print_exc()


def main():
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
