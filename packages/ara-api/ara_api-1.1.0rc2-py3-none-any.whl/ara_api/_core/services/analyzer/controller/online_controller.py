import signal
import sys

import customtkinter

from ara_api._core.services.analyzer.pages import (
    AccelPage,
    AnalogPage,
    GyroPage,
    MotorPage,
)

customtkinter.set_appearance_mode("system")


class AnalyzerServiceAPP(customtkinter.CTk):
    def __init__(self, csv_dir):
        super().__init__()
        self.csv_dir = csv_dir

        self.geometry("1200x800")
        self.title("Applied Robotics Avia Simple Analyzer")
        self.tk.call("tk", "scaling", 0.75)  # Set the scaling factor to 0.75

        self.button_frame = customtkinter.CTkFrame(self, width=200)
        self.button_frame.pack(side="right", fill="y", padx=20, pady=20)

        self.page_frame = customtkinter.CTkFrame(self)
        self.page_frame.pack(
            side="left", fill="both", expand=True, padx=20, pady=20
        )

        self.pages = {
            "Motor": MotorPage(self.page_frame, csv_dir=self.csv_dir),
            "Analog": AnalogPage(self.page_frame, csv_dir=self.csv_dir),
            "Accel": AccelPage(self.page_frame, csv_dir=self.csv_dir),
            "Gyro": GyroPage(self.page_frame, csv_dir=self.csv_dir),
        }

        for page in self.pages.values():
            page.pack(fill="both", expand=True)

        self.create_buttons()

        self.show_page("Motor")

        signal.signal(signal.SIGINT, self.signal_handler)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_buttons(self):
        motor_button = customtkinter.CTkButton(
            self.button_frame,
            text="Motor",
            command=lambda: self.show_page("Motor"),
        )
        motor_button.pack(pady=10, padx=10)

        analog_button = customtkinter.CTkButton(
            self.button_frame,
            text="Analog",
            command=lambda: self.show_page("Analog"),
        )
        analog_button.pack(pady=10, padx=10)

        accel_button = customtkinter.CTkButton(
            self.button_frame,
            text="Accel",
            command=lambda: self.show_page("Accel"),
        )
        accel_button.pack(pady=10, padx=10)

        gyro_button = customtkinter.CTkButton(
            self.button_frame,
            text="Gyro",
            command=lambda: self.show_page("Gyro"),
        )
        gyro_button.pack(pady=10, padx=10)

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)

    def signal_handler(self, sig, frame):
        self.stop_all_pages()
        sys.exit(0)

    def on_closing(self):
        self.stop_all_pages()
        self.destroy()

    def stop_all_pages(self):
        for page in self.pages.values():
            page.stop()


def main(csv):
    app = AnalyzerServiceAPP(csv_dir=csv)
    app.mainloop()


if __name__ == "__main__":
    main()
