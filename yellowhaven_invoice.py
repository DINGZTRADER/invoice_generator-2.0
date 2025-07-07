import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dateutil.parser import parse
from fpdf import FPDF
import pandas as pd
import os
from PIL import Image, ImageTk

# --- COLOR AND BRAND SETTINGS ---
BG_COLOR = "#232323"
FG_COLOR = "#FFE066"
CARD_COLOR = "#333333"
BTN_COLOR = "#FFE066"
BTN_TEXT = "#191919"
FIELD_BG = "#292929"
FIELD_FG = "#FFE066"

ROOM_RATES = {
    "Crested Crane ($98)":     {"rate": 98,  "max": 4},
    "Wild Geese ($135)":        {"rate": 135, "max": 3},
    "Kingfisher ($110)":        {"rate": 110, "max": 5},
    "Ross Turaco ($110)":       {"rate": 110, "max": 3},
    "Tower ($55)":             {"rate": 55,  "max": 2},
    "Wax Bill ($95)":          {"rate": 95,  "max": 4},
    "Starling ($85)":          {"rate": 85,  "max": 2},
    "Ibis ($75)":              {"rate": 75,  "max": 3},
    "Caven ($100)":             {"rate": 100, "max": 2},
    "Tree House The Crown ($100)": {"rate": 100, "max": 2},
    "Sunbird ($98)":           {"rate": 98,  "max": 3},
}
EXTRA_GUEST_RATE = 22
BREAKFAST_RATE = 10
CONFERENCE_ROOM_RATE = 120

class InvoiceGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yellow Haven Lodge - Invoice Generator")
        self.root.geometry("830x780")
        self.root.configure(bg=BG_COLOR)

        # --- LOGO AT TOP (transparent background recommended) ---
        try:
            logo_img = Image.open("logo2.png")  # Should be a transparent PNG
            logo_img = logo_img.resize((240, 100), Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(root, image=self.logo_tk, bg=BG_COLOR, bd=0)
            logo_label.place(x=20, y=8)
        except Exception as e:
            logo_label = tk.Label(root, text="Yellow Haven Lodge", font=("Arial Black", 22, "bold"), bg=BG_COLOR, fg=FG_COLOR)
            logo_label.place(x=30, y=14)

        # --- Header (minimal, moved up) ---
        header = tk.Label(root, text="INVOICE", font=("Arial Black", 28, "bold"),
                          bg=BG_COLOR, fg=FG_COLOR)
        header.place(x=400, y=28)
        date_str = datetime.now().strftime("%d %B, %Y")
        self.date_label = tk.Label(root, text=f"Date: {date_str}",
                                   font=("Arial", 10, "bold"),
                                   bg=BG_COLOR, fg=FG_COLOR)
        self.date_label.place(x=650, y=22)
        self.inv_no_label = tk.Label(root, text="Invoice no: [auto-generated]",
                                   font=("Arial", 10),
                                   bg=BG_COLOR, fg=FG_COLOR)
        self.inv_no_label.place(x=650, y=40)

        # --- Main card (moved up) ---
        self.card = tk.Frame(root, bg=CARD_COLOR, bd=0, relief="flat", highlightthickness=0)
        self.card.place(x=25, y=110, width=780, height=590)

        # Guest Info
        self.create_guest_info_frame()
        # Room Selection
        self.create_room_selection_frame()
        # Extras
        self.create_extras_frame()
        # Breakfast
        self.create_breakfast_frame()
        # Summary
        self.create_preview_frame()

        # Generate Button
        tk.Button(self.card, text="Generate Invoice", command=self.generate_invoice,
                  bg=BTN_COLOR, fg=BTN_TEXT, font=("Arial Black", 15),
                  activebackground="#FFD300", activeforeground=BTN_TEXT,
                  relief='flat', bd=0, padx=18, pady=8
                  ).pack(pady=(12, 18))

    def create_guest_info_frame(self):
        frame = tk.Frame(self.card, bg=CARD_COLOR)
        frame.pack(fill='x', pady=(5,2), padx=12)
        tk.Label(frame, text="Guest Name:", font=("Arial", 11, "bold"),
                 bg=CARD_COLOR, fg=FG_COLOR).grid(row=0, column=0, sticky='w', padx=4)
        self.guest_name = tk.Entry(frame, width=28, font=("Arial", 12), bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR, relief="flat")
        self.guest_name.grid(row=0, column=1, padx=(0,16), sticky='w')

        tk.Label(frame, text="Payment by:", font=("Arial", 11, "bold"),
                 bg=CARD_COLOR, fg=FG_COLOR).grid(row=0, column=2, sticky='w', padx=4)
        self.payment_method = ttk.Combobox(frame, values=["Cash", "Card", "Mobile Money", "Bank Transfer"], width=20, font=("Arial", 11))
        self.payment_method.set("Cash")
        self.payment_method.grid(row=0, column=3, sticky='w')

        tk.Label(frame, text="Check-in Date:", font=("Arial", 11),
                 bg=CARD_COLOR, fg=FG_COLOR).grid(row=1, column=0, sticky='w', padx=4, pady=7)
        self.checkin = tk.Entry(frame, width=24, font=("Arial", 12), bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR, relief="flat")
        self.checkin.insert(0, "e.g. 18 June 2025")
        self.checkin.grid(row=1, column=1, padx=(0,16), sticky='w')

        tk.Label(frame, text="Check-out Date:", font=("Arial", 11),
                 bg=CARD_COLOR, fg=FG_COLOR).grid(row=1, column=2, sticky='w', padx=4, pady=7)
        self.checkout = tk.Entry(frame, width=24, font=("Arial", 12), bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR, relief="flat")
        self.checkout.insert(0, "e.g. 21 June 2025")
        self.checkout.grid(row=1, column=3, sticky='w')

    def create_room_selection_frame(self):
        section = tk.Frame(self.card, bg=CARD_COLOR)
        section.pack(fill='x', pady=(8,2), padx=12)
        tk.Label(section, text="Room Selection", font=("Arial", 13, "bold"),
                 bg=CARD_COLOR, fg=FG_COLOR).grid(row=0, column=0, sticky='w', columnspan=4)
        self.room_frame = tk.Frame(section, bg=CARD_COLOR)
        self.room_frame.grid(row=1, column=0, columnspan=4, sticky='ew')
        self.rooms = []
        self.add_room_row()
        tk.Button(section, text="Add Room", command=self.add_room_row,
                  bg=BTN_COLOR, fg=BTN_TEXT, font=("Arial", 10, "bold"),
                  relief='flat', padx=8, pady=3).grid(row=2, column=0, sticky='w', pady=4)
        tk.Label(section, text="* Each extra guest after the first: $22", bg=CARD_COLOR,
                 fg="#FFD300", font=("Arial Black", 13, "bold")).grid(row=3, column=0, columnspan=4, sticky="w", pady=(6,0))

    def add_room_row(self):
        frame = tk.Frame(self.room_frame, bg=CARD_COLOR)
        frame.pack(pady=2, fill='x')
        tk.Label(frame, text="Room:", bg=CARD_COLOR, fg=FG_COLOR).pack(side='left')
        room_type = ttk.Combobox(frame, values=list(ROOM_RATES.keys()), width=28, state="readonly", font=("Arial", 11))
        room_type.pack(side='left', padx=5)
        tk.Label(frame, text="Guests:", bg=CARD_COLOR, fg=FG_COLOR).pack(side='left')
        pax = tk.Spinbox(frame, from_=1, to=1, width=3, font=("Arial", 11), bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR)
        pax.pack(side='left', padx=5)
        room_type.bind("<<ComboboxSelected>>", lambda e, rtype=room_type, px=pax: self.update_pax_spinbox(rtype, px))
        self.rooms.append((frame, room_type, pax))

    def update_pax_spinbox(self, room_type_box, pax_box):
        room = room_type_box.get()
        if room and room in ROOM_RATES:
            max_pax = ROOM_RATES[room]["max"]
            pax_box.config(from_=1, to=max_pax)

    def create_extras_frame(self):
        section = tk.Frame(self.card, bg=CARD_COLOR)
        section.pack(fill='x', pady=(6,2), padx=12)
        self.conference_var = tk.BooleanVar()
        tk.Checkbutton(section, text="Conference Room ($120/day)", variable=self.conference_var,
                       bg=CARD_COLOR, fg=FG_COLOR, selectcolor=CARD_COLOR, font=("Arial", 11)).grid(row=0, column=0, sticky='w')
        tk.Label(section, text="Days:", bg=CARD_COLOR, fg=FG_COLOR).grid(row=0, column=1, sticky='w', padx=7)
        self.conference_days = tk.Entry(section, width=5, bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR)
        self.conference_days.grid(row=0, column=2, sticky='w')

    def create_breakfast_frame(self):
        section = tk.Frame(self.card, bg=CARD_COLOR)
        section.pack(fill='x', pady=(4,2), padx=12)
        self.breakfast_var = tk.BooleanVar()
        tk.Checkbutton(section, text="Breakfast ($10/person/day)", variable=self.breakfast_var,
                       bg=CARD_COLOR, fg=FG_COLOR, selectcolor=CARD_COLOR, font=("Arial", 11)).pack(side='left', padx=2)
        tk.Label(section, text="Guests:", bg=CARD_COLOR, fg=FG_COLOR).pack(side='left', padx=6)
        self.breakfast_guests = tk.Entry(section, width=5, bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR)
        self.breakfast_guests.pack(side='left', padx=2)
        tk.Label(section, text="Days:", bg=CARD_COLOR, fg=FG_COLOR).pack(side='left', padx=6)
        self.breakfast_days = tk.Entry(section, width=5, bg=FIELD_BG, fg=FIELD_FG, insertbackground=FG_COLOR)
        self.breakfast_days.pack(side='left', padx=2)

    def create_preview_frame(self):
        # Expand this frame to take available space
        section = tk.Frame(self.card, bg=CARD_COLOR)
        section.pack(fill='both', expand=True, pady=(10,6), padx=12)
        tk.Label(section, text="Invoice Summary", font=("Arial", 12, "bold"), bg=CARD_COLOR, fg=FG_COLOR).pack(anchor='w')
        self.preview_label = tk.Label(section, text="", justify="left", font=("Courier New", 11, "bold"),
                                      bg=CARD_COLOR, fg=FG_COLOR, anchor='nw')
        self.preview_label.pack(padx=2, pady=4, fill='both', expand=True)

    def calculate_nights(self):
        try:
            checkin_raw = self.checkin.get().replace("e.g.", "").strip()
            checkout_raw = self.checkout.get().replace("e.g.", "").strip()
            checkin_date = parse(checkin_raw)
            checkout_date = parse(checkout_raw)
            return (checkout_date - checkin_date).days
        except Exception:
            messagebox.showerror("Date Error", "Please enter valid dates. (Format: 18 June 2025)")
            return None

    def update_preview(self):
        nights = self.calculate_nights()
        if not nights:
            return

        room_details = []
        room_subtotal = 0
        preview_text = "Room\tGuests\tRate/night\tNights\tTotal\n"
        for _, room_type, pax in self.rooms:
            room = room_type.get()
            if not room:
                continue
            pax_count = int(pax.get())
            base_rate = ROOM_RATES[room]["rate"]
            max_pax = ROOM_RATES[room]["max"]
            extra = pax_count - 1 if pax_count > 1 else 0
            rate = base_rate + extra * EXTRA_GUEST_RATE
            total = rate * nights
            room_details.append((room, pax_count, rate, nights, total))
            room_subtotal += total
            preview_text += f"{room}\t{pax_count}\t${rate}\t{nights}\t${total}\n"

        breakfast_total = 0
        if self.breakfast_var.get():
            try:
                guests = int(self.breakfast_guests.get())
                days = int(self.breakfast_days.get())
                breakfast_total = guests * BREAKFAST_RATE * days
            except ValueError:
                pass

        conference_total = 0
        if self.conference_var.get():
            try:
                conf_days = float(self.conference_days.get())
                conference_total = conf_days * CONFERENCE_ROOM_RATE
            except ValueError:
                pass

        subtotal = room_subtotal + breakfast_total + conference_total
        grand_total = subtotal

        preview_text += f"\nSubtotal (Rooms): ${room_subtotal:.2f}"
        preview_text += f"\nBreakfast: ${breakfast_total:.2f}"
        preview_text += f"\nConference Room: ${conference_total:.2f}"
        preview_text += f"\n\nGrand Total: ${grand_total:.2f}\n"
        self.preview_label.config(text=preview_text)

    def generate_invoice(self):
        self.update_preview()
        nights = self.calculate_nights()
        if not nights:
            return

        guest = self.guest_name.get().strip()
        payment_by = self.payment_method.get().strip()
        if not guest:
            messagebox.showwarning("Input Error", "Please enter guest name.")
            return

        # --- Room details check ---
        room_details = []
        room_subtotal = 0
        for _, room_type, pax in self.rooms:
            room = room_type.get()
            if not room:
                continue
            pax_count = int(pax.get())
            base_rate = ROOM_RATES[room]["rate"]
            max_pax = ROOM_RATES[room]["max"]
            extra = pax_count - 1 if pax_count > 1 else 0
            rate = base_rate + extra * EXTRA_GUEST_RATE
            total = rate * nights
            room_details.append((room, pax_count, rate, nights, total))
            room_subtotal += total

        if not room_details:
            messagebox.showerror("Error", "No room selected. Please select at least one room.")
            return

        breakfast_total = 0
        if self.breakfast_var.get():
            try:
                guests = int(self.breakfast_guests.get())
                days = int(self.breakfast_days.get())
                breakfast_total = guests * BREAKFAST_RATE * days
            except ValueError:
                pass

        conference_total = 0
        if self.conference_var.get():
            try:
                conf_days = float(self.conference_days.get())
                conference_total = conf_days * CONFERENCE_ROOM_RATE
            except ValueError:
                pass

        subtotal = room_subtotal + breakfast_total + conference_total
        grand_total = subtotal

        # --- Generate PDF ---
        try:
            pdf = FPDF()
            pdf.add_page()
            try:
                pdf.image("logo2.png", x=75, y=6, w=60)
            except:
                pass
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.ln(28)
            pdf.set_fill_color(35, 35, 35)
            pdf.set_text_color(255, 224, 102)

            pdf.set_font("Arial", 'B', 24)
            pdf.cell(0, 14, txt="INVOICE", ln=True, align='L', fill=False)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, txt=f"Date: {datetime.now().strftime('%d %B, %Y')}", ln=True, align='R')
            pdf.cell(0, 8, txt="Invoice no: [auto-generated]", ln=True, align='R')
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(0, 12, txt="Guest Name:   " + guest, ln=True, align='L')
            pdf.cell(0, 7, txt="Payment by: " + payment_by, ln=True, align='L')
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, txt="Room Charges", ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.cell(70, 7, "Room", 1)
            pdf.cell(20, 7, "Pax", 1)
            pdf.cell(28, 7, "Rate/Night", 1)
            pdf.cell(20, 7, "Nights", 1)
            pdf.cell(25, 7, "Total", 1)
            pdf.ln()

            for room, pax, rate, nts, total in room_details:
                pdf.cell(70, 7, room, 1)
                pdf.cell(20, 7, str(pax), 1, align='C')
                pdf.cell(28, 7, f"${rate}", 1, align='R')
                pdf.cell(20, 7, str(nts), 1, align='C')
                pdf.cell(25, 7, f"${total}", 1, align='R')
                pdf.ln()

            pdf.ln(1)
            pdf.set_font("Arial", '', 11)
            pdf.cell(143, 8, "Subtotal (Rooms):", 0, 0, 'R')
            pdf.cell(28, 8, f"${room_subtotal:.2f}", 0, 1, 'R')
            if breakfast_total > 0:
                pdf.cell(143, 8, "Breakfast:", 0, 0, 'R')
                pdf.cell(28, 8, f"${breakfast_total:.2f}", 0, 1, 'R')
            if conference_total > 0:
                pdf.cell(143, 8, "Conference Room:", 0, 0, 'R')
                pdf.cell(28, 8, f"${conference_total:.2f}", 0, 1, 'R')
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(143, 10, "Grand Total:", 0, 0, 'R')
            pdf.cell(28, 10, f"${grand_total:.2f}", 0, 1, 'R')
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(255, 211, 30)
            pdf.cell(0, 9, "* Each extra guest after the first: $22", ln=True)
            pdf.set_text_color(255, 224, 102)
            pdf.set_font("Arial", '', 9)
            pdf.multi_cell(0, 7, "Thank you for choosing Yellow Haven Lodge!")

            filename_base = f"Invoice_{guest.replace(' ', '_')}"
            pdf_filename = f"{filename_base}.pdf"
            xlsx_filename = f"{filename_base}.xlsx"

            pdf.output(pdf_filename)
            df = pd.DataFrame(room_details, columns=["Room", "Pax", "Rate/Night", "Nights", "Total"])
            df.to_excel(xlsx_filename, index=False)

            messagebox.showinfo("Success", f"Invoice saved as:\n{pdf_filename}\n{xlsx_filename}")
            try:
                os.startfile(pdf_filename)
                os.startfile(xlsx_filename)
            except Exception as ex:
                messagebox.showinfo("Info", f"Files saved but could not open automatically. Error: {ex}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not generate invoice files: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceGeneratorApp(root)
    root.mainloop()
