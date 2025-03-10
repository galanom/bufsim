#!/usr/bin/env python3
import tkinter as tk

class Checkerboard:
    def __init__(self, z=8, x=16, cell_size=24, delay=100,
                 manual=False, t_shift=5, read_size=10, batch=False, max_steps=1000):
        self.batch = batch
        self.z = z
        self.x = x
        self.cell_size = cell_size
        self.delay = delay
        self.manual = manual
        self.t_shift = t_shift       # delay (in steps) before reader starts
        self.read_size = read_size
        self.depth = 10

        self.empty_color = "white"
        self.writer_last_marked_color = "navy blue"
        self.writer_filled_color = "powder blue"
        self.reader_head_color = "black"
        self.reader_trail_color = "dark gray"
        self.left_shade_factor = 0.8
        self.top_shade_factor = 1.1

        # Compute a proportional font size (40% of cell_size) so that a three-digit number fits.
        self.font_size = max(8, int(self.cell_size * 0.4))

        # Dictionary to track for each column (x) the number of non-empty cells.
        self.column_nonempty_count = {col: 0 for col in range(self.x)}

        # Board data: mapping (row, col) -> {"id": canvas rectangle (or None in batch),
        # "state": state, "step": step, "text_id": text item id}
        self.cells = {}
        self.side_polygons = {}  # Used only in visual mode
        self.last_writer_marked = None

        if not self.batch:
            self.root = tk.Tk()
            self.root.title("Reorder Buffer")
            self.canvas = tk.Canvas(self.root,
                                    width=self.x * self.cell_size + self.depth + 40,
                                    height=self.z * self.cell_size + self.depth + 40)
            self.canvas.pack()
            self.draw_board()
            self.draw_axes()
            self.status_label = tk.Label(self.root, text="", font=("Courier", 14))
            self.status_label.pack()
            self.error_label = tk.Label(self.root, text="", font=("Courier", 12), fg="red")
            self.error_label.pack()
        else:
            self.root = None
            for row in range(self.z):
                for col in range(self.x):
                    self.cells[(row, col)] = {"id": None, "state": "empty", "step": None, "text_id": None}

        self.writer_pos = (0, 0)

        self.reader_current_pos = (self.read_size, 0)
        self.reader_cells = []
        self.time_step = 0
        self.halted = False

        if not self.batch:
            self.update_status_label()

        if self.manual:
            if not self.batch:
                self.root.bind("<KeyPress>", self.execute_writes)
        else:
            if not self.batch:
                self.animate()
            else:
                for _ in range(max_steps):
                    if self.halted:
                        break
                    self.execute_writes()
                print(f"Simulation done.")

        if not self.batch:
            self.root.mainloop()

    def draw_board(self):
        for row in range(self.z):
            for col in range(self.x):
                x1 = col * self.cell_size + self.depth + 20
                y1 = (self.z - row - 1) * self.cell_size + self.depth + 20
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill=self.empty_color,
                                                    outline="gray", dash=(2, 2))
                self.cells[(row, col)] = {"id": rect, "state": "empty", "step": None, "text_id": None}

                if col == 0:
                    poly_left = self.canvas.create_polygon(
                        x1 - self.depth, y1 - self.depth,
                        x1, y1,
                        x1, y2,
                        x1 - self.depth, y2 - self.depth,
                        fill=self.adjust_color(self.empty_color, self.left_shade_factor),
                        outline="gray")
                    self.side_polygons[(row, col, 'left')] = poly_left

                if row == self.z - 1:
                    poly_top = self.canvas.create_polygon(
                        x1 - self.depth, y1 - self.depth,
                        x2 - self.depth, y1 - self.depth,
                        x2, y1,
                        x1, y1,
                        fill=self.adjust_color(self.empty_color, self.top_shade_factor),
                        outline="gray")
                    self.side_polygons[(row, col, 'top')] = poly_top

    def draw_axes(self):
        for col in range(self.x):
            self.canvas.create_text(
                col * self.cell_size + self.depth + self.cell_size//2 + 20,
                self.z * self.cell_size + self.depth + 30,
                text=str(col), font=("Arial", 10))
        for row in range(self.z):
            self.canvas.create_text(
                self.depth,
                (self.z - row - 1) * self.cell_size + self.depth + self.cell_size//2 + 20,
                text=str(row), font=("Arial", 10))

    def adjust_color(self, base_color, factor):
        if self.batch:
            return base_color
        rgb = self.canvas.winfo_rgb(base_color)
        adjusted = tuple(min(65535, int(c * factor)) for c in rgb)
        return "#%02x%02x%02x" % (adjusted[0] >> 8, adjusted[1] >> 8, adjusted[2] >> 8)

    def set_cell(self, pos, new_color, new_state, step=None):
        cell = self.cells[pos]
        row, col = pos
        old_state = cell["state"]

        #if new_state == "empty":
        #    cell["step"] = None
        #    if old_state != "empty" and cell.get("text_id") is not None:
        #        self.canvas.delete(cell["text_id"])
        #        cell["text_id"] = None
        #else:
        if step is None:
            cell["step"] = self.cells[pos]["step"]
        else:
            cell["step"] = step

        # Update the column count.
        if old_state == "empty" and new_state != "empty":
            self.column_nonempty_count[col] += 1
        elif old_state != "empty" and new_state == "empty":
            self.column_nonempty_count[col] = max(0, self.column_nonempty_count[col] - 1)

        cell["state"] = new_state

        if not self.batch:
            self.canvas.itemconfig(cell["id"], fill=new_color)
            if (row, col, 'left') in self.side_polygons:
                left_color = self.adjust_color(new_color, self.left_shade_factor)
                self.canvas.itemconfig(self.side_polygons[(row, col, 'left')], fill=left_color)
            if (row, col, 'top') in self.side_polygons:
                top_color = self.adjust_color(new_color, self.top_shade_factor)
                self.canvas.itemconfig(self.side_polygons[(row, col, 'top')], fill=top_color)
            if new_state != "empty" and cell.get("step") is not None:
                x1 = col * self.cell_size + self.depth + 20
                y1 = (self.z - row - 1) * self.cell_size + self.depth + 20
                x_center = x1 + self.cell_size / 2
                y_center = y1 + self.cell_size / 2
                if cell.get("text_id") is None:
                    text_id = self.canvas.create_text(x_center, y_center, text=str(cell["step"]),
                                                      font=("Arial", self.font_size), fill="white")
                    cell["text_id"] = text_id
                else:
                    self.canvas.itemconfig(cell["text_id"], text=str(cell["step"]),
                                           font=("Arial", self.font_size), fill="white")

    def advance_writer_marker(self):
        pos = self.writer_pos
        if self.cells[pos]["state"] == "written":
            if self.cells[pos]["step"] >= self.t_shift:
                self.halt_simulation(f"Rule check failed [{self.time_step}]: writer advances to cell at {pos} that is [{self.cells[pos]['state']}]")
                return
            else:
                print(f"warning [{self.time_step}]: overwriting apparently useless cell at {pos} with step {self.cells[pos]['step']}")
        if self.cells[pos]["state"] == "reading":
            if self.reader_cells[0] == self.writer_pos:
                print(f"warning [{self.time_step}]: writing over the cell it is being currently read")
            else:
                self.halt_simulation(f"Rule check failed [{self.time_step}]: writer advances to cell at {pos} that being read (and is not at the tail)")
        if self.last_writer_marked is not None:
            self.set_cell(self.last_writer_marked, self.writer_filled_color, "written")
        self.set_cell(pos, self.writer_last_marked_color, "writing", step=self.time_step)
        r, c = pos
        if r < self.z - 1:
            self.writer_pos = (r + 1, c)
        else:
            self.writer_pos = (0, (c + 1) % self.x)
        self.last_writer_marked = pos

    def advance_reader_marker(self):
        pos = self.reader_current_pos
        if self.cells[pos]["state"] != "written":
            if self.cells[pos]["state"] == "empty":
                self.halt_simulation(
                    f"Rule check failed [{self.time_step}]: reader advances to cell at {pos} that is empty"
                )
                return
            else:
                print(f"warning [{self.time_step}]: reading a cell that is being written at {pos}")
        # Update previous reader head (if exists) to the trail color.
        if self.reader_cells:
            prev_head = self.reader_cells[-1]
            self.set_cell(prev_head, self.reader_trail_color, "reading")
        self.set_cell(pos, self.reader_head_color, "reading")
        self.reader_cells.append(pos)
        if len(self.reader_cells) > self.read_size:
            old = self.reader_cells.pop(0)
            self.set_cell(old, self.empty_color, "empty")

        r, c = pos
        # are we at the bottom?
        if r == 0:
            next_pos = (self.z - 1, (c + 2 - self.z) % self.x)
        else:
            next_pos = (r - 1, (c + 1) % self.x)

        #if r > 0:
        #    # Normal diagonal move, but if c+1 reaches self.x, wrap it modulo self.x.
        #    next_pos = (r - 1, (c + 1) % self.x)
        #else:
        #    # At the top row, we can’t go diagonally upward.
        #    # Continue with the original anti-diagonal logic.
        #    i = r + c
        #    next_i = i + 1
        #    if next_i > (self.z - 1) + (self.x - 1):
        #        next_pos = (0, 0)
        #    elif next_i < self.z:
        #        next_pos = (next_i, 0)
        #    else:
        #        next_pos = (self.z - 1, next_i - (self.z - 1))
        self.reader_current_pos = next_pos


    def halt_simulation(self, error_message):
        if not self.batch:
            self.error_label.config(text=error_message)
        else:
            print("Illegal state encountered:", error_message)
        self.halted = True

    def execute_writes(self, event=None):
        if self.halted:
            return
        if self.time_step >= self.t_shift:
            self.advance_reader_marker()
        self.advance_writer_marker()
        self.time_step += 1
        if not self.batch:
            self.update_status_label()

    def update_status_label(self):
        if not self.batch:
            if self.last_writer_marked is not None:
                writer_str = f"({self.last_writer_marked[0]:2d},{self.last_writer_marked[1]:2d})"
            else:
                writer_str = "  N/A  "
            if self.reader_cells:
                last_reader = self.reader_cells[-1]
                reader_str = f"({last_reader[0]:2d},{last_reader[1]:2d})"
            else:
                reader_str = "  N/A  "
            self.status_label.config(
                text=f"step:{self.time_step:3d} | writer: {writer_str} | reader: {reader_str}")

    def animate(self):
        if not self.halted:
            self.execute_writes()
            self.root.after(self.delay, self.animate)

if __name__ == "__main__":
    Checkerboard()

