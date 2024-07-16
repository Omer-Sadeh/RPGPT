from backend.Endpoint import run_app
from threading import Thread
from colorama import init, Fore, Style
import subprocess

init(autoreset=True)


def run_frontend_command(command):
    frontend_dir = './frontend'
    process = subprocess.Popen(command, shell=True, cwd=frontend_dir)
    process.wait()


if __name__ == "__main__":
    print(Style.BRIGHT + Fore.BLUE + """
            .______      .______     _______ .______   .___________.
            |   _  \     |   _  \   /  _____||   _  \  |           |
            |  |_)  |    |  |_)  | |  |  __  |  |_)  | `---|  |----`
            |      /     |   ___/  |  | |_ | |   ___/      |  |     
            |  |\  \----.|  |      |  |__| | |  |          |  |     
            | _| `._____|| _|       \______| | _|          |__|     
          """ + Style.RESET_ALL)

    print(Style.BRIGHT + "What would you like to do?\n" + Style.RESET_ALL)
    print("1. Run the backend server (dev)")
    print("2. Run both servers (dev)")
    print("3. Run the frontend app (dev)")
    print("4. Build the frontend app (for prod)")

    choice1 = input(Style.BRIGHT + "Enter your choice: " + Style.RESET_ALL)

    if choice1 == "1":
        print("\nRunning the backend server...\n" +
              Fore.LIGHTBLACK_EX + "Closing this window will stop the server." + Style.RESET_ALL)
        run_app()
    elif choice1 == "2":
        Thread(target=run_app, daemon=True).start()
        run_frontend_command('npm start')
    elif choice1 == "3":
        run_frontend_command('electron .')
    elif choice1 == "4":
        run_frontend_command('npm run electron:build && open dist')


