import threading
import time

import customtkinter
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from ara_api._utils import GRPCDataFetcher


class AccelPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = GRPCDataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.accel_data = {"X": [], "Y": [], "Z": []}
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
            new_data = self.data_fetcher.get_imu_data()["accel"]
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            for axis, value in zip(self.accel_data.keys(), new_data):
                self.accel_data[axis].append(value)
                # Keep only the last 100 accel data points
                if len(self.accel_data[axis]) > 100:
                    self.accel_data[axis].pop(0)

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

        colors = {"X": (255, 0, 0), "Y": (0, 255, 0), "Z": (0, 0, 255)}
        name = ["X", "Y", "Z"]

        for i, axis in enumerate(name):
            y_data = np.array(self.accel_data[axis][-100:], dtype=np.int32)
            y_data = np.interp(
                y_data,
                [-200, 200],
                [
                    height // 3 * (i + 1) - margin_bottom,
                    height // 3 * i + margin_bottom,
                ],
            )

            # Draw Y axis
            cv2.line(
                img,
                (margin_left, height // 3 * i + margin_bottom),
                (margin_left, height // 3 * (i + 1) - margin_bottom),
                (0, 0, 0),
                1,
            )
            # Draw X axis
            cv2.line(
                img,
                (margin_left, height // 3 * (i + 1) - margin_bottom),
                (width - margin_left, height // 3 * (i + 1) - margin_bottom),
                (0, 0, 0),
                1,
            )

            # Draw Y axis labels
            for y in range(-200, 201, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [-200, 200],
                        [
                            height // 3 * (i + 1) - margin_bottom,
                            height // 3 * i + margin_bottom,
                        ],
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
                        (x_pos, height // 3 * (i + 1) - 10),
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
                    colors[axis],
                    2,
                )

            # Draw legend
            legend_x = width - 150
            legend_y = height // 3 * i + 20
            current_value = (
                self.accel_data[axis][-1] if self.accel_data[axis] else 0
            )
            cv2.putText(
                img,
                f"{axis}: {current_value}",
                (legend_x, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                colors[axis],
                1,
            )

        return img

    def start_csv_saving(self):
        threading.Thread(target=self.save_to_csv).start()

    def save_to_csv(self):
        while self.running:
            time.sleep(10)  # Save data every 10 seconds
            with self.csv_lock:
                data = {
                    "time": self.time_data,
                    "accel_x": self.accel_data["X"],
                    "accel_y": self.accel_data["Y"],
                    "accel_z": self.accel_data["Z"],
                }
                df = pd.DataFrame(data)
                df.to_csv(
                    f"{self.csv_dir}/accel_data.csv",
                    mode="a",
                    header=not self.header_added,
                    index=False,
                )
                if not self.header_added:
                    self.header_added = True

    def stop(self):
        self.running = False


class AccelOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/accel_data.csv"

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

        colors = {
            "accel_x": (255, 0, 0),
            "accel_y": (0, 255, 0),
            "accel_z": (0, 0, 255),
        }
        name = ["accel_x", "accel_y", "accel_z"]

        for i, axis in enumerate(name):
            y_data = np.array(df[axis], dtype=np.int32)
            y_data = np.interp(
                y_data,
                [-200, 200],
                [
                    height // 3 * (i + 1) - margin_bottom,
                    height // 3 * i + margin_bottom,
                ],
            )
            x_data = np.array(df["time"], dtype=np.int16)

            cv2.line(
                img=img,
                pt1=(margin_left, height // 3 * i + margin_bottom),
                pt2=(margin_left, height // 3 * (i + 1) - margin_bottom),
                color=(0, 0, 0),
                thickness=1,
            )
            cv2.line(
                img=img,
                pt1=(margin_left, height // 3 * (i + 1) - margin_bottom - 100),
                pt2=(
                    width - margin_bottom,
                    height // 3 * (i + 1) - margin_bottom - 100,
                ),
                color=(0, 0, 0),
                thickness=1,
            )

            for y in range(-200, 201, 100):
                y_pos = int(
                    np.interp(
                        y,
                        [-200, 200],
                        [
                            height // 3 * (i + 1) - margin_bottom,
                            height // 3 * i + margin_bottom,
                        ],
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
                cv2.putText(
                    img=img,
                    text=f"{round(x_data[x])}" if x_data[x] != 0 else "",
                    org=(x_pos, height // 3 * (i + 1) - 110),
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.3,
                    color=(0, 0, 0),
                    thickness=1,
                )

            for j in range(1, len(y_data)):
                cv2.line(
                    img=img,
                    pt1=(
                        margin_left
                        + int(
                            np.interp(
                                j - 1,
                                [0, len(y_data) - 1],
                                [0, width - 2 * margin_left],
                            )
                        ),
                        int(y_data[j - 1]),
                    ),
                    pt2=(
                        margin_left
                        + int(
                            np.interp(
                                j,
                                [0, len(y_data) - 1],
                                [0, width - 2 * margin_left],
                            )
                        ),
                        int(y_data[j]),
                    ),
                    color=colors[axis],
                    thickness=2,
                )

        return img
