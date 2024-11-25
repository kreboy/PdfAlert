import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk  # Für das Logo
import time
import threading
import os
import random
import subprocess

class PDFReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFAlert")
        self.root.geometry("800x600")
        self.root.config(bg="#2E2E2E")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, 'assets', 'logo', 'logo.png')
        self.logo_image = Image.open(logo_path)
        self.logo_image = self.logo_image.resize((100, 100))
        self.logo = ImageTk.PhotoImage(self.logo_image)

        self.root.iconphoto(True, self.logo)

        self.logo_label = tk.Label(
            root,
            image=self.logo,
            bg="#2E2E2E"
        )
        self.logo_label.pack(pady=10)

        self.label = tk.Label(
            root,
            text="Willkommen zum PDFAlert!",
            font=("Helvetica Neue", 16, "bold"),
            bg="#2E2E2E",
            fg="white",
            pady=10
        )
        self.label.pack()

        self.select_folder_button = ttk.Button(
            root,
            text="Ordner mit PDFs auswählen",
            command=self.select_folder,
            style="SelectFolder.TButton",
        )
        self.select_folder_button.pack(pady=10)

        self.time_label = tk.Label(
            root,
            text="Wähle die Zeit für die Erinnerung (in Minuten):",
            font=("Helvetica Neue", 10),
            bg="#3A3A3A",
            fg="white",
            pady=10
        )
        self.time_label.pack()

        # Zeit Spinner (Spinbox)
        self.time_spinbox = ttk.Spinbox(
            root,
            from_=10,
            to=300,
            font=("Helvetica Neue", 12),
            width=5
        )
        self.time_spinbox.pack(pady=10)

        # Start-Reminder Button
        self.start_button = ttk.Button(
            root,
            text="Erinnerung starten",
            command=self.start_reminder,
            style="TButton",
            state=tk.DISABLED
        )
        self.start_button.pack(pady=10)

        self.exit_button = ttk.Button(
            root,
            text="Beenden",
            command=root.quit,
            style="Exit.TButton",
        )
        self.exit_button.pack(pady=20)

        self.color_picker_button = ttk.Button(
            root,
            text="Wähle eine Farbe für das Menü",
            command=self.choose_color,
            style="ColorPicker.TButton",
        )
        self.color_picker_button.pack(pady=10)

        style = ttk.Style()
        style.configure("TButton",
                        padding=6,
                        relief="flat",
                        background="#4CAF50",
                        foreground="black",
                        font=("Helvetica Neue", 12, "bold"))
        style.map("TButton",
                  background=[('active', '#45a049')],
                  foreground=[('active', 'white')])

        style.configure("Exit.TButton",
                        padding=10,
                        relief="flat",
                        background="#003366",
                        foreground="black",
                        font=("Helvetica Neue", 14, "bold"))
        style.map("Exit.TButton",
                  background=[('active', '#002a52')],
                  foreground=[('active', 'black')])

        style.configure("SelectFolder.TButton",
                        padding=6,
                        relief="flat",
                        background="#003366",
                        foreground="black",
                        font=("Helvetica Neue", 12, "bold"))
        style.map("SelectFolder.TButton",
                  background=[('active', '#002a52')],
                  foreground=[('active', 'black')])

        style.configure("ColorPicker.TButton",
                        padding=6,
                        relief="flat",
                        background="#FF6347",
                        foreground="black",
                        font=("Helvetica Neue", 12, "bold"))
        style.map("ColorPicker.TButton",
                  background=[('active', '#e55347')],
                  foreground=[('active', 'white')])

        self.pdf_folder = None
        self.opened_pdfs = []
        self.last_pdf = None
        self.first_time = True

        if self.first_time:
            messagebox.showinfo("WICHTIG", "Denke daran, die PDF nach dem Lesen zu schließen!")
            self.first_time = False

    def choose_color(self):
        """Farbwahl mit dem Color Picker-Dialog."""
        color = askcolor()[1]
        if color:
            self.update_color(color)

    def update_color(self, color):
        """Aktualisiert die Hintergrundfarbe des Fensters und andere Widgets."""
        self.root.config(bg=color)
        self.label.config(bg=color)
        self.select_folder_button.config(style="SelectFolder.TButton")
        self.time_label.config(bg=color)
        self.time_spinbox.config(bg=color)

    def select_folder(self):
        """Lässt den Benutzer einen Ordner auswählen, in dem sich die PDFs befinden."""
        folder = filedialog.askdirectory(title="Ordner mit PDFs auswählen")
        if folder:
            self.pdf_folder = folder
            messagebox.showinfo("Ordner ausgewählt", f"Ordner '{self.pdf_folder}' wurde ausgewählt!")
            self.start_button.config(state=tk.NORMAL)

    def show_reminder(self):
        """Zeigt ein Popup-Fenster als Erinnerung und öffnet zufällige PDFs."""
        if not self.pdf_folder:
            messagebox.showerror("Fehler", "Kein Ordner mit PDFs ausgewählt!")
            return

        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith(".pdf")]

        if not pdf_files:
            messagebox.showerror("Fehler", "Keine PDFs im Ordner gefunden!")
            return

        reminder_interval = int(self.time_spinbox.get()) * 60

        while True:
            time.sleep(reminder_interval)
            messagebox.showinfo("PDF Erinnerung", "Zeit, ein PDF zu lesen!")

            remaining_pdfs = [f for f in pdf_files if f not in self.opened_pdfs]

            if not remaining_pdfs:
                self.opened_pdfs = []
                remaining_pdfs = pdf_files

            random_pdf = random.choice([f for f in remaining_pdfs if f != self.last_pdf])

            self.opened_pdfs.append(random_pdf)
            self.last_pdf = random_pdf

            pdf_path = os.path.join(self.pdf_folder, random_pdf)

            subprocess.Popen([pdf_path], shell=True)

    def start_reminder(self):
        """Startet die Erinnerung in einem separaten Thread."""
        reminder_thread = threading.Thread(target=self.show_reminder)
        reminder_thread.daemon = True
        reminder_thread.start()

        messagebox.showinfo("Erinnerung gestartet", "Die Erinnerung wurde erfolgreich gestartet!")
        self.start_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReminderApp(root)
    root.mainloop()
