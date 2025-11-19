import tkinter as tk
from tkinter import messagebox
import ctypes
import platform
from importlib.resources import files
from io import BytesIO

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]


class AgentEventPopup:
    def __init__(self, on_close_callback=None):
        self.on_close_callback = on_close_callback
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        width, height = 250, 60
        radius = 15
        bg_color = "#ffffff"     # Light theme
        text_color = "#222222"   # Normal dark text
        
        
        from PIL import Image, ImageTk, ImageDraw

        # -------------------------
        # Create rounded background image
        # -------------------------
        rounded_bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

        bg = Image.new("RGBA", (width, height), bg_color)
        rounded_bg = Image.composite(bg, rounded_bg, mask)

        self.rounded_bg_tk = ImageTk.PhotoImage(rounded_bg)

        canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0
        )
        canvas.pack()

        canvas.create_image(0, 0, image=self.rounded_bg_tk, anchor="nw")

        # -------------------------
        # Content Frame (on top)
        # -------------------------
        container = tk.Frame(self.root, bg=bg_color)
        container.place(x=0, y=0, width=width, height=height)

        # Load logo
        logo = (files("user_agent_sdk") / "assets" / "logo.png").read_bytes()
        img = Image.open(BytesIO(logo)).resize((30, 30), Image.Resampling.LANCZOS)
        self.logo = ImageTk.PhotoImage(img)

        logo_label = tk.Label(container, image=self.logo, bg=bg_color)
        logo_label.pack(side="left", padx=10)

        self.label = tk.Label(
            container,
            text="",
            fg=text_color,
            bg=bg_color,
            font=("Segoe UI", 10, "bold")
        )
        self.label.pack(side="left", expand=True, anchor="w")

        close_btn = tk.Label(
            container,
            text="✕",
            fg=text_color,
            bg=bg_color,
            font=("Segoe UI", 14),
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=10)
        close_btn.bind("<Button-1>", lambda e: self.confirm_close())

        # -------------------------
        # Make draggable
        # -------------------------
        for widget in (container, logo_label, self.label):
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        # Bottom-right positioning
        if platform.system() == 'Windows':
            rect = RECT()
            ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
            work_width = rect.right
            work_height = rect.bottom
        else:
            work_width = self.root.winfo_screenwidth()
            work_height = self.root.winfo_screenheight()
        x = work_width - width
        y = work_height - height
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # self.root.mainloop()  # Removed to allow setting name before showing

    def show(self):
        self.root.mainloop()

    def confirm_close(self):
        if messagebox.askyesno("Confirm Close", "Closing this popup will stop the computer use agent. Are you sure?"):
            self.close()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        self.root.geometry(f"+{self.root.winfo_x()+dx}+{self.root.winfo_y()+dy}")

    def close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.root.destroy()

    def set_event_name(self, new_name: str):
        self.label.config(text=new_name)

