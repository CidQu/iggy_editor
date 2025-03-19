import tkinter as tk
from tkinter import ttk
from helpers.byteToHex import convert_bytes_to_hex
from models.readChars import parse_file
from tkinter import messagebox

class FontViewerApp:
    def __init__(self, root, file_path):
        self.root = root
        self.root.title("Font Viewer")
        #self.root.geometry("600x400")

        self.file_path = file_path
        self.parsed_data = parse_file(self.file_path)
        self.current_font_index = 0
        self.current_char_index = 0
        self.fonts = [offset_data['font'] for offset_data in self.parsed_data['offsets'] if 'font' in offset_data]


        self.setup_ui()
        self.load_font_data()


    def setup_ui(self):
        # Font Selection
        self.font_label = ttk.Label(self.root, text="Font:")
        self.font_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.font_combo = ttk.Combobox(self.root, state="readonly")
        self.font_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.font_combo["values"] = [font['fontName'] for font in self.fonts]
        self.font_combo.bind("<<ComboboxSelected>>", self.load_font_data)


        # Character Selection
        self.char_label = ttk.Label(self.root, text="Char:")
        self.char_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.char_frame = ttk.Frame(self.root)
        self.char_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.char_decrement = ttk.Button(self.char_frame, text="-", command=self.previous_character)
        self.char_decrement.grid(row=0, column=0)

        self.char_var = tk.StringVar(value="0")
        self.char_entry = ttk.Entry(self.char_frame, textvariable=self.char_var, width=5, justify="center")
        self.char_entry.grid(row=0, column=1, padx=5)
        self.char_entry.bind("<FocusOut>", lambda event: self.update_character(int(self.char_var.get())))
        self.char_entry.bind("<Return>", lambda event: self.update_character(int(self.char_var.get())))

        self.char_increment = ttk.Button(self.char_frame, text="+", command=self.next_character)
        self.char_increment.grid(row=0, column=2)


        # Canvas for drawing
        self.canvas = tk.Canvas(self.root, bg="white", width=400, height=300) # Adjust the size as needed
        self.canvas.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Keybindings
        self.root.bind("<Right>", lambda _: self.next_character())
        self.root.bind("<Left>", lambda _: self.previous_character())
        self.root.bind("<Down>", lambda _: self.next_font())
        self.root.bind("<Up>", lambda _: self.previous_font())

        # Status Bar (for showing current character/font info)
        self.status_bar = ttk.Label(self.root, text="", anchor="w")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5)

        # Set up keyboard commands label
        self.keyboard_commands = ttk.Label(self.root, text="\nKeyboard Commands:\n"
                                                    "right: next character\n"
                                                    "left:  previous character\n"
                                                    "down:  next font\n"
                                                    "up: show/hide points and width")
        self.keyboard_commands.grid(row=5, column=0, columnspan=1)

    def load_font_data(self, _event=None):
        if not self.fonts:
            return

        self.current_font_index = self.font_combo.current()
        if self.current_font_index == -1:  # Handle case where no font is selected yet
            self.current_font_index = 0
            self.font_combo.current(0)

        font = self.fonts[self.current_font_index]
        if font['numCharacters'] > 0:
          self.current_char_index = 0
          self.draw_character()

    def draw_character(self, _event=None):
        self.current_char_index = int(self.char_var.get())
        if self.current_char_index == -1:
            return
        
        self.canvas.delete("all")
        font = self.fonts[self.current_font_index]
        char_data = font["charList"][self.current_char_index]
        has_points = char_data['hasPoints']

        if has_points:
            ############################
            # WIP
            ############################
            # WIP
            ############################

            self.status_bar.config(text=f"Font: {self.font_combo.get()}\nChar: {char_data['keycodeValue']} ({convert_bytes_to_hex(char_data['keycodeValue'].encode('utf-16le'))})\nIndex: {self.current_char_index} / {len(font['charList'])-1}\nNumber of Coordinates: {char_data['numChunks']}")
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, text="Not implemented", fill="black")
            # a1, a2, a3, a4 = char_data['a1'], char_data['a2'], char_data['a3'], char_data['a4']
            
            # scale_factor = 150

            # x_min = min(a1, a3)
            # y_min = min(a2, a4)
            # x_max = max(a1, a3)
            # y_max = max(a2, a4)

            # width = x_max - x_min
            # height = y_max - y_min
            # x_min_scaled = (x_min) * scale_factor + 50 # offset for visiblity
            # y_min_scaled = (y_min) * scale_factor + 50
            # width_scaled = width * scale_factor
            # height_scaled = height * scale_factor

            # self.canvas.create_rectangle(x_min_scaled, y_min_scaled, x_min_scaled+width_scaled, y_min_scaled+height_scaled, outline="black")
            # self.status_bar.config(text=f"Font: {self.font_combo.get()}, Char: {self.current_char_index} (Index: {self.current_char_index} / {len(font['charList'])-1})")
        else:
            self.status_bar.config(text=f"Font: {self.font_combo.get()}\nChar: {char_data['keycodeValue']} ({convert_bytes_to_hex(char_data['keycodeValue'].encode('utf-16le'))})\nIndex: {self.current_char_index} / {len(font['charList'])-1}\nNo Points")
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, text="No Points", fill="black")
    def next_character(self):
        if self.current_char_index < len(self.fonts[self.current_font_index]['charList']) - 1:
            self.current_char_index += 1
            self.char_var.set(self.current_char_index)
            self.draw_character()
        elif self.current_char_index == len(self.fonts[self.current_font_index]['charList']) - 1:
            self.current_char_index = 0
            self.char_var.set(self.current_char_index)
            self.draw_character()
        else:
            messagebox.showerror("Invalid Index", f"Unknown Error")
    
    def previous_character(self):
        if self.current_char_index > 0:
            self.current_char_index -= 1
            self.char_var.set(self.current_char_index)
            self.draw_character()
        elif self.current_char_index == 0:
            self.current_char_index = len(self.fonts[self.current_font_index]['charList']) - 1
            self.char_var.set(self.current_char_index)
            self.draw_character()
        else:
            messagebox.showerror("Invalid Index", f"Unknown Error")

    def update_character(self, newIndex):
        if self.current_char_index >= 0 and newIndex >= 0 and newIndex < len(self.fonts[self.current_font_index]['charList']):
            self.current_char_index = newIndex
            self.char_var.set(self.current_char_index)
            self.draw_character()
        else:
            messagebox.showerror("Invalid Index", f"Number you entered must be between 0 and {len(self.fonts[self.current_font_index]['charList']) - 1}")

    def next_font(self):
        if self.current_font_index < len(self.fonts) - 1:
            self.current_font_index += 1
            self.font_combo.current(self.current_font_index)
            self.load_font_data()  # Load characters for the new font
            self.draw_character() # Draw the currently selected char

    def previous_font(self):
        if self.current_font_index > 0:
            self.current_font_index -= 1
            self.font_combo.current(self.current_font_index)
            self.load_font_data()
            self.draw_character()

def runApp(filepath):
    root = tk.Tk()
    FontViewerApp(root, filepath)
    root.mainloop()