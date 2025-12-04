from tkinter import *
from tkinter import ttk

root = Tk()
root.title("ปุ่มเปลี่ยน Tab")
root.geometry("600x400")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# สร้าง TAB ต่าง ๆ
tab1 = Frame(notebook, bg="lightblue")
tab2 = Frame(notebook, bg="lightgreen")
tab3 = Frame(notebook, bg="lightyellow")

notebook.add(tab1, text="Tab 1")
notebook.add(tab2, text="Tab 2")
notebook.add(tab3, text="Tab 3")

Label(tab1, text="นี่คือ TAB 1", font=("Arial", 18), bg="lightblue").pack(pady=20)
Label(tab2, text="นี่คือ TAB 2", font=("Arial", 18), bg="lightgreen").pack(pady=20)
Label(tab3, text="นี่คือ TAB 3", font=("Arial", 18), bg="lightyellow").pack(pady=20)

# -----------------------------
# ปุ่มเปลี่ยนหน้า
# -----------------------------
def go_tab1():
    notebook.select(0)

def go_tab2():
    notebook.select(1)

def go_tab3():
    notebook.select(2)

Button(root, text="ไป Tab 1", command=go_tab1).pack(side=LEFT, padx=10, pady=10)
Button(root, text="ไป Tab 2", command=go_tab2).pack(side=LEFT, padx=10, pady=10)
Button(root, text="ไป Tab 3", command=go_tab3).pack(side=LEFT, padx=10, pady=10)

root.mainloop()
