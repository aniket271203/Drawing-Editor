import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
import xml.etree.ElementTree as ET
import math
from PIL import ImageGrab
from PIL import Image, ImageDraw
from PIL import ImageTk
import sys

# Define constants
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 900
LINE = "line"
RECTANGLE = "rectangle"
GROUP = "group"
NONE = "none"
POLYGON = "polygon"


class DrawingEditor:
    def __init__(self, root):
       
        self.root = root
        self.root.title("Drawing Editor")

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH,
                                height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack()

        self.objects = []
        self.groups = []

        self.selected_object = NONE
        self.selected_group = None
        self.selection_indicator = None
        self.selection_indicator_group = []
        self.start_x = None
        self.start_y = None
        self.temp_line = None
        self.temp_rect = None
        self.click_count = 0
        self.drawing_modified = False
        self.group_mode = False
        self.drag_data = {"x": 0, "y": 0}
        self.selected_tool = None
        self.selected_objects_grouped = []

        self.create_menu()
        self.create_toolbox()

        self.canvas.bind("<Button-1>", self.handle_click)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        if len(sys.argv) > 1:
            self.open_drawing(sys.argv[1])

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(label="Save as JPEG",
                              command=self.save_drawing_as_JPEG)
        file_menu.add_command(label="Save as TXT",
                              command=self.save_drawing_as_TXT)
        file_menu.add_command(label="Export as XML",
                              command=self.save_drawing_as_XML)
        file_menu.add_command(label="Import from JPEG",
                              command=self.open_jpeg_drawing)

        file_menu.add_command(label="Open", command=self.open_drawing)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Delete", command=self.delete_object)
        edit_menu.add_command(
            label="Rotate", command=self.rotate_object_dialog)
        edit_menu.add_command(label="Copy", command=self.copy_object)
        edit_menu.add_command(label="Move", command=self.move_object)
        edit_menu.add_command(label="resize", command=self.resize_dialog)
        # edit_menu.add_command(label="increase size", command=self.increase_size)
        edit_menu.add_command(label="Edit", command=self.edit_object)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        group_menu = tk.Menu(menubar, tearoff=0)
        group_menu.add_command(label="Select for Grouping",
                               command=self.enter_group_mode)
        group_menu.add_command(label="Group", command=self.group_objects)
        group_menu.add_command(label="Ungroup", command=self.ungroup_objects)
        group_menu.add_command(label="Ungroup_All", command=self.ungroup_all)
        menubar.add_cascade(label="Group", menu=group_menu)

        self.root.config(menu=menubar)

    def enter_group_mode(self):
        if self.selection_indicator:
            self.canvas.delete(self.selection_indicator)
        self.group_mode = True
        self.selection_indicator = None
        self.selected_objects_grouped = []

    def resize_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Resize Object")

        tk.Label(dialog, text="Width:").pack()
        width_entry = tk.Entry(dialog)
        width_entry.pack()

        tk.Label(dialog, text="Height:").pack()
        height_entry = tk.Entry(dialog)
        height_entry.pack()

        resize_button = tk.Button(
            dialog, text="Resize", command=lambda: self.resize_object(width_entry, height_entry))
        resize_button.pack()

    def resize_object(self, width_entry, height_entry):
        width_str = width_entry.get()
        height_str = height_entry.get()
        try:
            width = float(width_str)
            height = float(height_str)
            id = self.selected_object
            if self.selected_object:
                object_type = self.canvas.type(self.selected_object)
                if object_type == "rectangle" or object_type == "line":
                    coords = self.canvas.coords(self.selected_object)

                    new_coords = [coords[0], coords[1],
                                  coords[0] + width, coords[1] + height]

                    self.canvas.coords(id, *new_coords)
                    self.canvas.coords(self.selection_indicator, *new_coords)

                elif object_type == "polygon":  # Check if the selected object is a polygon
                    # Get the coordinates of the polygon
                    coords = self.canvas.coords(self.selected_object)
                    num_points = len(coords) // 2
                    if num_points >= 3:
                        center_x = sum(coords[i] for i in range(
                            0, len(coords), 2)) / num_points
                        center_y = sum(coords[i] for i in range(
                            1, len(coords), 2)) / num_points

                        scale_x = width / self.canvas.winfo_width()
                        scale_y = height / self.canvas.winfo_height()

                        new_coords = []
                        for i in range(0, len(coords), 2):
                            new_x = center_x + (coords[i] - center_x) * scale_x
                            new_y = center_y + \
                                (coords[i + 1] - center_y) * scale_y
                            new_coords.extend([new_x, new_y])
                        # Resize the polygon
                        self.canvas.coords(id, *new_coords)
                        self.canvas.coords(
                            self.selection_indicator, *new_coords)
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Please enter valid width jk = coords[0]and height.")

    def group_objects(self):
        if self.selected_objects_grouped and isinstance(self.selected_objects_grouped, list):
            # Extract the bounding boxes of all selected objects
            for obj1 in self.selected_objects_grouped:
                for obj2 in self.objects:
                    if obj1 == obj2:
                        self.objects.remove(obj2)
            bounding_boxes = [self.canvas.bbox(
                obj_id) for obj_id in self.selected_objects_grouped]
            # Extract the minimum and maximum coordinates from all bounding boxes
            min_x = min(box[0] for box in bounding_boxes)
            min_y = min(box[1] for box in bounding_boxes)
            max_x = max(box[2] for box in bounding_boxes)
            max_y = max(box[3] for box in bounding_boxes)

            border_width = 2
            min_x -= border_width
            min_y -= border_width
            max_x += border_width
            max_y += border_width

            # Create a rectangle that encompasses all the objects in the group
            group_id = self.canvas.create_rectangle(
                min_x, min_y, max_x, max_y, outline="green", dash=(4, 4))

            for obj in self.selection_indicator_group:
                # print(obj)
                self.canvas.delete(obj)
            if self.selection_indicator:
                self.canvas.delete(self.selection_indicator)

            self.groups.append(
                {"id": group_id, "objects": self.selected_objects_grouped})
            self.selected_objects_grouped = []
            self.drawing_modified = True
            self.group_mode = False

    def ungroup_all(self):
        for grps in self.groups:
            for objs in grps['objects']:
                self.objects.append(objs)
            self.canvas.delete(grps['id'])
        self.groups = []

    def ungroup_objects(self):
        # self.handle_click()
        if self.groups:
            for group in self.groups:
                # print(group['id'],self.selected_group)
                if group['id'] == self.selected_group:
                    # print("yes")
                    for obj in group['objects']:
                        # print(obj)
                        self.objects.append(obj)
                        if self.selection_indicator:
                            self.canvas.delete(self.selection_indicator)
                        self.canvas.itemconfig(obj, outline="black")
                    self.canvas.delete(group['id'])
                    self.groups.remove(group)
                    self.selected_objects_grouped = []
                    self.drawing_modified = True
                    break

    def deselect_object(self):
        if self.selected_objects_grouped:
            if isinstance(self.selected_objects_grouped, list):
                for obj in self.selected_objects_grouped:
                    self.canvas.itemconfig(obj, outline="black")
            else:
                self.canvas.itemconfig(self.selected_object, outline="black")
            if self.selection_indicator:
                self.canvas.delete(self.selection_indicator)
                self.selection_indicator = None
            self.selected_objects_grouped = []
            if self.group_mode:
                self.group_mode = False

    def create_toolbox(self):
        self.toolbox = tk.Frame(self.root)
        self.toolbox.pack(side=tk.TOP, fill=tk.X)

        self.line_button = tk.Button(
            self.toolbox, text="Line", command=self.set_line)
        self.line_button.pack(side=tk.LEFT)
        self.rect_button = tk.Button(
            self.toolbox, text="Rectangle", command=self.set_rectangle)
        self.rect_button.pack(side=tk.LEFT)

    def set_line(self):
        self.selected_tool = LINE

    def set_rectangle(self):
        self.selected_tool = RECTANGLE

    def handle_click(self, event):
        x, y = event.x, event.y
        if self.group_mode:
            obj = self.canvas.find_closest(x, y)
            # print(obj,obj[0])
            if obj:
                if len(self.selected_objects_grouped) == 0:
                    self.selected_objects_grouped.append(obj[0])
                elif obj[0] not in self.selected_objects_grouped:
                    self.selected_objects_grouped.append(obj[0])
                selected_group_object = self.canvas.create_rectangle(
                    self.canvas.bbox(self.selected_objects_grouped[-1]), outline="blue")
                self.selection_indicator_group.append(selected_group_object)
                # print(f"yes{self.selected_objects_grouped}")
            else:
                self.deselect_object()
        if self.selected_tool == LINE:
            if self.click_count == 0:
                self.create_line(event)
                self.canvas.bind("<Motion>", self.update_temp_line)
            elif self.click_count == 1:
                self.finalize_line(event)
                self.selected_tool = NONE
        elif self.selected_tool == RECTANGLE:
            if self.click_count == 0:
                # print(self.click_count)
                self.create_rectangle(event)
                self.canvas.bind("<Motion>", self.update_temp_rectangle)
            elif self.click_count == 1:
                self.finalize_rectangle(event)
                self.selected_tool = NONE
        else:
            self.select_object(x, y)

    def select_object(self, x, y):
        obj = self.canvas.find_closest(x, y)
        if obj:
            self.selected_object = obj[0]
            self.selected_group = obj[0]
            if self.selection_indicator:
                self.canvas.delete(self.selection_indicator)
            bbox = self.canvas.bbox(obj)
            if bbox:
                self.selection_indicator = self.canvas.create_rectangle(
                    bbox, outline="blue")

    def delete_object(self):
        if self.selected_object:
            for grps in self.groups:
                if grps['id'] == self.selected_object:
                    for objs in grps['objects']:
                        self.canvas.delete(objs)
                        if self.selection_indicator:
                            self.canvas.delete(self.selection_indicator)
            self.canvas.delete(self.selected_object)
            self.selected_object = None
            if self.selection_indicator:
                self.canvas.delete(self.selection_indicator)
            self.drawing_modified = True

    def copy_object(self):
        group_copy = False
        if self.selected_object:
            # print(self.selected_group)
            x = None
            for x in self.groups:
                id = x['id']
                if (id == self.selected_group):
                    # break
                    group_copy = True
                    print(x['objects'])
                    for obj in x['objects']:
                        # print(obj)
                        coords = self.canvas.coords(obj)
                        obj_type = self.canvas.type(obj)
                        offset = 10
                        if obj_type == LINE:
                            color = self.canvas.itemcget(obj, "fill")
                            new_coords = [coord + offset for coord in coords]
                            new_object = self.canvas.create_line(
                                *new_coords, fill=color)  # Assuming new line is black
                            self.selected_objects_grouped.append(new_object)
                        elif obj_type == RECTANGLE:
                            color = self.canvas.itemcget(obj, "outline")
                            new_coords = [
                                coord + offset if index % 2 == 0 else coord - offset for index, coord in enumerate(coords)]
                            # Assuming new rectangle is white with black outline
                            new_object = self.canvas.create_rectangle(
                                *new_coords, fill="white", outline=color)
                            self.selected_objects_grouped.append(new_object)
                        elif obj_type == POLYGON:
                            color = self.canvas.itemcget(obj, "outline")
                            new_coords = [
                                coord + offset if index % 2 == 0 else coord - offset for index, coord in enumerate(coords)]
                            # Assuming new rectangle is white with black outline
                            new_object = self.canvas.create_polygon(
                                *new_coords, fill="white", outline=color, smooth=True)
                            self.selected_objects_grouped.append(new_object)
                        self.objects.append(new_object)
                        self.drawing_modified = True
                self.group_objects()
                break

            if (group_copy == False):
                coords = self.canvas.coords(self.selected_object)
                obj_type = self.canvas.type(self.selected_object)
                offset = 10
                if obj_type == LINE:
                    color = self.canvas.itemcget(self.selected_object, "fill")
                    new_coords = [coord + offset for coord in coords]
                    new_object = self.canvas.create_line(
                        *new_coords, fill=color)  # Assuming new line is black
                elif obj_type == RECTANGLE:
                    color = self.canvas.itemcget(
                        self.selected_object, "outline")
                    new_coords = [coord + offset if index % 2 == 0 else coord -
                                  offset for index, coord in enumerate(coords)]
                    # Assuming new rectangle is white with black outline
                    new_object = self.canvas.create_rectangle(
                        *new_coords, fill="white", outline=color)
                elif obj_type == POLYGON:
                    color = self.canvas.itemcget(
                        self.selected_object, "outline")
                    new_coords = [coord + offset if index % 2 == 0 else coord -
                                  offset for index, coord in enumerate(coords)]
                    # Assuming new rectangle is white with black outline
                    new_object = self.canvas.create_polygon(
                        *new_coords, fill="white", outline=color, smooth=True)
                self.objects.append(new_object)
                self.drawing_modified = True

    def move_object(self):
        if self.selected_object:
            self.selected_objects_grouped.append(self.selected_object)
            for grp in self.groups:
                if grp["id"] == self.selected_object:
                    for objects in grp["objects"]:
                        self.selected_objects_grouped.append(objects)

            self.canvas.bind("<B1-Motion>", self.drag_object)
            self.canvas.bind("<ButtonRelease-1>", self.release_object)

           #  self.canvas.bind("<Button-3>", lambda event: self.rotate_object(90))

    def drag_object(self, event):
        x_diff = event.x - self.drag_data["x"]
        y_diff = event.y - self.drag_data["y"]

        if len(self.selected_objects_grouped) == 1:
            for obj in self.selected_objects_grouped:
                self.canvas.moveto(obj, event.x, event.y)

        for obj in self.selected_objects_grouped:
            self.canvas.move(obj, x_diff, y_diff)
            
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def rotate_object_dialog(self):
        # Create a dialog to input rotation angle
        if self.selected_object:
            dialog = tk.Toplevel(self.root)
            dialog.title("Rotate Object")

            tk.Label(dialog, text="Rotation Angle (degrees):").pack()
            angle_entry = tk.Entry(dialog)
            angle_entry.pack()

            tk.Button(dialog, text="Rotate",
                      command=lambda: self.rotate_object(angle_entry)).pack()

    def rotate_object(self, angle_entry):
        if self.selected_object:
            # Get the initial coordinates and center of the object
            angle_str = angle_entry.get()
            try:
                angle = float(angle_str)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid angle")

            rectangle_id = self.selected_object
            coords = self.canvas.coords(rectangle_id)
            obj_type = self.canvas.type(rectangle_id)

            x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
            if obj_type == RECTANGLE:
                self.delete_object()
                pol = self.create_rounded_rectangle(x1, y1, x2, y2, 0, "black")
                coords = self.canvas.coords(pol)
                x1, y1, x2, y2 = coords[28], coords[1], coords[8], coords[19]
                rectangle_id = pol

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Convert angle to radians for trigonometric functions
            angle_rad = math.radians(angle)

            new_coords = []
            # print(coords)
            for i in range(0, len(coords), 2):
                x = coords[i]
                y = coords[i + 1]
                # Translate coordinates to origin, rotate, then translate back
                new_x = center_x + \
                    (x-center_x) * math.cos(angle_rad) - \
                    (y-center_y) * math.sin(angle_rad)
                new_y = center_y+(x-center_x) * math.sin(angle_rad) + \
                    (y-center_y) * math.cos(angle_rad)
                new_coords.extend([new_x, new_y])

            self.canvas.coords(rectangle_id, *new_coords)
            # self.canvas.coords(self.selection_indicator, *new_coords)
            if self.selection_indicator:
                self.canvas.delete(self.selection_indicator)
            self.selected_object = rectangle_id
            bbox = self.canvas.bbox(rectangle_id)
            if bbox:
                self.selection_indicator = self.canvas.create_rectangle(
                    bbox, outline="blue")

            self.drawing_modified = True

    def release_object(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.selected_objects_grouped = []

    def create_line(self, event):
        if self.click_count == 0:
            self.start_x = event.x
            self.start_y = event.y
            self.click_count += 1

            if self.temp_line is not None:
                self.canvas.delete(self.temp_line)

            end_x, end_y = event.x, event.y
            self.temp_line = self.canvas.create_line(
                self.start_x, self.start_y, end_x, end_y, fill="black", width=1, dash=(2, 2))

    def update_temp_line(self, event):
        if self.click_count == 1:
            if self.temp_line is not None:
                end_x, end_y = event.x, event.y
                self.canvas.coords(self.temp_line, self.start_x,
                                   self.start_y, end_x, end_y)

    def finalize_line(self, event):
        if self.click_count == 1:
            end_x, end_y = event.x, event.y
            line = self.canvas.create_line(
                self.start_x, self.start_y, end_x, end_y, fill="black", width=1)
            self.objects.append(line)

            # Reset start coordinates
            self.start_x = None
            self.start_y = None
            self.click_count = 0

            # Delete temporary line
            if self.temp_line is not None:
                self.canvas.delete(self.temp_line)
                self.temp_line = None

            # Unbind motion event
            self.canvas.unbind("<Motion>")
            self.drawing_modified = True

    def create_rectangle(self, event):
        # print(self.click_count)
        if self.click_count == 0:
            self.start_x = event.x
            self.start_y = event.y
            self.click_count = 1

        if self.temp_rect is not None:
            self.canvas.delete(self.temp_rect)
        end_x, end_y = event.x, event.y
        self.temp_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, end_x, end_y, outline="black", width=1, fill="", dash=(2, 2))

    def update_temp_rectangle(self, event):
        if self.temp_rect is not None:
            end_x, end_y = event.x, event.y
            self.canvas.coords(self.temp_rect, self.start_x,
                               self.start_y, end_x, end_y)

    def finalize_rectangle(self, event):
        if self.click_count == 1:
            end_x, end_y = event.x, event.y
            rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, end_x, end_y, outline="black", width=1, fill="")
            self.objects.append(rect)

            # Reset start coordinates
            self.start_x = None
            self.start_y = None
            self.click_count = 0

            # Delete temporary rectangle
            if self.temp_rect is not None:
                self.canvas.delete(self.temp_rect)
                self.temp_rect = None

            # Unbind motion event
            self.canvas.unbind("<Motion>")
            self.drawing_modified = True

    def open_jpeg_drawing(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JPEG files", "*.jpeg")])
        if filename:
            img = Image.open(filename)
            photo = ImageTk.PhotoImage(img)

            # Clear the canvas before loading the new image
            self.canvas.delete("all")

            # Create a new image item on the canvas
            self.canvas.create_image(0, 0, anchor="nw", image=photo)

            # Save the reference to the photo to prevent it from being garbage collected
            self.canvas.photo = photo

            messagebox.showinfo(
                "Info", "Drawing loaded successfully from JPEG.")

    def save_drawing_as_XML(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xml")
        if filename:
            root = ET.Element("drawing")
            for obj in self.objects:
                obj_type = self.canvas.type(obj)
                if obj_type == LINE:
                    coords = self.canvas.coords(obj)
                    color = self.canvas.itemcget(obj, "fill")
                    line = ET.SubElement(root, "line")
                    start = ET.SubElement(line, "start")
                    start_x = ET.SubElement(start, "x")
                    start_x.text = str(coords[0])
                    start_y = ET.SubElement(start, "y")
                    start_y.text = str(coords[1])
                    end = ET.SubElement(line, "end")
                    end_x = ET.SubElement(end, "x")
                    end_x.text = str(coords[2])
                    end_y = ET.SubElement(end, "y")
                    end_y.text = str(coords[3])
                    line_color = ET.SubElement(line, "color")
                    line_color.text = color
                elif obj_type == RECTANGLE:
                    coords = self.canvas.coords(obj)
                    color = self.canvas.itemcget(obj, "fill")
                    rectangle = ET.SubElement(root, "rectangle")
                    upper_left = ET.SubElement(rectangle, "upper-left")
                    upper_left_x = ET.SubElement(upper_left, "x")
                    upper_left_x.text = str(coords[0])
                    upper_left_y = ET.SubElement(upper_left, "y")
                    upper_left_y.text = str(coords[1])
                    lower_right = ET.SubElement(rectangle, "lower-right")
                    lower_right_x = ET.SubElement(lower_right, "x")
                    lower_right_x.text = str(coords[2])
                    lower_right_y = ET.SubElement(lower_right, "y")
                    lower_right_y.text = str(coords[3])
                    rect_color = ET.SubElement(rectangle, "color")
                    rect_color.text = color

                elif obj_type == POLYGON:  # Add condition for polygons
                    coords = self.canvas.coords(obj)
                    color = self.canvas.itemcget(obj, "outline")
                    polygon = ET.SubElement(root, "polygon")
                    for i in range(0, len(coords), 2):
                        point = ET.SubElement(polygon, "point")
                        point_x = ET.SubElement(point, "x")
                        point_x.text = str(coords[i])
                        point_y = ET.SubElement(point, "y")
                        point_y.text = str(coords[i + 1])
                    poly_color = ET.SubElement(polygon, "color")
                    poly_color.text = color

            # Add grouped objects
            for grps in self.groups:
                group = ET.SubElement(root, "group")
                for obj in grps['objects']:
                    obj_type = self.canvas.type(obj)
                    if obj_type == LINE:
                        coords = self.canvas.coords(obj)
                        color = self.canvas.itemcget(obj, "fill")
                        line = ET.SubElement(group, "line")
                        start = ET.SubElement(line, "start")
                        start_x = ET.SubElement(start, "x")
                        start_x.text = str(coords[0])
                        start_y = ET.SubElement(start, "y")
                        start_y.text = str(coords[1])
                        end = ET.SubElement(line, "end")
                        end_x = ET.SubElement(end, "x")
                        end_x.text = str(coords[2])
                        end_y = ET.SubElement(end, "y")
                        end_y.text = str(coords[3])
                        line_color = ET.SubElement(line, "color")
                        line_color.text = color
                    elif obj_type == RECTANGLE:
                        coords = self.canvas.coords(obj)
                        color = self.canvas.itemcget(obj, "fill")
                        rectangle = ET.SubElement(group, "rectangle")
                        upper_left = ET.SubElement(rectangle, "upper-left")
                        upper_left_x = ET.SubElement(upper_left, "x")
                        upper_left_x.text = str(coords[0])
                        upper_left_y = ET.SubElement(upper_left, "y")
                        upper_left_y.text = str(coords[1])
                        lower_right = ET.SubElement(rectangle, "lower-right")
                        lower_right_x = ET.SubElement(lower_right, "x")
                        lower_right_x.text = str(coords[2])
                        lower_right_y = ET.SubElement(lower_right, "y")
                        lower_right_y.text = str(coords[3])
                        rect_color = ET.SubElement(rectangle, "color")
                        rect_color.text = color

                    elif obj_type == POLYGON:  # Handle polygon objects
                        coords = self.canvas.coords(obj)
                        color = self.canvas.itemcget(obj, "outline")
                        polygon = ET.SubElement(group, "polygon")
                        for i in range(0, len(coords), 2):
                            point = ET.SubElement(polygon, "point")
                            point_x = ET.SubElement(point, "x")
                            point_x.text = str(coords[i])
                            point_y = ET.SubElement(point, "y")
                            point_y.text = str(coords[i + 1])
                        poly_color = ET.SubElement(polygon, "color")
                        poly_color.text = color

            tree = ET.ElementTree(root)
            tree.write(filename)
            messagebox.showinfo("Info", "Drawing saved successfully.")
            self.drawing_modified = False

    def save_drawing_as_JPEG(self):
        filename = filedialog.asksaveasfilename(defaultextension=".jpeg")
        if filename:
            img = Image.new("RGB", (self.canvas.winfo_width(),
                            self.canvas.winfo_height()), "white")
            draw = ImageDraw.Draw(img)

            # Iterate over all canvas items and draw them onto the image
            for item in self.canvas.find_all():
                item_type = self.canvas.type(item)
                if item_type == "line":
                    coords = self.canvas.coords(item)
                    color = self.canvas.itemcget(item, "fill")
                    draw.line(coords, fill=color)

                elif item_type == "rectangle":
                    coords = self.canvas.coords(item)
                    color = self.canvas.itemcget(item, "outline")
                    draw.rectangle(coords, outline=color, fill="white")
                elif item_type == "polygon":
                    coords = self.canvas.coords(item)
                    color = self.canvas.itemcget(item, "outline")
                    draw.polygon(coords, outline=color, fill="white")

            img.save(filename, "JPEG")

    def save_drawing_as_TXT(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, "w") as f:
                for grps in self.groups:
                    f.write("begin\n")
                    for obj in grps['objects']:
                        obj_type = self.canvas.type(obj)
                        if obj_type == "line":
                            coords = self.canvas.coords(obj)
                            color = self.canvas.itemcget(obj, "fill")
                            if not color:
                                color = "white"
                            f.write(
                                f"{LINE} {coords[0]} {coords[1]} {coords[2]} {coords[3]} {color}\n")
                        elif obj_type == "rectangle":
                            coords = self.canvas.coords(obj)
                            color = self.canvas.itemcget(obj, "outline")
                            if not color:
                                color = "white"
                            f.write(
                                f"{RECTANGLE} {coords[0]} {coords[1]} {coords[2]} {coords[3]} {color}\n")
                        elif obj_type == "polygon":  # Handle polygon objects
                            coords = self.canvas.coords(obj)
                            color = self.canvas.itemcget(obj, "outline")
                            if not color:
                                color = "white"
                            f.write(
                                f"{POLYGON} {' '.join(map(str, coords))} {color}\n")
                    f.write("end\n")

                # iteration through main list
                for obj in self.objects:
                    obj_type = self.canvas.type(obj)
                    if obj_type == "line":
                        coords = self.canvas.coords(obj)
                        color = self.canvas.itemcget(obj, "fill")
                        if not color:
                            color = "white"
                        f.write(
                            f"{LINE} {coords[0]} {coords[1]} {coords[2]} {coords[3]} {color}\n")
                    elif obj_type == "rectangle":
                        coords = self.canvas.coords(obj)
                        color = self.canvas.itemcget(obj, "outline")
                        if not color:
                            color = "white"
                        f.write(
                            f"{RECTANGLE} {coords[0]} {coords[1]} {coords[2]} {coords[3]} {color}\n")
                    elif obj_type == "polygon":  # Handle polygon objects
                        coords = self.canvas.coords(obj)
                        color = self.canvas.itemcget(obj, "outline")
                        if not color:
                            color = "white"
                        f.write(
                            f"{POLYGON} {' '.join(map(str, coords))} {color}\n")
            messagebox.showinfo("Info", "Drawing saved successfully.")
            self.drawing_modified = False

    def open_drawing(self,file="none"):
        if self.drawing_modified:
            if messagebox.askyesno("Unsaved Changes", "There are unsaved changes. Do you want to save before opening a new file?"):
                self.save_drawing_as_TXT()
        
        if file=="none":    
            filename = filedialog.askopenfilename()
        else:
            filename=file
        if filename:
            if filename.endswith('.xml'):
                self.load_objects_from_XML(filename)
            elif filename.endswith('.txt'):
                self.load_objects_from_txt(filename)

    def load_objects_from_XML(self, filename):
        self.canvas.delete("all")
        tree = ET.parse(filename)
        root = tree.getroot()
        for obj in root:
            if obj.tag == "group":
                for group_obj in obj:
                    if group_obj.tag == "line":
                        start = group_obj.find("start")
                        start_x = int(float(start.find("x").text))
                        start_y = int(float(start.find("y").text))
                        end = group_obj.find("end")
                        end_x = int(float(end.find("x").text))
                        end_y = int(float(end.find("y").text))
                        color = group_obj.find("color").text
                        line = self.canvas.create_line(
                            start_x, start_y, end_x, end_y, fill=color)
                        self.selected_objects_grouped.append(line)
                    elif group_obj.tag == "rectangle":
                        upper_left = group_obj.find("upper-left")
                        upper_left_x = int(float(upper_left.find("x").text))
                        upper_left_y = int(float(upper_left.find("y").text))
                        lower_right = group_obj.find("lower-right")
                        lower_right_x = int(float(lower_right.find("x").text))
                        lower_right_y = int(float(lower_right.find("y").text))
                        color = group_obj.find("color").text
                        rect = self.canvas.create_rectangle(
                            upper_left_x, upper_left_y, lower_right_x, lower_right_y, outline=color)
                        self.selected_objects_grouped.append(rect)
                    elif group_obj.tag == "polygon":
                        points = []
                        for point in group_obj.findall("point"):
                            point_x = int(float(point.find("x").text))
                            point_y = int(float(point.find("y").text))
                            points.extend([point_x, point_y])
                        color = group_obj.find("color").text
                        poly = self.canvas.create_polygon(
                            points, outline=color, fill='white', smooth=True)
                        self.selected_objects_grouped.append(poly)
                self.group_objects()

            if obj.tag == "line":
                start = obj.find("start")
                start_x = int(float(start.find("x").text))
                start_y = int(float(start.find("y").text))
                end = obj.find("end")
                end_x = int(float(end.find("x").text))
                end_y = int(float(end.find("y").text))
                color = obj.find("color").text
                line = self.canvas.create_line(
                    start_x, start_y, end_x, end_y, fill=color)
                self.objects.append(line)
            elif obj.tag == "rectangle":
                upper_left = obj.find("upper-left")
                upper_left_x = int(float(upper_left.find("x").text))
                upper_left_y = int(float(upper_left.find("y").text))
                lower_right = obj.find("lower-right")
                lower_right_x = int(float(lower_right.find("x").text))
                lower_right_y = int(float(lower_right.find("y").text))
                color = obj.find("color").text
                rect = self.canvas.create_rectangle(
                    upper_left_x, upper_left_y, lower_right_x, lower_right_y, outline=color)
                self.objects.append(rect)
            elif obj.tag == "polygon":  # Add condition for polygons
                points = []
                for point in obj.findall("point"):
                    point_x = int(float(point.find("x").text))
                    point_y = int(float(point.find("y").text))
                    points.extend([point_x, point_y])
                color = obj.find("color").text
                poly = self.canvas.create_polygon(
                    points, outline=color, fill='white', smooth=True)
                self.objects.append(poly)

    def load_objects_from_txt(self, filename):
        flag = 0
        self.canvas.delete("all")
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if parts[0] == "begin":
                    flag = 1
                if parts[0] == "end":
                    self.group_objects()
                    flag = 0
                if parts[0] == LINE:
                    x1, y1, x2, y2 = map(float, parts[1:5])
                    color = parts[5]
                    line = self.canvas.create_line(x1, y1, x2, y2, fill=color)
                    if flag == 0:
                        self.objects.append(line)
                    elif flag == 1:
                        self.selected_objects_grouped.append(line)
                elif parts[0] == RECTANGLE:
                    x1, y1, x2, y2 = map(float, parts[1:5])
                    color = parts[5]
                    rect = self.canvas.create_rectangle(
                        x1, y1, x2, y2, outline=color)
                    if flag == 0:
                        self.objects.append(rect)
                    elif flag == 1:
                        self.selected_objects_grouped.append(rect)
                elif parts[0] == POLYGON:
                    coords = list(map(float, parts[1:-1]))
                    color = parts[-1]
                    # print(coords)
                    pol = self.canvas.create_polygon(
                        coords, outline=color, fill='white', smooth=True)
                    if flag == 0:
                        self.objects.append(pol)
                    elif flag == 1:
                        self.selected_objects_grouped.append(pol)

    def on_close(self):
        if self.drawing_modified:
            if messagebox.askyesno("Unsaved Changes", "Do you want to save changes before closing?"):
                self.save_drawing_as_TXT()
        self.root.destroy()

# -----------------------------------------------------------------------------------------------

    def edit_line_properties(self):
        # Get current line color
        current_color = self.canvas.itemcget(self.selected_object, "fill")

        # Create a dialog box for editing line color
        line_color = colorchooser.askcolor(
            title="Choose Line Color", initialcolor=current_color)[1]
        if line_color:
            self.canvas.itemconfig(self.selected_object, fill=line_color)
            self.drawing_modified = True

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, colour):

        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]

        pol = self.canvas.create_polygon(
            points, outline=colour, fill='white', smooth=True)
        self.objects.append(pol)
        return pol

    def edit_rectangle_properties(self):
        current_outline = self.canvas.itemcget(self.selected_object, "outline")
        
        outline_color = colorchooser.askcolor(
            title="Choose Outline Color", initialcolor=current_outline)[1]
      
        if outline_color:
            self.canvas.itemconfig(self.selected_object, outline=outline_color)
            self.drawing_modified = True
        if messagebox.askyesno("Round Corners", "Do you want to make the corners rounded?"):
            rectangle_id = self.selected_object
            coords = self.canvas.coords(rectangle_id)
            x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
            radius = 20
            colour = 'black'
            if outline_color:
                colour = outline_color
            self.delete_object()
            self.create_rounded_rectangle(x1, y1, x2, y2, radius, colour)
            self.drawing_modified = True
        else:
            polygon_id = self.selected_object
            points = self.canvas.coords(polygon_id)
            obj_type = self.canvas.type(self.selected_object)
            if obj_type == POLYGON:
                x1, y1, x2, y2 = points[28], points[1], points[8], points[19]
            elif obj_type == RECTANGLE:
                x1, y1, x2, y2 = points[0], points[1], points[2], points[3]
            # print(points)
            colour = 'black'
            if outline_color:
                colour = outline_color
            self.drawing_modified = True
            self.delete_object()
            self.create_rounded_rectangle(x1, y1, x2, y2, 0, colour)

    def edit_object(self):
        if self.selected_object:
            obj_type = self.canvas.type(self.selected_object)
            if obj_type == LINE:
                self.edit_line_properties()
            elif obj_type == RECTANGLE or obj_type == POLYGON:
                self.edit_rectangle_properties()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingEditor(root)
    root.mainloop()
