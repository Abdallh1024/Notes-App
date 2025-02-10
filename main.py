import tkinter as tk
import sqlite3
import threading

# إنشاء قاعدة البيانات والجداول
conn = sqlite3.connect("notes.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL
)
""")
conn.commit()

def clear_warning():
    threading.Timer(2.0, lambda: warning_label.config(text="")).start()

def save_note():
    note_text = text_area.get("1.0", tk.END).strip()
    if note_text:
        if edit_mode.get():
            c.execute("UPDATE notes SET content = ? WHERE id = ?", (note_text, note_to_edit.get()))
            warning_label.config(text="تم تحديث الملاحظة!", fg="#a3be8c")
        else:
            c.execute("INSERT INTO notes (content) VALUES (?)", (note_text,))
            warning_label.config(text="تم حفظ الملاحظة!", fg="#a3be8c")
        conn.commit()
        text_area.delete("1.0", tk.END)
        switch_to_main_view()
        load_notes()
    else:
        warning_label.config(text="لا يمكن حفظ ملاحظة فارغة!", fg="#bf616a")
    clear_warning()

def load_notes():
    listbox.delete(0, tk.END)
    c.execute("SELECT id, content FROM notes")
    for row in c.fetchall():
        listbox.insert(tk.END, f"{row[0]}: {row[1][:30]}...")

def delete_note():
    try:
        selected = listbox.curselection()[0]
        note_id = int(listbox.get(selected).split(":")[0])
        confirm_frame.pack(pady=10)
        global note_to_delete
        note_to_delete = note_id
    except IndexError:
        warning_label.config(text="يرجى اختيار ملاحظة لحذفها!", fg="#bf616a")
        clear_warning()

def confirm_delete():
    global note_to_delete
    c.execute("DELETE FROM notes WHERE id = ?", (note_to_delete,))
    conn.commit()
    confirm_frame.pack_forget()
    warning_label.config(text="تم حذف الملاحظة!", fg="#a3be8c")
    load_notes()
    clear_warning()

def cancel_delete():
    confirm_frame.pack_forget()

def edit_note():
    try:
        selected = listbox.curselection()[0]
        note_id = int(listbox.get(selected).split(":")[0])
        c.execute("SELECT content FROM notes WHERE id = ?", (note_id,))
        note_content = c.fetchone()[0]
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", note_content)
        note_to_edit.set(note_id)
        edit_mode.set(True)
        show_add_note()
    except IndexError:
        warning_label.config(text="يرجى اختيار ملاحظة لتعديلها!", fg="#bf616a")
        clear_warning()

def close_app():
    root.destroy()

def show_add_note():
    listbox.pack_forget()
    button_frame.pack_forget()
    add_button.place_forget()
    text_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    back_button.pack(pady=5, fill=tk.X)
    text_area.focus_set()
    warning_label.config(text="")

def switch_to_main_view():
    text_frame.pack_forget()
    back_button.pack_forget()
    listbox.pack(pady=10, fill=tk.BOTH, expand=True)
    button_frame.pack(pady=5)
    add_button.place(relx=0.95, rely=0.9, anchor="se")
    warning_label.config(text="")
    edit_mode.set(False)

# واجهة المستخدم
root = tk.Tk()
root.title("تطبيق الملاحظات")
root.geometry("400x600")
root.configure(bg="#2e3440")
root.resizable(True, True)

edit_mode = tk.BooleanVar(value=False)
note_to_edit = tk.IntVar(value=0)

warning_label = tk.Label(root, text="", fg="#eceff4", bg="#2e3440", font=("Arial", 12, "bold"))
warning_label.pack()

text_frame = tk.Frame(root, bg="#2e3440")
text_area = tk.Text(text_frame, height=10, bg="#3b4252", fg="#eceff4", insertbackground="#eceff4", font=("Arial", 12))
text_area.pack(expand=True, fill=tk.BOTH)

save_button = tk.Button(text_frame, text="حفظ الملاحظة", command=save_note, bg="#81a1c1", fg="white", font=("Arial", 12, "bold"))
save_button.pack(pady=5)

text_frame.pack_forget()

back_button = tk.Button(root, text="⬅", command=switch_to_main_view, bg="#4c566a", fg="#eceff4", font=("Arial", 14, "bold"), borderwidth=0)
back_button.pack_forget()

listbox = tk.Listbox(root, height=10, bg="#3b4252", fg="#eceff4", font=("Arial", 12))
listbox.pack(pady=10, fill=tk.BOTH, expand=True)

load_notes()

button_frame = tk.Frame(root, bg="#2e3440")
button_frame.pack(pady=5)

delete_button = tk.Button(button_frame, text="🗑", command=delete_note, bg="#2e3440", fg="#eceff4", font=("Arial", 14, "bold"), borderwidth=0)
delete_button.pack(side=tk.LEFT, padx=10)

edit_button = tk.Button(button_frame, text="✏️", command=edit_note, bg="#2e3440", fg="#eceff4", font=("Arial", 14, "bold"), borderwidth=0)
edit_button.pack(side=tk.LEFT, padx=10)

close_button = tk.Button(button_frame, text="❌", command=close_app, bg="#2e3440", fg="#eceff4", font=("Arial", 14, "bold"), borderwidth=0)
close_button.pack(side=tk.LEFT, padx=10)

confirm_frame = tk.Frame(root, bg="#2e3440")
confirm_label = tk.Label(confirm_frame, text="هل أنت متأكد من الحذف؟", fg="#eceff4", bg="#2e3440", font=("Arial", 12, "bold"))
confirm_label.pack()
confirm_yes = tk.Button(confirm_frame, text="نعم", command=confirm_delete, bg="#bf616a", fg="white", font=("Arial", 12, "bold"))
confirm_yes.pack(side=tk.LEFT, padx=10)
confirm_no = tk.Button(confirm_frame, text="إلغاء", command=cancel_delete, bg="#88c0d0", fg="white", font=("Arial", 12, "bold"))
confirm_no.pack(side=tk.RIGHT, padx=10)
confirm_frame.pack_forget()

add_button = tk.Button(root, text="➕", command=show_add_note, bg="#2e3440", fg="#eceff4", font=("Arial", 18, "bold"), borderwidth=0)
add_button.place(relx=0.95, rely=0.9, anchor="se")

root.mainloop()

# إغلاق الاتصال بقاعدة البيانات عند إغلاق التطبيق
conn.close()
