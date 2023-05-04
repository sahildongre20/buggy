import os
import subprocess


def setup():
    # print("Installing required Python packages...")
    # subprocess.call("pip install -r requirements.txt")

    print("Running database migrations...")
    subprocess.call("python manage.py migrate")


def start_server():
    print("Starting Django development server...")
    subprocess.Popen('start cmd /k "python manage.py runserver"')


def open_browser():
    print("Opening default browser...")
    os.system('start "" "http://localhost:8000"')


def main():
    print("script to run BugPredictor Project")
    setup()
    start_server()
    open_browser()


if __name__ == "__main__":
    main()
