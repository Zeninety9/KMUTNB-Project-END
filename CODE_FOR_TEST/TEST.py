import tkinter as tk

root = tk.Tk()

entry = tk.Entry(root, state="readonly")
entry.pack(pady=20)

def update_entry(new_text):
    entry.config(state="normal")   # เปิดให้แก้ไข
    entry.delete(0, tk.END)        # ลบข้อความเก่า
    entry.insert(0, new_text)      # ใส่ข้อความใหม่
    entry.config(state="readonly") # ปิด readonly กลับ

tk.Button(root, text="Update", command=lambda: update_entry("Hello ESP32")).pack(pady=10)

root.mainloop()
