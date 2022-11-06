from queue import Queue
from tkinter import *
from tkinter import ttk
from datetime import datetime
from tkinter.messagebox import *
import pickle
import os

class PatientInfo:
    def __init__(self, inputs):
        self.name = inputs["name"]
        self.arrival_time = inputs["time"]
        self.is_emergency = inputs["is_emergency"]
        self.symptom = inputs["reason"]

    def __str__(self) -> str:
        return f"""
            ===========================
            Name: {self.name}
            Why: {self.symptom}
            Is Emergency: {self.is_emergency}
            Time: {self.arrival_time}
            ===========================
        """

    def __eq__(self, __o: object) -> bool:
        return self.is_emergency == __o.is_emergency and self.arrival_time == __o.arrival_time

    def __lt__(self, __o: object) -> bool:
        # LT = if A LT B, then A is less important than B
        if self.is_emergency == True and __o.is_emergency == False:
            return False
        if __o.is_emergency == True and self.is_emergency == False:
            return True
        if self.arrival_time < __o.arrival_time:
            return False
        elif self.arrival_time == __o.arrival_time:
            return False
        else:
            return True

class DoctorView:
    def __init__(self, root, queue, hospital):
        self.windowSize = "700x280"
        self.bg_color = "white"
        self.button_color = "white"
        self.box_color = "yellow"
        self.root = root
        self.queue = queue
        self.hospital = hospital

        self.patient_view = None
    
    def set_patient_view(self, patient_view):
        self.patient_view = patient_view
    
    #--------------------------doctor window----------------------------
    def create_doctor_view(self):
        for child in self.root.winfo_children():
            if child.winfo_name() == "top_lvl_doctor":
                print("Doctor View is opened")
                return None

        print("Open Doctor View")
        newWindow = Toplevel(self.root, name="top_lvl_doctor")

        #patient list table
        table_frame = Frame(newWindow)
        table_frame.place(x=20, y=20)
        self.table = ttk.Treeview(table_frame)
        self.table.pack()
        self.table['columns'] = ('id', 'name', 'symptom', 'emergency_case', 'time')

        # Constructing vertical scrollbar
        # with treeview
        verscrlbar = ttk.Scrollbar(newWindow, orient ="vertical", command = self.table.yview)
        verscrlbar.pack(side ='right', fill ='x')
        
        # Configuring treeview
        self.table.configure(xscrollcommand = verscrlbar.set)

        self.table.column("#0", width=0,  stretch=YES)
        self.table.column("id", anchor=CENTER, width=30)
        self.table.column("name", anchor=CENTER, width=200)
        self.table.column("symptom", anchor=CENTER, width=100)
        self.table.column("emergency_case", anchor=CENTER, width=100)
        self.table.column("time", anchor=CENTER, width=200)

        self.table.heading("id", text="No.", anchor=CENTER)
        self.table.heading("name", text="Name", anchor=CENTER)
        self.table.heading("symptom", text="Symptom", anchor=CENTER)
        self.table.heading("emergency_case", text="Emergency Case", anchor=CENTER)
        self.table.heading("time", text="Arrival Time", anchor=CENTER)

        Button(newWindow, text="treatment done", fg="black", bg ="white", command=self.done).place(x=20, y=235)

        newWindow.title("Doctor's view")
        newWindow.geometry(self.windowSize)

        self.refresh_patient_queue()
    
    def done(self):
        if len(self.queue) == 0:
            return None
        # pop most important patient
        self.queue.pop(0)

        self.refresh_patient_queue()
        if self.patient_view:
            self.patient_view.refresh_patient_queue()

        self.hospital.save_patient_list_to_file()

    def refresh_patient_queue(self):
        found_window = False
        for child in self.root.winfo_children():
            if child.winfo_name() == "top_lvl_doctor":
                found_window = True
        if not found_window:
            return

        self.table.delete(*self.table.get_children())
        ind = 1
        for p in self.queue:
            # insert 'name', 'symptom', 'emergency_case', 'time'
            patient_info = (
                ind, p.name, p.symptom, "Yes" if p.is_emergency else "No", p.arrival_time
            )
            self.table.insert("", "end", text ="", values=patient_info)
            ind += 1

class PatientView:
    def __init__(self, root, queue, hospital):
        self.windowSize = "970x250"
        self.bg_color = "white"
        self.button_color = "white"
        self.box_color = "grey"
        self.root = root
        self.hospital = hospital

        # input boxes
        self.emergency = StringVar()
        self.emergency.set("No")

        self.queue = queue

        self.doctor_view = None
    
    def set_doctor_view(self, doctor_view:DoctorView):
        self.doctor_view = doctor_view
    
    #--------------------------patient window----------------------------
    def clear(self):
        self.p_name.delete(0, END)
        self.p_why.delete(1.0, END)
        self.emergency.set("No")

    def refresh_patient_queue(self):
        found_window = False
        for child in self.root.winfo_children():
            if child.winfo_name() == "top_lvl_patient":
                found_window = True
        if not found_window:
            return

        self.table.delete(*self.table.get_children())
        ind = 1
        for p in self.queue:
            # insert 'name', 'symptom', 'emergency_case', 'time'
            patient_info = (
                ind, p.name, p.symptom, "Yes" if p.is_emergency else "No", p.arrival_time
            )
            self.table.insert("", "end", text ="", values=patient_info)
            ind += 1

    def add_patient_to_queue(self, patient):
        self.queue.append(patient)
        self.queue.sort(reverse=True)
        
        self.refresh_patient_queue()

        for each in self.queue:
            print(each.name)

    def submit(self):
        print("A patient submitted information")

        # Validate Info
        warning_messages = []
        if not self.p_name.get() or len(self.p_name.get()) == 0:
            warning_messages.append("Name")
        if not self.p_why.get(1.0, END) or len(self.p_why.get(1.0, END).strip()) == 0:
            warning_messages.append("Symptom")
        if len(warning_messages) != 0:
            final_messages = "The following fields are missing: " + ', '.join(warning_messages)
            print(final_messages)
            showwarning(title="Warning!", message=final_messages)
        
        else:
            arrival_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            patient_info = PatientInfo(
                {
                    "name": self.p_name.get(),
                    "reason": self.p_why.get(1.0, END),
                    "is_emergency": self.emergency.get() == "Yes",
                    "time": arrival_time
                }
            )
            # patient in queue
            print(patient_info)
            self.add_patient_to_queue(patient_info)

            if self.doctor_view:
                self.doctor_view.refresh_patient_queue()

            self.hospital.save_patient_list_to_file()


    def create_patient_view(self):
        for child in self.root.winfo_children():
            if child.winfo_name() == "top_lvl_patient":
                print("Patient View is opened")
                return None

        print("Open Patient View")
        newWindow = Toplevel(self.root, name="top_lvl_patient")

        #name
        Label(newWindow, text="Name", fg="black", font=40, bg=self.bg_color).place(x=800-120, y=30)
        self.p_name = Entry(newWindow, bg=self.box_color)
        self.p_name.place(x=275+570+20-120, y=30)

        #reason
        Label(newWindow, text="Symtomp", fg="black", font=40, bg=self.bg_color).place(x=800-120, y=65)
        self.p_why = Text(newWindow, bg=self.box_color, height =5, width =26)
        self.p_why.place(x=297+570-120, y=70)

        #emergency
        Label(newWindow, text="Emergency", fg="black", font=40, bg=self.bg_color).place(x=800-120, y=150)
        Radiobutton(newWindow, text="Yes", variable=self.emergency, value="Yes").place(x=880-120, y=155)
        Radiobutton(newWindow, text="No", variable=self.emergency, value="No").place(x=930-120, y=155)

        #button
        Button(newWindow, text="SUBMIT", fg="black", bg ="black", command=self.submit).place(x=290+570-120, y=190)
        Button(newWindow, text="CLEAR", fg="black", bg ="black", command=self.clear).place(x=360+570-120, y=190)

        #patient list table
        table_frame = Frame(newWindow)
        table_frame.place(x=20, y=20)
        self.table = ttk.Treeview(table_frame)
        self.table.pack()
        self.table['columns'] = ('id', 'name', 'symptom', 'emergency_case', 'time')

        # Constructing vertical scrollbar
        # with treeview
        verscrlbar = ttk.Scrollbar(newWindow, orient ="vertical", command = self.table.yview)
        verscrlbar.pack(side ='right', fill ='x')
        
        # Configuring treeview
        self.table.configure(xscrollcommand = verscrlbar.set)

        self.table.column("#0", width=0,  stretch=YES)
        self.table.column("id", anchor=CENTER, width=30)
        self.table.column("name", anchor=CENTER, width=200)
        self.table.column("symptom", anchor=CENTER, width=100)
        self.table.column("emergency_case", anchor=CENTER, width=100)
        self.table.column("time", anchor=CENTER, width=200)

        self.table.heading("id", text="No.", anchor=CENTER)
        self.table.heading("name", text="Name", anchor=CENTER)
        self.table.heading("symptom", text="Symptom", anchor=CENTER)
        self.table.heading("emergency_case", text="Emergency Case", anchor=CENTER)
        self.table.heading("time", text="Arrival Time", anchor=CENTER)
        
        newWindow.title("Patient's")
        newWindow.geometry(self.windowSize)

        self.refresh_patient_queue()

class Hospital:
    def __init__(self):
        self.windowSize = "500x280"
        self.root = Tk()

        #Variables
        self.bg_color = "white"
        self.box_color = "yellow"
        self.database_file = "./patient_lists.pk"

        self.queue = []

        self.doctor_view = DoctorView(self.root, self.queue, self)
        self.patient_view = PatientView(self.root, self.queue, self)
        self.doctor_view.set_patient_view(self.patient_view)
        self.patient_view.set_doctor_view(self.doctor_view)

        self.load_queue_from_file()
    
    def load_queue_from_file(self):
        if os.path.isfile(self.database_file) :
            file = open(self.database_file, 'rb')
            data = pickle.load(file)

            # close the file
            file.close()
            for item in data:
                self.queue.append(item)
            self.queue.sort(reverse=True)
        
    def save_patient_list_to_file(self):
        pickle.dump(self.queue, open(self.database_file ,'wb+'))
        
    #----------------------------Main window-----------------------------
    def create_hospital_view(self):
        #text
        Label(self.root, text="\nPlease Select\n", fg="black", font=40, bg=self.bg_color).pack()

        #button
        Button(self.root, text="PATIENT", fg="black", bg ="black", command=self.patient_view.create_patient_view).place(x=120, y=150)
        Button(self.root, text="DOCTOR", fg="black", bg ="black", command=self.doctor_view.create_doctor_view).place(x=300, y=150)

        #window
        self.root.geometry(self.windowSize)
        self.root.title("Queing Management System")
        self.root.mainloop()


if __name__ == "__main__":
    my_hospital = Hospital()
    my_hospital.create_hospital_view()
