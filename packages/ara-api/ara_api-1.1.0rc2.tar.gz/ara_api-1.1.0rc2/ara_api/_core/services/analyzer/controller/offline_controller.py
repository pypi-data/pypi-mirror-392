import customtkinter

from ara_api._core.services.analyzer.pages import (
    AccelOfflinePage,
    AnalogOfflinePage,
    FrequencyOfflinePage,
    GyroOfflinePage,
    MotorOfflinePage,
)

customtkinter.set_appearance_mode("system")


class AnalyzerOfflineAPP(customtkinter.CTk):
    def __init__(self, csv_dir):
        super().__init__()

        self.geometry("1200x800")
        self.title("Applied Robotics Avia Simple Offline Analyzer")
        self.tk.call("tk", "scaling", 0.75)

        self.button_frame = customtkinter.CTkFrame(self, width=200)
        self.button_frame.pack(side="right", fill="y", padx=20, pady=20)

        self.page_frame = customtkinter.CTkFrame(self)
        self.page_frame.pack(
            side="left", fill="both", expand=True, padx=20, pady=20
        )

        self.pages = {
            "Motor": MotorOfflinePage(self.page_frame, csv_dir=csv_dir),
            "Analog": AnalogOfflinePage(self.page_frame, csv_dir=csv_dir),
            "Gyro": GyroOfflinePage(self.page_frame, csv_dir=csv_dir),
            "Accel": AccelOfflinePage(self.page_frame, csv_dir=csv_dir),
            "Frequency": FrequencyOfflinePage(
                self.page_frame, csv_dir=csv_dir
            ),
        }

        self.create_buttons()

        for page in self.pages.values():
            page.pack(fill="both", expand=True)

    def create_buttons(self):
        motor_button = customtkinter.CTkButton(
            self.button_frame,
            width=200,
            height=30,
            text="Motor",
            corner_radius=5,
            font=customtkinter.CTkFont(
                family="Helvetica", size=8, weight="bold"
            ),
            command=lambda: self.show_page("Motor"),
        )
        motor_button.pack(padx=20, pady=20)

        analog_button = customtkinter.CTkButton(
            self.button_frame,
            width=200,
            height=30,
            text="Amperage and Voltage",
            corner_radius=5,
            font=customtkinter.CTkFont(
                family="Helvetica", size=8, weight="bold"
            ),
            command=lambda: self.show_page("Analog"),
        )
        analog_button.pack(padx=20, pady=20)

        gyro_button = customtkinter.CTkButton(
            self.button_frame,
            width=200,
            height=30,
            text="Gyroscope",
            corner_radius=5,
            font=customtkinter.CTkFont(
                family="Helvetica", size=8, weight="bold"
            ),
            command=lambda: self.show_page("Gyro"),
        )
        gyro_button.pack(padx=20, pady=20)

        accel_button = customtkinter.CTkButton(
            self.button_frame,
            width=200,
            height=30,
            text="Accelerometer",
            corner_radius=5,
            font=customtkinter.CTkFont(
                family="Helvetica", size=8, weight="bold"
            ),
            command=lambda: self.show_page("Accel"),
        )
        accel_button.pack(padx=20, pady=20)

        frequency_button = customtkinter.CTkButton(
            self.button_frame,
            width=200,
            height=30,
            text="Frequency Graphs",
            corner_radius=5,
            font=customtkinter.CTkFont(
                family="Helvetica", size=8, weight="bold"
            ),
            command=lambda: self.show_page("Frequency"),
        )
        frequency_button.pack(padx=20, pady=20)

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)


def main(csv):
    app = AnalyzerOfflineAPP(csv_dir=csv)
    app.mainloop()


if __name__ == "__main__":
    main("csv_data_0")
