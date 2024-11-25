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
        self.root.config(bg="#2E2E2E")  # Dunklerer Hintergrund für die Box

        # Dynamisch den Pfad zum Logo erstellen
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Ordner des Skripts
        logo_path = os.path.join(script_dir, 'assets', 'logo', 'logo.png')  # Pfad zum Logo
        self.logo_image = Image.open(logo_path)  # Bild laden
        self.logo_image = self.logo_image.resize((100, 100))  # Größe des Logos anpassen
        self.logo = ImageTk.PhotoImage(self.logo_image)

        # Setze das Icon für das Fenster
        self.root.iconphoto(True, self.logo)

        # Logo-Label
        self.logo_label = tk.Label(
            root,
            image=self.logo,
            bg="#2E2E2E"
        )
        self.logo_label.pack(pady=10)

        # Titel Label
        self.label = tk.Label(
            root,
            text="Willkommen zum PDFAlert!",
            font=("Helvetica Neue", 16, "bold"),
            bg="#2E2E2E",
            fg="white",  # Helle Schriftfarbe für besseren Kontrast
            pady=10
        )
        self.label.pack()

        # Ordner auswählen Button
        self.select_folder_button = ttk.Button(
            root,
            text="Ordner mit PDFs auswählen",
            command=self.select_folder,
            style="SelectFolder.TButton",
        )
        self.select_folder_button.pack(pady=10)

        # Zeit einstellen Label
        self.time_label = tk.Label(
            root,
            text="Wähle die Zeit für die Erinnerung (in Minuten):",
            font=("Helvetica Neue", 10),
            bg="#3A3A3A",  # Dunklerer Hintergrund für das Label
            fg="white",  # Weiße Schriftfarbe
            pady=10
        )
        self.time_label.pack()

        # Zeit Spinner (Spinbox)
        self.time_spinbox = ttk.Spinbox(
            root,
            from_=10,
            to=300,  # 5 Stunden = 300 Minuten
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
            state=tk.DISABLED  # Zu Beginn deaktiviert
        )
        self.start_button.pack(pady=10)

        # Exit Button
        self.exit_button = ttk.Button(
            root,
            text="Beenden",
            command=root.quit,
            style="Exit.TButton",
        )
        self.exit_button.pack(pady=20)

        # Color Picker Button
        self.color_picker_button = ttk.Button(
            root,
            text="Wähle eine Farbe für das Menü",
            command=self.choose_color,
            style="ColorPicker.TButton",
        )
        self.color_picker_button.pack(pady=10)

        # Style für Buttons anpassen
        style = ttk.Style()
        style.configure("TButton",
                        padding=6,
                        relief="flat",
                        background="#4CAF50",  # Grüner Button
                        foreground="black",  # Schwarze Schriftfarbe
                        font=("Helvetica Neue", 12, "bold"))
        style.map("TButton",
                  background=[('active', '#45a049')],  # Button-Farbe bei Hover
                  foreground=[('active', 'white')])

        # Spezielle Anpassung für den Exit-Button (Beenden)
        style.configure("Exit.TButton",
                        padding=10,
                        relief="flat",
                        background="#003366",  # Dunkelblau für den Beenden-Button
                        foreground="black",  # Schwarze Schriftfarbe
                        font=("Helvetica Neue", 14, "bold"))  # Dickerer Button
        style.map("Exit.TButton",
                  background=[('active', '#002a52')],  # Dunkleres Blau bei Hover
                  foreground=[('active', 'black')])

        # Spezielle Anpassung für den Ordner-Auswahl-Button
        style.configure("SelectFolder.TButton",
                        padding=6,
                        relief="flat",
                        background="#003366",  # Dunkelblau für den Button
                        foreground="black",  # Schwarze Schriftfarbe
                        font=("Helvetica Neue", 12, "bold"))  # Etwas dickere Schrift
        style.map("SelectFolder.TButton",
                  background=[('active', '#002a52')],  # Dunkleres Blau bei Hover
                  foreground=[('active', 'black')])

        # Spezielle Anpassung für den ColorPicker-Button
        style.configure("ColorPicker.TButton",
                        padding=6,
                        relief="flat",
                        background="#FF6347",  # Tomatenfarbe für den Button
                        foreground="black",  # Schwarze Schriftfarbe
                        font=("Helvetica Neue", 12, "bold"))
        style.map("ColorPicker.TButton",
                  background=[('active', '#e55347')],  # Dunkleres Rot bei Hover
                  foreground=[('active', 'white')])

        self.pdf_folder = None
        self.opened_pdfs = []  # Liste der geöffneten PDFs
        self.last_pdf = None  # Variable für die zuletzt geöffnete PDF
        self.first_time = True  # Flag für den ersten Start des Programms

        # Überprüfe, ob es das erste Mal ist, dass die Anwendung gestartet wird
        if self.first_time:
            messagebox.showinfo("WICHTIG", "Denke daran, die PDF nach dem Lesen zu schließen!")
            self.first_time = False

    def choose_color(self):
        """Farbwahl mit dem Color Picker-Dialog."""
        color = askcolor()[1]  # Gibt den Farbcode im Hex-Format zurück, z.B. "#ff5733"
        if color:
            self.update_color(color)

    def update_color(self, color):
        """Aktualisiert die Hintergrundfarbe des Fensters und andere Widgets."""
        self.root.config(bg=color)  # Fenster Hintergrundfarbe ändern
        self.label.config(bg=color)  # Titel-Label Hintergrundfarbe ändern
        self.select_folder_button.config(style="SelectFolder.TButton")
        self.time_label.config(bg=color)  # Zeit Label Hintergrundfarbe ändern
        self.time_spinbox.config(bg=color)  # Zeit Spinbox Hintergrundfarbe ändern

    def select_folder(self):
        """Lässt den Benutzer einen Ordner auswählen, in dem sich die PDFs befinden."""
        folder = filedialog.askdirectory(title="Ordner mit PDFs auswählen")
        if folder:
            self.pdf_folder = folder
            messagebox.showinfo("Ordner ausgewählt", f"Ordner '{self.pdf_folder}' wurde ausgewählt!")
            self.start_button.config(state=tk.NORMAL)  # Start-Button aktivieren

    def show_reminder(self):
        """Zeigt ein Popup-Fenster als Erinnerung und öffnet zufällige PDFs."""
        if not self.pdf_folder:
            messagebox.showerror("Fehler", "Kein Ordner mit PDFs ausgewählt!")
            return

        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith(".pdf")]

        # Sicherstellen, dass mindestens eine PDF existiert
        if not pdf_files:
            messagebox.showerror("Fehler", "Keine PDFs im Ordner gefunden!")
            return

        reminder_interval = int(self.time_spinbox.get()) * 60  # Umrechnung von Minuten in Sekunden

        while True:
            time.sleep(reminder_interval)  # Warten nach der eingestellten Zeit
            # Zeige Erinnerungspopup
            messagebox.showinfo("PDF Erinnerung", "Zeit, ein PDF zu lesen!")

            # Überprüfen, ob noch PDFs übrig sind, die noch nicht geöffnet wurden
            remaining_pdfs = [f for f in pdf_files if f not in self.opened_pdfs]

            if not remaining_pdfs:
                # Wenn keine PDFs übrig sind, setze die Liste zurück und beginne von vorne
                self.opened_pdfs = []
                remaining_pdfs = pdf_files

            # Zufällige PDF aus den verbleibenden PDFs auswählen, aber sicherstellen, dass es nicht die gleiche ist wie die letzte
            random_pdf = random.choice([f for f in remaining_pdfs if f != self.last_pdf])

            self.opened_pdfs.append(random_pdf)
            self.last_pdf = random_pdf  # Setze die zuletzt geöffnete PDF

            pdf_path = os.path.join(self.pdf_folder, random_pdf)
            
            # PDF mit dem Standard-PDF-Viewer öffnen
            subprocess.Popen([pdf_path], shell=True)

    def start_reminder(self):
        """Startet die Erinnerung in einem separaten Thread."""
        reminder_thread = threading.Thread(target=self.show_reminder)
        reminder_thread.daemon = True  # Der Thread wird beendet, wenn die Hauptanwendung beendet wird
        reminder_thread.start()

        # Erfolgreich-Meldung nach dem Start
        messagebox.showinfo("Erinnerung gestartet", "Die Erinnerung wurde erfolgreich gestartet!")
        self.start_button.config(state=tk.DISABLED)  # Deaktiviert den Button nach dem Start


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReminderApp(root)
    root.mainloop()
