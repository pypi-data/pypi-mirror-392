import threading
import time

import customtkinter
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from ara_api._utils import GRPCDataFetcher


class MotorPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = GRPCDataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.motor_data = {
            "motor_1": [],
            "motor_2": [],
            "motor_3": [],
            "motor_4": [],
        }
        self.label = customtkinter.CTkLabel(self)
        self.label.pack(fill="both", expand=True)
        self.lock = threading.Lock()
        self.csv_lock = threading.Lock()
        self.running = True
        self.header_added = False
        self.update_graphs()
        self.start_csv_saving()

    def update_graphs(self):
        if self.running:
            threading.Thread(target=self.fetch_data).start()
            threading.Thread(target=self.update_image).start()
            self.after(100, self.update_graphs)  # Schedule the next update

    def fetch_data(self):
        with self.lock:
            if not hasattr(self, "start_time"):
                self.start_time = time.time()

            current_time = time.time() - self.start_time
            new_data = self.data_fetcher.get_motor_data()
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            for motor in self.motor_data.keys():
                self.motor_data[motor].append(new_data[motor])
                # Keep only the last 100 motor data points
                if len(self.motor_data[motor]) > 100:
                    self.motor_data[motor].pop(0)

    def update_image(self):
        with self.lock:
            img = self.create_image()
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(img)
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)

    def create_image(self):
        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        colors = {
            "motor_1": (255, 0, 0),
            "motor_2": (0, 255, 0),
            "motor_3": (0, 0, 255),
            "motor_4": (255, 0, 255),
        }

        # Draw legend
        legend_x = width - 150
        legend_y = 30
        for motor, color in colors.items():
            current_value = (
                self.motor_data[motor][-1] if self.motor_data[motor] else 0
            )
            cv2.putText(
                img,
                f"{motor}: {current_value}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )
            legend_y += 20

        for motor, color in colors.items():
            y_data = np.array(self.motor_data[motor][-100:], dtype=np.int32)
            y_data = np.interp(
                y_data, [1000, 2000], [height - margin_bottom, margin_bottom]
            )

            # Draw Y axis
            cv2.line(
                img,
                (margin_left, margin_bottom),
                (margin_left, height - margin_bottom),
                (0, 0, 0),
                1,
            )
            # Draw X axis
            cv2.line(
                img,
                (margin_left, height - margin_bottom),
                (width - margin_left, height - margin_bottom),
                (0, 0, 0),
                1,
            )

            # Draw Y axis labels
            for y in range(1000, 2000, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [1000, 2000],
                        [height - margin_bottom, margin_bottom],
                    )
                )
                cv2.putText(
                    img,
                    str(y),
                    (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                )

            # Draw X axis labels
            x_start = max(0, len(self.time_data) - 100)
            for x in range(x_start, x_start + 101, 10):
                if x < len(self.time_data):
                    x_pos = int(
                        np.interp(
                            x - x_start,
                            [0, 100],
                            [margin_left, width - margin_left],
                        )
                    )
                    cv2.putText(
                        img,
                        f"{self.time_data[x]:.1f}",
                        (x_pos, height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (0, 0, 0),
                        1,
                    )

            for j in range(1, len(y_data)):
                cv2.line(
                    img,
                    (
                        margin_left
                        + int(
                            np.interp(
                                j, [0, 100], [0, width - 2 * margin_left]
                            )
                        ),
                        int(y_data[j - 1]),
                    ),
                    (
                        margin_left
                        + int(
                            np.interp(
                                j + 1, [0, 100], [0, width - 2 * margin_left]
                            )
                        ),
                        int(y_data[j]),
                    ),
                    color,
                    2,
                )

        return img

    def start_csv_saving(self):
        threading.Thread(target=self.save_to_csv).start()


class MotorOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/motor_data.csv"

        self.canvas = customtkinter.CTkCanvas(
            self, bg="white", highlightthickness=0
        )
        self.canvas.bind(sequence="<Map>", func=self.update_canvas)
        self.canvas.pack(fill="both", expand=True)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())

        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        df = pd.read_csv(self.csv_file)

        height, width = self.winfo_height(), self.winfo_width()
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        margin_left = 60
        margin_bottom = 30

        rect_w, rect_h = 120, 20

        colors = {
            "motor_1": (255, 0, 0),
            "motor_2": (0, 255, 0),
            "motor_3": (0, 0, 255),
            "motor_4": (255, 0, 255),
        }

        legend_x = width - 150
        legend_y = 30

        for motor, color in colors.items():
            y_data = np.array(df[f"{motor}"], dtype=np.int16)
            y_data = np.interp(
                y_data, [1000, 2000], [height - margin_bottom, margin_bottom]
            )
            x_data = np.array(df["time"], dtype=np.int16)

            # draw axis
            cv2.line(
                img=img,
                pt1=(margin_left, margin_bottom),
                pt2=(margin_left, height - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )
            cv2.line(
                img=img,
                pt1=(margin_left, height - margin_bottom),
                pt2=(width - margin_left, height - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )

            for y in range(1000, 2001, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [1000, 2000],
                        [height - margin_bottom, margin_bottom],
                    )
                )
                cv2.putText(
                    img=img,
                    text=str(y),
                    org=(10, y_pos),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            for x in range(0, len(x_data), 200):
                x_pos = int(
                    np.interp(
                        x,
                        [0, len(df["time"])],
                        [margin_left, width - margin_left],
                    )
                )
                text_value = (
                    round(x_data[x])
                    + (0 if (x_data[x] == 0 or x_data[x] == 500) else 1)
                )
                cv2.putText(
                    img=img,
                    text=f"{text_value}",
                    org=(x_pos, height - 10),
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            end = int(y_data[len(y_data) - 1])
            for j in range(1, len(y_data)):
                cv2.line(
                    img=img,
                    pt1=(
                        margin_left
                        + int(
                            np.interp(
                                j, [0, end], [0, width - 2 * margin_left]
                            )
                        ),
                        int(y_data[j - 1]),
                    ),
                    pt2=(
                        margin_left
                        + int(
                            np.interp(
                                j + 1, [0, end], [0, width - 2 * margin_left]
                            )
                        ),
                        int(y_data[j]),
                    ),
                    color=color,
                    thickness=2,
                )

        for motor, color in colors.items():
            cv2.rectangle(
                img,
                (legend_x, legend_y + 4),
                (legend_x + rect_w, legend_y - rect_h + 2),
                color=(140, 138, 138),
                thickness=-1,
            )
            cv2.putText(
                img,
                f"{motor}: {round(np.mean(df[f'{motor}']))}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )
            legend_y += 25

        return img
