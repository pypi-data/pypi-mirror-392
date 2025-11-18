import argparse
import os
from importlib.metadata import version

import pyfiglet
from colorama import Fore

from ara_api._core.services.analyzer import offline, online


def main():
    ansii_art = pyfiglet.figlet_format(
        "ARA MINI ANALYZER {}".format(version("ara_api")),
        font="slant",
        width=70,
    )
    summary = (
        "{cyan}Поздравляем! Вы запустили анализатор для обработки данных с "
        "{cyan}дрона ARA MINI\n"
        "{cyan}Анализатор работает в двух режимах: онлайн и оффлайн\n"
        "{cyan}Для работы в онлайн режиме необходимо подключение к дрону"
        "{cyan}по WiFi и запущенное ядро API(ara-api-core)\n"
    ).format(cyan=Fore.CYAN)

    print(Fore.BLUE + ansii_art)
    print(summary)

    parser = argparse.ArgumentParser(
        description="Applied Robotics Avia Simple Analyzer"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        required=False,
        help="Directory to save CSV files",
    )
    parser.add_argument(
        "--csv-dir",
        type=str,
        required=True,
        help="Directory to save CSV files",
    )
    args = parser.parse_args()

    if not os.path.exists(args.csv_dir):
        os.makedirs(args.csv_dir)

    if not args.offline:
        online(args.csv_dir)

    if args.offline:
        offline(args.csv_dir)


if __name__ == "__main__":
    main()
