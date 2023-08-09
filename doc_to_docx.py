from win32com import client as wc
from tkinter import messagebox
import tkinter as tk
import os


w = wc.Dispatch("Word.Application")
doc = w.Documents.Open(os.path.abspath("E:\\cf88.doc"))
doc.SaveAs("E:\\cf88.docx", 16)

root = tk.Tk()
root.withdraw()
messagebox.showinfo("Sucesso")
