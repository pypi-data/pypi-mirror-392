class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def log(message: str, color: str = Colors.ENDC):
    print(f"{color}{message}{Colors.ENDC}")


def error(message: str, exit_app: bool = True):
    log(f"===  ERREUR  ===\n{message}", Colors.FAIL)
    if exit_app:
        exit(-1)


def warning(message: str):
    log(f"===  AVERTISSEMENT  ===\n{message}", Colors.WARNING)


def yes_or_no(prompt: str) -> bool:
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Veuillez répondre par 'y' ou 'n'.")
