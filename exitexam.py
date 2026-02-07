import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
import os

# Model Database
class PoliticsModel:
    def __init__(self, db_file="politics_gui_db.json"):
        self.db_file = db_file
        if not os.path.exists(self.db_file):
            self.init_mock_data()
        self.load_data()
        self.current_user_role = None

    def init_mock_data(self):
        data = {
            "politicians": [
                {"id": 101, "name": "นายสมชาย ใจดี", "party": "พรรคก้าวหน้า"},
                {"id": 202, "name": "นางสาวจริงใจ รักถิ่น", "party": "พรรคพัฒนาชนบท"},
                {"id": 303, "name": "นายเอกพล คนรุ่นใหม่", "party": "พรรคอนาคตไกล"},
                {"id": 444, "name": "พลเอก มั่นคง", "party": "พรรคพลังเงียบ"},
                {"id": 555, "name": "คุณหญิง สุดารัตน์", "party": "พรรคไทยสร้างสรรค์"}
            ],
            "campaigns": [],
            "promises": [
                {"id": "P01", "pol_id": 101, "desc": "รถไฟฟ้า 20 บาทตลอดสาย", "date": "2023-05-01", "status": "กำลังดำเนินการ"},
                {"id": "P02", "pol_id": 101, "desc": "เพิ่มเบี้ยผู้สูงอายุ", "date": "2023-05-02", "status": "เงียบหาย"},
                {"id": "P03", "pol_id": 202, "desc": "ประกันราคาข้าว", "date": "2023-04-10", "status": "กำลังดำเนินการ"},
                {"id": "P04", "pol_id": 202, "desc": "เรียนฟรีถึงปริญญาตรี", "date": "2023-04-12", "status": "ยังไม่เริ่ม"},
                {"id": "P05", "pol_id": 303, "desc": "สมรสเท่าเทียม", "date": "2023-03-15", "status": "กำลังดำเนินการ"},
                {"id": "P06", "pol_id": 303, "desc": "ยกเลิกเกณฑ์ทหาร", "date": "2023-03-20", "status": "เงียบหาย"},
                {"id": "P07", "pol_id": 444, "desc": "บัตรคนจนพลัส", "date": "2023-02-01", "status": "ยังไม่เริ่ม"},
                {"id": "P08", "pol_id": 444, "desc": "คนละครึ่งเฟสใหม่", "date": "2023-02-05", "status": "เงียบหาย"},
                {"id": "P09", "pol_id": 555, "desc": "SME กู้ดอกเบี้ยต่ำ", "date": "2023-03-01", "status": "กำลังดำเนินการ"},
                {"id": "P10", "pol_id": 555, "desc": "อินเทอร์เน็ตฟรีทุกหมู่บ้าน", "date": "2023-03-05", "status": "ยังไม่เริ่ม"}
            ],
            "updates": [
                {"u_id": 1, "p_id": "P01", "date": "2023-09-01", "detail": "ครม. อนุมัติหลักการแล้ว"},
                {"u_id": 2, "p_id": "P03", "date": "2023-10-01", "detail": "ตั้งคณะกรรมการศึกษาผลกระทบ"}
            ],
            "users": {"admin": "1234", "user": "1234"}
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        with open(self.db_file, 'r', encoding='utf-8') as f:
            self.db = json.load(f)

    def save_data(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=4)

    def login(self, username, password):
        users = self.db.get("users", {})
        if username in users and users[username] == password:
            self.current_user_role = "admin" if username == "admin" else "user"
            return True, self.current_user_role
        return False, None

    def get_all_promises(self):
        # เรียงตามวันที่
        return sorted(self.db['promises'], key=lambda x: x['date'])

    def get_politician_by_id(self, pol_id):
        for p in self.db['politicians']:
            if p['id'] == pol_id:
                return p
        return None

    def get_promise_detail(self, p_id):
        promise = next((p for p in self.db['promises'] if p['id'] == p_id), None)
        if not promise: return None
        politician = self.get_politician_by_id(promise['pol_id'])
        updates = [u for u in self.db['updates'] if u['p_id'] == p_id]
        return {"promise": promise, "politician": politician, "updates": updates}

    def add_update(self, p_id, detail):
        # เช็คสถานะ
        promise = next((p for p in self.db['promises'] if p['id'] == p_id), None)
        if promise['status'] == 'เงียบหาย':
            return False, "ไม่สามารถอัปเดตได้ เนื่องจากสถานะคือ 'เงียบหาย'"
        
        new_update = {
            "u_id": len(self.db['updates']) + 1,
            "p_id": p_id,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "detail": detail
        }
        self.db['updates'].append(new_update)
        self.save_data()
        return True, "บันทึกสำเร็จ"
    
    def get_all_politicians(self):
        return self.db['politicians']
    
    def get_promises_by_pol_id(self, pol_id):
        return [p for p in self.db['promises'] if p['pol_id'] == pol_id]


# View UI
class LoginView(tk.Frame):
    def __init__(self, master, on_login_click):
        super().__init__(master)
        self.pack(pady=50)
        
        tk.Label(self, text="ระบบติดตามสัญญา (Politics Tracker)", font=("Arial", 20)).pack(pady=20)
        
        tk.Label(self, text="Username:").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack()
        
        tk.Label(self, text="Password:").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack()
        
        tk.Button(self, text="เข้าสู่ระบบ", command=lambda: on_login_click(self.entry_user.get(), self.entry_pass.get())).pack(pady=20)

class DashboardView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        # Top Bar
        top_frame = tk.Frame(self, bg="#ddd")
        top_frame.pack(side="top", fill="x")
        tk.Label(top_frame, text="เมนูหลัก", bg="#ddd", font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=5)
        tk.Button(top_frame, text="ออกจากระบบ", command=controller.logout).pack(side="right", padx=10, pady=5)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="ดูคำสัญญาทั้งหมด", width=20, height=2, command=controller.show_promise_list).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="ดูรายชื่อนักการเมือง", width=20, height=2, command=controller.show_politician_list).grid(row=0, column=1, padx=10)

        # Content Area (ที่จะเปลี่ยนไปมา)
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

class PromiseListView(tk.Frame):
    def __init__(self, master, promises, on_select):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        tk.Label(self, text="รายการคำสัญญาทั้งหมด", font=("Arial", 16)).pack(pady=10)
        
        # Table
        cols = ("ID", "Date", "Status", "Description")
        tree = ttk.Treeview(self, columns=cols, show="headings")
        tree.heading("ID", text="รหัส")
        tree.heading("Date", text="วันที่ประกาศ")
        tree.heading("Status", text="สถานะ")
        tree.heading("Description", text="รายละเอียด")
        
        tree.column("ID", width=50)
        tree.column("Date", width=100)
        tree.column("Status", width=100)
        tree.column("Description", width=400)

        for p in promises:
            tree.insert("", "end", values=(p['id'], p['date'], p['status'], p['desc']))
            
        tree.pack(fill="both", expand=True)
        
        # Double Click Event
        tree.bind("<Double-1>", lambda event: on_select(tree))

class PromiseDetailView(tk.Frame):
    def __init__(self, master, data, role, on_back, on_update_click):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        p = data['promise']
        pol = data['politician']
        
        # Header
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)
        tk.Button(header, text="< ย้อนกลับ", command=on_back).pack(side="left")
        tk.Label(header, text=f"รายละเอียดสัญญา: {p['id']}", font=("Arial", 16, "bold")).pack(side="left", padx=20)

        # Info
        info_frame = tk.LabelFrame(self, text="ข้อมูลทั่วไป")
        info_frame.pack(fill="x", pady=5)
        
        tk.Label(info_frame, text=f"นโยบาย: {p['desc']}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(info_frame, text=f"ผู้เสนอ: {pol['name']} ({pol['party']})").pack(anchor="w")
        tk.Label(info_frame, text=f"วันที่: {p['date']} | สถานะ: {p['status']}", fg="blue").pack(anchor="w")

        # Update History
        tk.Label(self, text="ไทม์ไลน์ความคืบหน้า", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        
        cols = ("Date", "Detail")
        tree = ttk.Treeview(self, columns=cols, show="headings", height=5)
        tree.heading("Date", text="วันที่อัปเดต")
        tree.heading("Detail", text="รายละเอียด")
        tree.column("Date", width=100)
        tree.column("Detail", width=400)
        
        for u in data['updates']:
            tree.insert("", "end", values=(u['date'], u['detail']))
        tree.pack(fill="x")

        # Action Button (Check Permission & Status)
        if role == 'admin':
            if p['status'] == 'เงียบหาย':
                tk.Label(self, text="* ไม่สามารถอัปเดตได้เนื่องจากสถานะคือ 'เงียบหาย'", fg="red").pack(pady=10)
            else:
                tk.Button(self, text="เพิ่มความคืบหน้า (Update)", bg="green", fg="white", 
                          command=lambda: on_update_click(p['id'])).pack(pady=10)

class UpdateFormView(tk.Frame):
    def __init__(self, master, promise_id, on_submit, on_cancel):
        super().__init__(master)
        self.pack(fill="both", expand=True, pady=20)
        
        tk.Label(self, text=f"อัปเดตความคืบหน้า: {promise_id}", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(self, text="รายละเอียดสิ่งที่ดำเนินการ:").pack()
        self.txt_detail = tk.Text(self, height=5, width=50)
        self.txt_detail.pack(pady=5)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="บันทึก", command=lambda: on_submit(promise_id, self.txt_detail.get("1.0", "end-1c"))).pack(side="left", padx=5)
        tk.Button(btn_frame, text="ยกเลิก", command=on_cancel).pack(side="left", padx=5)

class PoliticianListView(tk.Frame):
    def __init__(self, master, politicians, on_select):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        tk.Label(self, text="รายชื่อนักการเมือง", font=("Arial", 16)).pack(pady=10)
        
        cols = ("ID", "Name", "Party")
        tree = ttk.Treeview(self, columns=cols, show="headings")
        tree.heading("ID", text="รหัส")
        tree.heading("Name", text="ชื่อ-สกุล")
        tree.heading("Party", text="พรรค")
        
        for p in politicians:
            tree.insert("", "end", values=(p['id'], p['name'], p['party']))
        tree.pack(fill="both", expand=True)
        
        tree.bind("<Double-1>", lambda event: on_select(tree))


# Controller

class PoliticsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Politics Tracker System (MVC Pattern)")
        self.geometry("800x600")
        
        self.model = PoliticsModel()
        self.current_frame = None
        
        # เริ่มต้นที่หน้า Login
        self.show_login()

    def switch_frame(self, frame_class, **kwargs):
        """Utility function สำหรับสลับหน้าจอ"""
        if self.current_frame:
            self.current_frame.destroy()
        
        # สร้าง Frame ใหม่แล้วแสดงผล
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    # --- Login & Main Menu ---
    def show_login(self):
        self.switch_frame(LoginView, on_login_click=self.attempt_login)

    def attempt_login(self, user, pwd):
        success, role = self.model.login(user, pwd)
        if success:
            messagebox.showinfo("Success", f"ยินดีต้อนรับ {role}")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "ชื่อผู้ใช้หรือรหัสผ่านผิด")

    def logout(self):
        self.model.current_user_role = None
        self.show_login()

    def show_dashboard(self):
        # หน้า Dashboard หลัก
        if self.current_frame: self.current_frame.destroy()
        
        # สร้าง Container หลักสำหรับ Dashboard (มีเมนูด้านบน)
        self.dashboard_container = DashboardView(self, self)
        self.dashboard_container.pack(fill="both", expand=True)
        self.current_frame = self.dashboard_container # Track ไว้เพื่อ destroy ตอน logout
        
        # เริ่มต้นแสดง List คำสัญญาใน Content Area ของ Dashboard
        self.show_promise_list()

    # --- Features Logic ---
    
    def show_promise_list(self):
        # Clear content area
        for widget in self.dashboard_container.content_frame.winfo_children():
            widget.destroy()
            
        promises = self.model.get_all_promises()
        # ส่ง function on_select ไปให้ View เมื่อ user ดับเบิ้ลคลิก
        PromiseListView(self.dashboard_container.content_frame, promises, self.on_promise_select)

    def on_promise_select(self, tree):
        item = tree.selection()
        if item:
            p_id = tree.item(item, "values")[0]
            self.show_promise_detail(p_id)

    def show_promise_detail(self, p_id):
        # Clear content area
        for widget in self.dashboard_container.content_frame.winfo_children():
            widget.destroy()

        data = self.model.get_promise_detail(p_id)
        role = self.model.current_user_role
        
        PromiseDetailView(
            self.dashboard_container.content_frame, 
            data, 
            role, 
            on_back=self.show_promise_list,
            on_update_click=self.show_update_form
        )

    def show_update_form(self, p_id):
        # Clear content area
        for widget in self.dashboard_container.content_frame.winfo_children():
            widget.destroy()
            
        UpdateFormView(
            self.dashboard_container.content_frame,
            p_id,
            on_submit=self.submit_update,
            on_cancel=lambda: self.show_promise_detail(p_id)
        )

    def submit_update(self, p_id, detail):
        if not detail.strip():
            messagebox.showwarning("Warning", "กรุณากรอกรายละเอียด")
            return
            
        success, msg = self.model.add_update(p_id, detail)
        if success:
            messagebox.showinfo("Success", msg)
            self.show_promise_detail(p_id) # กลับไปหน้า Detail
        else:
            messagebox.showerror("Error", msg)

    # --- Politician Feature ---
    def show_politician_list(self):
        for widget in self.dashboard_container.content_frame.winfo_children():
            widget.destroy()
        
        pols = self.model.get_all_politicians()
        PoliticianListView(self.dashboard_container.content_frame, pols, self.on_politician_select)

    def on_politician_select(self, tree):
        item = tree.selection()
        if item:
            pol_id = int(tree.item(item, "values")[0])
            self.show_politician_promises(pol_id)

    def show_politician_promises(self, pol_id):
        for widget in self.dashboard_container.content_frame.winfo_children():
            widget.destroy()
        
        # Reuse PromiseListView แต่ filter เฉพาะคนนี้
        promises = self.model.get_promises_by_pol_id(pol_id)
        
        # เพิ่มปุ่มย้อนกลับเฉพาะหน้า
        tk.Button(self.dashboard_container.content_frame, text="< กลับไปหน้ารายชื่อ", 
                  command=self.show_politician_list).pack(anchor="w", pady=5)
        
        if not promises:
            tk.Label(self.dashboard_container.content_frame, text="ไม่พบคำสัญญาของคนนี้").pack()
        else:
            PromiseListView(self.dashboard_container.content_frame, promises, self.on_promise_select)


# Main
if __name__ == "__main__":
    app = PoliticsApp()
    app.mainloop()