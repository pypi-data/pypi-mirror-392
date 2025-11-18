import threading
import time

import customtkinter
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from ara_api._utils import GRPCDataFetcher


class AnalogPage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.data_fetcher = GRPCDataFetcher()
        self.csv_dir = csv_dir
        self.time_data = []
        self.voltage_data = []
        self.current_data = []
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
            new_data = self.data_fetcher.get_analog_data()
            self.time_data.append(current_time)

            # Keep only the last 100 time data points
            if len(self.time_data) > 100:
                self.time_data.pop(0)

            self.voltage_data.append(new_data["voltage"])
            self.current_data.append(new_data["current"])

            # Keep only the last 100 data points
            if len(self.voltage_data) > 100:
                self.voltage_data.pop(0)
            if len(self.current_data) > 100:
                self.current_data.pop(0)

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
        margin_top = 30

        # Draw voltage graph
        y_data = np.array(self.voltage_data[-100:], dtype=np.float32)
        y_data = np.interp(
            y_data, [0, 5], [height // 2 - margin_bottom, margin_top]
        )

        # Draw Y axis for voltage
        cv2.line(
            img,
            (margin_left, margin_top),
            (margin_left, height // 2 - margin_bottom),
            (0, 0, 0),
            1,
        )
        # Draw X axis for voltage
        cv2.line(
            img,
            (margin_left, height // 2 - margin_bottom),
            (width - margin_left, height // 2 - margin_bottom),
            (0, 0, 0),
            1,
        )

        # Draw Y axis labels for voltage
        for y in range(0, 6):
            y_pos = int(
                np.interp(y, [0, 5], [height // 2 - margin_bottom, margin_top])
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
                    (x_pos, height // 2 - 10),
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
                        np.interp(j, [0, 100], [0, width - 2 * margin_left])
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
                (0, 0, 255),
                2,
            )

        # Draw legend for voltage
        legend_x = width - 150
        legend_y = 30
        current_voltage = self.voltage_data[-1] if self.voltage_data else 0
        cv2.putText(
            img,
            f"Voltage: {current_voltage:.2f}V",
            (legend_x, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )

        # Draw current graph
        y_data = np.array(self.current_data[-100:], dtype=np.float32)
        y_data = np.interp(
            y_data, [0, 15], [height - margin_bottom, height // 2 + margin_top]
        )

        # Draw Y axis for current
        cv2.line(
            img,
            (margin_left, height // 2 + margin_top),
            (margin_left, height - margin_bottom),
            (0, 0, 0),
            1,
        )
        # Draw X axis for current
        cv2.line(
            img,
            (margin_left, height - margin_bottom),
            (width - margin_left, height - margin_bottom),
            (0, 0, 0),
            1,
        )

        # Draw Y axis labels for current
        for y in range(0, 16, 3):
            y_pos = int(
                np.interp(
                    y,
                    [0, 15],
                    [height - margin_bottom, height // 2 + margin_top],
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

        for j in range(1, len(y_data)):
            cv2.line(
                img,
                (
                    margin_left
                    + int(
                        np.interp(j, [0, 100], [0, width - 2 * margin_left])
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
                (0, 0, 255),
                2,
            )

        # Draw legend for current
        legend_y = height // 2 + 50
        current_current = self.current_data[-1] if self.current_data else 0
        cv2.putText(
            img,
            f"Current: {current_current:.2f}A",
            (legend_x, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
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
                    "voltage": self.voltage_data,
                    "amperage": self.current_data,
                }
                df = pd.DataFrame(data)
                df.to_csv(
                    f"{self.csv_dir}/amper_voltage_data.csv",
                    mode="a",
                    header=not self.header_added,
                    index=False,
                )
                if not self.header_added:
                    self.header_added = True

    def stop(self):
        self.running = False


class AnalogOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_file = csv_dir + "/amper_voltage_data.csv"

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

        colors = {"voltage": (255, 0, 0), "amperage": (255, 0, 0)}

        time_data = np.array(df["time"])

        voltage_data = np.array(df["voltage"], dtype=np.int32)
        voltage_data = np.interp(
            voltage_data, [0, 5], [height // 2 - margin_bottom, margin_bottom]
        )
        amperage_data = np.array(df["amperage"], dtype=np.int32)
        amperage_data = np.interp(
            amperage_data,
            [0, 15],
            [height // 2 - margin_bottom, margin_bottom],
        )

        # axis for voltage
        cv2.line(
            img=img,
            pt1=(margin_left, margin_bottom),
            pt2=(margin_left, height // 2 - margin_bottom),
            color=(0, 0, 0),
            thickness=1,
        )

        cv2.line(
            img=img,
            pt1=(margin_left, height // 2 - margin_bottom),
            pt2=(width - margin_left, height // 2 - margin_bottom),
            color=(0, 0, 0),
            thickness=1,
        )

        # axis for amperage
        cv2.line(
            img=img,
            pt1=(margin_left, height // 2 + margin_bottom),
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

        # Draw Y axis labels for voltage
        for y in range(0, 6):
            y_pos = int(
                np.interp(
                    y, [0, 5], [height // 2 - margin_bottom, margin_bottom]
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

        # Draw Y axis labels for amperage
        for y in range(0, 16, 3):
            y_pos = int(
                np.interp(
                    y,
                    [0, 15],
                    [height - margin_bottom, height // 2 + margin_bottom],
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
        x_start = max(0, len(time_data) - 100)
        for x in range(x_start, x_start + 101, 10):
            if x < len(time_data):
                x_pos = int(
                    np.interp(
                        x - x_start,
                        [0, 100],
                        [margin_left, width - margin_left],
                    )
                )
                cv2.putText(
                    img,
                    f"{time_data[x]:.1f}",
                    (x_pos, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 0),
                    1,
                )

        for j in range(1, len(voltage_data)):
            cv2.line(
                img=img,
                pt1=(
                    margin_left
                    + int(
                        np.interp(
                            j - 1,
                            [0, len(voltage_data) - 1],
                            [0, width - 2 * margin_left],
                        )
                    ),
                    int(voltage_data[j - 1]),
                ),
                pt2=(
                    margin_left
                    + int(
                        np.interp(
                            j,
                            [0, len(voltage_data) - 1],
                            [0, width - 2 * margin_left],
                        )
                    ),
                    int(voltage_data[j]),
                ),
                color=colors["voltage"],
                thickness=2,
            )

        for j in range(1, len(amperage_data)):
            cv2.line(
                img=img,
                pt1=(
                    margin_left
                    + int(
                        np.interp(
                            j - 1,
                            [0, len(amperage_data) - 1],
                            [0, width - 2 * margin_left],
                        )
                    ),
                    int(amperage_data[j - 1] + height // 2),
                ),
                pt2=(
                    margin_left
                    + int(
                        np.interp(
                            j,
                            [0, len(amperage_data) - 1],
                            [0, width - 2 * margin_left],
                        )
                    ),
                    int(amperage_data[j] + height // 2),
                ),
                color=colors["amperage"],
                thickness=2,
            )

        return img
