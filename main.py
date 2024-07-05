import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import qrcode
import os
from fpdf import FPDF
import threading
import uuid
import mysql.connector
import datetime
# Configure the MySQL database connection
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'database': 'your_database'
}

#conn = mysql.connector.connect(**db_config)
#cursor = conn.cursor()
#cursor.execute('''
#    CREATE TABLE IF NOT EXISTS tickets (
#        id INT AUTO_INCREMENT PRIMARY KEY,
#        uuid VARCHAR(36) NOT NULL
#    )
#''')
#conn.commit()

class TicketGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket Generator")

        # Initialize variables
        self.date = tk.StringVar(value=datetime.datetime.now().strftime("%d/%m/%Y %H:%MH-%H:%MH"))
        self.num_tickets = tk.IntVar(value=30)
        self.qr_url = tk.StringVar(value="https://chat.whatsapp.com/yourgroupinviteurl")
        self.base_image_path = "entrada.png"
        # Replace / by _
        self.output_pdf_path = "tickets_" + self.date.get().replace("/", "_").replace(" ", "_").replace(":", "_") + ".pdf"
        self.text_x = tk.IntVar(value=220)
        self.text_y = tk.IntVar(value=130)
        self.qr_x = tk.IntVar(value=22)
        self.qr_y = tk.IntVar(value=45)
        self.font_size = tk.IntVar(value=16)
        self.font_path = "typewriter.ttf"  # Path to the Arial font file
        self.entry_width = 30
        # Create UI elements
        ttk.Label(root, text="Fecha:").grid(row=0, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(root, textvariable=self.date, width=self.entry_width)
        self.date_entry.grid(row=0, column=1)

        ttk.Label(root, text="Número de entradas:").grid(row=1, column=0, sticky=tk.W)
        self.num_tickets_entry = ttk.Entry(root, textvariable=self.num_tickets, width=self.entry_width)
        self.num_tickets_entry.grid(row=1, column=1)

        ttk.Label(root, text="URL del QR:").grid(row=2, column=0, sticky=tk.W)
        self.qr_url_entry = ttk.Entry(root, textvariable=self.qr_url, width=self.entry_width)
        self.qr_url_entry.grid(row=2, column=1)

        ttk.Label(root, text="Posición X del Texto:").grid(row=3, column=0, sticky=tk.W)
        self.text_x_entry = ttk.Entry(root, textvariable=self.text_x, width=self.entry_width)
        self.text_x_entry.grid(row=3, column=1)

        ttk.Label(root, text="Posición Y del Texto:").grid(row=4, column=0, sticky=tk.W)
        self.text_y_entry = ttk.Entry(root, textvariable=self.text_y, width=self.entry_width)
        self.text_y_entry.grid(row=4, column=1)

        ttk.Label(root, text="Posición X del QR:").grid(row=5, column=0, sticky=tk.W)
        self.qr_x_entry = ttk.Entry(root, textvariable=self.qr_x, width=self.entry_width)
        self.qr_x_entry.grid(row=5, column=1)

        ttk.Label(root, text="Posición Y del QR:").grid(row=6, column=0, sticky=tk.W)
        self.qr_y_entry = ttk.Entry(root, textvariable=self.qr_y, width=self.entry_width)
        self.qr_y_entry.grid(row=6, column=1)

        ttk.Label(root, text="Tamaño de la Fuente:").grid(row=7, column=0, sticky=tk.W)
        self.font_size_entry = ttk.Entry(root, textvariable=self.font_size, width=self.entry_width)
        self.font_size_entry.grid(row=7, column=1)

        self.preview_label = ttk.Label(root)
        self.preview_label.grid(row=8, column=0, columnspan=2, pady=10)

        self.generate_button = ttk.Button(root, text="Generar Tickets", command=self.start_generation)
        self.generate_button.grid(row=9, column=0, columnspan=2, pady=10)

        self.progress = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
        self.progress.grid(row=10, column=0, columnspan=2, pady=10)

        self.progress_label = ttk.Label(root, text="0%")
        self.progress_label.grid(row=10, column=0, columnspan=2)

        self.update_preview()

        # Bind update preview to changes
        self.date_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.num_tickets_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.qr_url_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.text_x_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.text_y_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.qr_x_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.qr_y_entry.bind("<KeyRelease>", lambda event: self.update_preview())
        self.font_size_entry.bind("<KeyRelease>", lambda event: self.update_preview())

    def update_preview(self):
        self.create_ticket(1, self.date.get(), self.qr_url.get(), self.base_image_path, "preview.png")
        preview_image = Image.open("preview.png")
        # Width and height of the preview label
        width, height = preview_image.size
        preview_image = preview_image.resize((int(width/2), int(height/2)), Image.LANCZOS)  # Resize image to fit the preview label
        preview_photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.config(image=preview_photo)
        self.preview_label.image = preview_photo
        os.remove("preview.png")

    def create_ticket(self, entry_number, date, qr_url, base_image_path, output_image_path):
        # Generate a UUID for the ticket
        ticket_uuid = str(uuid.uuid4())

        # Save the UUID to the database
        #cursor.execute('INSERT INTO tickets (uuid, date, entry_number) VALUES (%s, %s, %s)', (ticket_uuid, date, entry_number))
        #conn.commit()

        # Load base image
        base = Image.open(base_image_path).convert('RGBA')
        width, height = base.size

        # Create QR code with UUID
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(ticket_uuid)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white').convert('RGBA')
        qr_img = qr_img.resize((100, 100))  # Resize QR code

        # Place QR code on the ticket
        base.paste(qr_img, (self.qr_x.get(), self.qr_y.get()), qr_img)

        # Add text (entry number and date)
        draw = ImageDraw.Draw(base)
        font = ImageFont.truetype(self.font_path, self.font_size.get())  # Load Arial font
        text = f"Entrada No: {entry_number}\nFecha: {date}"
        text_position = (self.text_x.get(), self.text_y.get())
        draw.text(text_position, text, font=font, fill=(0, 0, 0))

        # Save the final image
        base.save(output_image_path)

    def start_generation(self):
        thread = threading.Thread(target=self.generate_tickets)
        thread.start()

    def generate_tickets(self):
        pdf = FPDF()
        pdf.set_auto_page_break(0)

        tickets_per_page = 6
        ticket_width = 211  # Full width of the A4 page
        ticket_height = 48
        space_between_tickets = 2

        num_tickets = self.num_tickets.get()
        self.progress["maximum"] = num_tickets

        for i in range(1, num_tickets + 1):
            output_image_path = f"ticket_{i}.png"
            self.create_ticket(i, self.date.get(), self.qr_url.get(), self.base_image_path, output_image_path)

            if (i - 1) % tickets_per_page == 0:
                pdf.add_page()
                y_position = 0

            pdf.image(output_image_path, x=0, y=y_position, w=ticket_width)
            y_position += ticket_height + space_between_tickets

            os.remove(output_image_path)  # Clean up the image file after adding it to the PDF

            self.progress["value"] = i
            self.progress_label.config(text=f"{int((i/num_tickets)*100)}%")
            self.root.update_idletasks()

        pdf.output(self.output_pdf_path)

        messagebox.showinfo("Éxito", "PDF con tickets creado exitosamente.")
        self.progress_label.config(text="0%")
        self.progress["value"] = 0

# Create the main window
root = tk.Tk()
app = TicketGeneratorApp(root)
root.mainloop()

# Close the database connection
cursor.close()
conn.close()
