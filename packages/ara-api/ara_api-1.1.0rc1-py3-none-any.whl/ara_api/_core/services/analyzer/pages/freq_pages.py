import customtkinter
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk


class FrequencyOfflinePage(customtkinter.CTkFrame):
    def __init__(self, master, csv_dir, **kwargs):
        super().__init__(master, **kwargs)
        self.csv_gyro_file = csv_dir + "/gyro_data.csv"
        self.csv_accel_file = csv_dir + "/accel_data.csv"

        self.canvas = customtkinter.CTkCanvas(
            self, bg="white", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.update_canvas)

    def update_canvas(self, event):
        img = Image.fromarray(self.create_image())
        new_img = ImageTk.PhotoImage(img)
        self.canvas.image = new_img
        self.canvas.create_image(0, 0, anchor="nw", image=new_img)

    def create_image(self):
        sampling_rate = 400.0
        img_height, img_width = (
            self.canvas.winfo_height(),
            self.canvas.winfo_width(),
        )
        if img_height < 1 or img_width < 1:
            img_height, img_width = 400, 600

        img = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255

        # Считываем данные
        df_gyro = pd.read_csv(self.csv_gyro_file)
        df_accel = pd.read_csv(self.csv_accel_file)

        # Выбираем примеры столбца: gyro_x, acc_x
        gyro_data = np.array(df_gyro["gyro_x"], dtype=np.float32)
        accel_data = np.array(df_accel["accel_x"], dtype=np.float32)

        # Вычисляем FFT
        gyro_fft = np.fft.fft(gyro_data)
        accel_fft = np.fft.fft(accel_data)

        freqs_gyro = np.fft.fftfreq(len(gyro_data), d=1.0 / sampling_rate)
        freqs_accel = np.fft.fftfreq(len(accel_data), d=1.0 / sampling_rate)

        # Берем положительные частоты
        pos_mask_gyro = freqs_gyro >= 0
        pos_mask_accel = freqs_accel >= 0

        freqs_gyro = freqs_gyro[pos_mask_gyro]
        gyro_amp = np.abs(gyro_fft[pos_mask_gyro])
        gyro_phase = np.angle(gyro_fft[pos_mask_gyro])

        freqs_accel = freqs_accel[pos_mask_accel]
        accel_amp = np.abs(accel_fft[pos_mask_accel])
        accel_phase = np.angle(accel_fft[pos_mask_accel])

        # Координаты для двух графиков (амплитуда вверху, фаза внизу)
        half_height = img_height // 2
        margin_left = 60
        margin_bottom_amp = half_height - 20
        margin_bottom_phase = img_height - 20

        # Рисуем оси (верхняя для амплитуды, нижняя для фазы)
        cv2.line(
            img,
            (margin_left, 20),
            (margin_left, margin_bottom_amp),
            (0, 0, 0),
            1,
        )
        cv2.line(
            img,
            (margin_left, margin_bottom_amp),
            (img_width - margin_left, margin_bottom_amp),
            (0, 0, 0),
            1,
        )
        cv2.line(
            img,
            (margin_left, half_height + 20),
            (margin_left, margin_bottom_phase),
            (0, 0, 0),
            1,
        )
        cv2.line(
            img,
            (margin_left, margin_bottom_phase),
            (img_width - margin_left, margin_bottom_phase),
            (0, 0, 0),
            1,
        )

        # Рисуем график амплитуды
        max_amp = float(max(gyro_amp.max(), accel_amp.max(), 1))

        def scale_amp(amp):
            return np.interp(amp, [0, max_amp], [0, margin_bottom_amp - 20])

        for i in range(1, len(gyro_amp)):
            x1 = int(
                np.interp(
                    freqs_gyro[i - 1],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y1 = margin_bottom_amp - int(scale_amp(gyro_amp[i - 1]))
            x2 = int(
                np.interp(
                    freqs_gyro[i],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y2 = margin_bottom_amp - int(scale_amp(gyro_amp[i]))
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        for i in range(1, len(accel_amp)):
            x1 = int(
                np.interp(
                    freqs_accel[i - 1],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y1 = margin_bottom_amp - int(scale_amp(accel_amp[i - 1]))
            x2 = int(
                np.interp(
                    freqs_accel[i],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            y2 = margin_bottom_amp - int(scale_amp(accel_amp[i]))
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Рисуем график фазы (нижний)
        phase_min, phase_max = -np.pi, np.pi
        y_range_phase = margin_bottom_phase - (half_height + 20)

        def scale_phase(ph):
            return np.interp(ph, [phase_min, phase_max], [0, y_range_phase])

        for i in range(1, len(gyro_phase)):
            x1 = int(
                np.interp(
                    freqs_gyro[i - 1],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph1 = margin_bottom_phase - int(scale_phase(gyro_phase[i - 1]))
            x2 = int(
                np.interp(
                    freqs_gyro[i],
                    [0, freqs_gyro[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph2 = margin_bottom_phase - int(scale_phase(gyro_phase[i]))
            cv2.line(img, (x1, ph1), (x2, ph2), (255, 0, 0), 2)

        for i in range(1, len(accel_phase)):
            x1 = int(
                np.interp(
                    freqs_accel[i - 1],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph1 = margin_bottom_phase - int(scale_phase(accel_phase[i - 1]))
            x2 = int(
                np.interp(
                    freqs_accel[i],
                    [0, freqs_accel[-1]],
                    [margin_left, img_width - margin_left],
                )
            )
            ph2 = margin_bottom_phase - int(scale_phase(accel_phase[i]))
            cv2.line(img, (x1, ph1), (x2, ph2), (0, 255, 0), 2)

        # Добавляем ось X: частоты
        max_freq = (
            max(freqs_gyro[-1], freqs_accel[-1])
            if len(freqs_gyro) > 1 and len(freqs_accel) > 1
            else sampling_rate
        )
        num_ticks_x = 6
        for tick in np.linspace(0, max_freq, num_ticks_x):
            x_pos = int(
                np.interp(
                    tick, [0, max_freq], [margin_left, img_width - margin_left]
                )
            )
            cv2.putText(
                img,
                f"{tick:.1f}",
                (x_pos, img_height - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
            )

        cv2.putText(
            img,
            "Frequency [Hz]",
            (img_width // 2 - 50, img_height - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
        )

        # Добавляем ось Y для амплитуды (upper plot)
        num_ticks_amp = 4
        for tick in np.linspace(0, max_amp, num_ticks_amp):
            y_pos = margin_bottom_amp - int(
                np.interp(tick, [0, max_amp], [0, margin_bottom_amp - 20])
            )
            cv2.putText(
                img,
                f"{tick:.1f}",
                (margin_left - 35, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
            )
        cv2.putText(
            img,
            "Amplitude",
            (margin_left + 10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
        )

        # Добавляем ось Y для фазы (lower plot)
        num_ticks_phase = 5
        for tick in np.linspace(phase_min, phase_max, num_ticks_phase):
            tick_deg = np.degrees(tick)
            # ограничим текст в интервале ±180
            y_pos = margin_bottom_phase - int(
                np.interp(tick, [phase_min, phase_max], [0, y_range_phase])
            )
            cv2.putText(
                img,
                f"{tick_deg:.0f}",
                (margin_left - 35, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1,
            )
        cv2.putText(
            img,
            "Phase [deg]",
            (margin_left + 10, half_height + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
        )

        return img
