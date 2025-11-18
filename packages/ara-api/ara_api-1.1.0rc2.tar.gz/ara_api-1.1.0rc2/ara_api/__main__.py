from ara_api._core import ApplicationManager


def main():
    """Entry point for the application."""
    manager = ApplicationManager()
    manager.mainloop()


if __name__ == "__main__":
    main()
