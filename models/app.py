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
        self.show_points = False
        self.show_bounds = False
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
        self.canvas = tk.Canvas(self.root, bg="white", width=500, height=500) # Adjust the size as needed
        self.canvas.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Keybindings
        self.root.bind("<Right>", lambda _: self.next_character())
        self.root.bind("<Left>", lambda _: self.previous_character())
        self.root.bind("<Down>", lambda _: self.next_font())
        self.root.bind("<Up>", lambda _: self.previous_font())
        self.root.bind("p", lambda _: self.toggle_points())
        self.root.bind("b", lambda _: self.toggle_bounds())

        # Status Bar (for showing current character/font info)
        self.status_bar = ttk.Label(self.root, text="", anchor="w")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5)

        # Set up keyboard commands label
        self.keyboard_commands = ttk.Label(self.root, text="\nKeyboard Commands:\n"
                                                    "right: next character\n"
                                                    "left:  previous character\n"
                                                    "down:  next font\n"
                                                    "up: show/hide points and width\n"
                                                    "p: show/hide points\n"
                                                    "b: show/hide bounds\n")
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
            a1 = char_data.get('a1')
            a2 = char_data.get('a2')
            a3 = char_data.get('a3')
            a4 = char_data.get('a4')
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Draw a boundary rectangle according to the normalized coordinate space
            self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, outline="gray")

            self.canvas.create_line(-1,1,1,1)

            out_of_bounds = False

            # Draw each coordinate as a cross using an extended canvas area (-0.2 to 1.2)
            for coord in char_data.get('coordinates', []):
                # Use the dot's float value directly (assumed between -0.2 and 1.2)
                # This assume is wrong but I don't know how to fix it
                x_val = coord['x']
                y_val = coord['y']
                prev_x = 0.0
                prev_y = 0.0

                if (y_val < a2 or y_val > a4) or (x_val < a1 or x_val > a3):
                    print(f"Out of bounds: {x_val}, {y_val}")
                    out_of_bounds = True

                if char_data['coordinates'].index(coord) > 0:
                    # Get previus point
                    # This is a bit weird, but it works for now
                    previus_coordinate = char_data['coordinates'][char_data['coordinates'].index(coord) - 1]
                    prev_x = ((previus_coordinate['x'] + 0.2) / 1.4) * canvas_width
                    prev_y = ((previus_coordinate['y'] + 1.2) / 1.4) * canvas_height
                
                # Map data space [-0.2, 1.2] to canvas pixels
                pixel_x = ((x_val + 0.2) / 1.4) * canvas_width
                pixel_y = (((y_val + 1.2) / 1.4) * canvas_height)

                # Determine color based on line_type.
                if coord['line_type'] == 3:
                    color = "red"
                elif coord['line_type'] == 1:
                    color = "blue"
                else:
                    color = "black"

                cs = 2  # cross size in pixels
                if self.show_points:
                    self.canvas.create_line(pixel_x - cs, pixel_y - cs, pixel_x + cs, pixel_y + cs, fill=color)
                    self.canvas.create_line(pixel_x - cs, pixel_y + cs, pixel_x + cs, pixel_y - cs, fill=color)
                # For debugging, show the index of the coordinate in the list
                # self.canvas.create_text(pixel_x + 10, pixel_y + 10, text=f"{char_data['coordinates'].index(coord)}", fill=color)

                if coord['line_type'] == 2:
                    # Draw a line from the previous point to this point
                    self.canvas.create_line(prev_x, prev_y, pixel_x, pixel_y, fill=color)

                # If this coordinate is curved, draw its control cross.
                if coord['line_type'] == 3:
                    curved_x = coord.get('curved_x')
                    curved_y = coord.get('curved_y')
                    if curved_x != 0.0 or curved_y != 0.0:
                        pixel_cx = ((curved_x + 0.2) / 1.4) * canvas_width
                        pixel_cy = ((curved_y + 1.2) / 1.4) * canvas_height

                        # Cross
                        if self.show_points:
                            self.canvas.create_line(pixel_cx - cs, pixel_cy - cs, pixel_cx + cs, pixel_cy + cs, fill=color)
                            self.canvas.create_line(pixel_cx - cs, pixel_cy + cs, pixel_cx + cs, pixel_cy - cs, fill=color)

                        # Curved Line
                        self.canvas.create_line(prev_x, prev_y, pixel_cx, pixel_cy, pixel_x, pixel_y, smooth=True, splinesteps=36, fill=color)

            # Draw reference lines for x=0 (vertical) and y=0 (horizontal)
            # For x=0:
            x0_pixel = ((0 + 0.2) / 1.4) * canvas_width
            self.canvas.create_line(x0_pixel, 0, x0_pixel, canvas_height, fill="green", dash=(4,2))
            
            # For y=0:
            y0_pixel = canvas_height - ((0 + 0.2) / 1.4) * canvas_height
            self.canvas.create_line(0, y0_pixel, canvas_width, y0_pixel, fill="green", dash=(4,2))

            # Draw the character's bounding box
            a_2 = ((a2 + 1.2) / 1.4) * canvas_width # Y + AXIS
            a_4 = ((a4 + 1.2) / 1.4) * canvas_height # Y - AXIS

            a_1 = ((a1 + 0.2) / 1.4) * canvas_width # X + AXIS
            a_3 = ((a3 + 0.2) / 1.4) * canvas_height # X - AXIS

            if self.show_bounds:
                # Y's
                self.canvas.create_line(0, a_4, canvas_width, a_4, fill="purple")
                self.canvas.create_line(0, a_2, canvas_width, a_2, fill="purple")

                # X's
                self.canvas.create_line(a_1, 0, a_1, canvas_height, fill="purple")
                self.canvas.create_line(a_3, 0, a_3, canvas_height, fill="purple")
            
            if out_of_bounds:
                messagebox.showerror("Invalid Bounds", f"Out of bounds: {x_val}, {y_val}")

            # I hate how long and ugly this is
            self.status_bar.config(text=f"Font: {self.font_combo.get()}\nChar: {char_data['keycodeValue']} ({convert_bytes_to_hex(char_data['keycodeValue'].encode('utf-16le'))})\nIndex: {self.current_char_index} / {len(font['charList'])-1}\nNumber of Coordinates: {char_data['numChunks']}")

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

    def toggle_points(self):
        self.show_points = not self.show_points
        self.draw_character()
    
    def toggle_bounds(self):
        self.show_bounds = not self.show_bounds
        self.draw_character()

def runApp(filepath):
    root = tk.Tk()
    FontViewerApp(root, filepath)
    root.mainloop()