import os, re, sys, time, shutil, platform, msvcrt
from typing import Tuple
from colorama import Fore, Style
from tqdm import tqdm

class Colors:
    GREEN = Style.BRIGHT + Fore.GREEN
    CYAN = Style.BRIGHT + Fore.CYAN
    YELLOW = Style.BRIGHT + Fore.YELLOW
    RED = Style.BRIGHT + Fore.RED
    MAGENTA = Style.BRIGHT + Fore.MAGENTA
    BLUE = Style.BRIGHT + Fore.BLUE

LOGO = """
████████                                          ████████
██            ██╗    ██╗██╗      ███████╗██╗            ██
██            ██║    ██║██║      ██╔════╝██║            ██
██            ██║ █╗ ██║██║█████╗█████╗  ██║            ██
██            ██║███╗██║██║╚════╝██╔══╝  ██║            ██
██            ╚███╔███╔╝██║      ██║     ██║            ██
██                                                      ██
██      ██████╗ ██████╗ ██╗   ██╗████████╗███████╗      ██
██      ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝      ██
██      ██████╔╝██████╔╝██║   ██║   ██║   █████╗        ██
██      ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝        ██
██      ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗      ██
██      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝      ██
████████                                          ████████
"""

def get_terminal_size() -> Tuple[int, int]:
    return shutil.get_terminal_size()

def truncate_line(line, width):
    return line[:width - 3] + '...' if len(line) > width else line

def center_text(text: str) -> str:
    return '\n'.join([line.center(get_terminal_size()[0]) for line in text.split('\n')])

def banner(show_logo: bool = False):
    if show_logo:
        gradient_print(center_text(LOGO), start_color='magenta', end_color='yellow')
    gradient_print(center_text("WiFi Brute Force Tool"), start_color='cyan', end_color='magenta')

def clear():
    os.system("cls" if platform.system() == "Windows" else "clear")

def sprint(text: str, start_color: str = 'cyan', end_color: str = 'yellow', delay: float = 0.001):
    for char in gradient_string(text, start_color, end_color):
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_header(text: str, start_color: str = 'yellow', end_color: str = 'magenta'):
    terminal_width = get_terminal_size()[0]
    gradient_print('=' * terminal_width, start_color, end_color)
    gradient_print(center_text(text), start_color, end_color)
    gradient_print('=' * terminal_width, start_color, end_color)

def get_input(prompt: str, color: str = 'green') -> str:
    return input(f"{gradient_string(prompt, color, 'yellow')}")

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def name_to_rgb(color_name):
    color_dict = {
        'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
        'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255),
        'white': (255, 255, 255), 'black': (0, 0, 0)
    }
    return color_dict.get(color_name.lower(), (255, 255, 255))

def parse_color(color):
    if isinstance(color, tuple) and len(color) == 3:
        return color
    if isinstance(color, str):
        if color.startswith('#'):
            return hex_to_rgb(color)
        elif re.match(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', color):
            return tuple(map(int, re.findall(r'\d+', color)))
        else:
            return name_to_rgb(color)
    raise ValueError("Invalid color format")

def gradient_string(text: str, start_color: str = 'cyan', end_color: str = 'yellow') -> str:
    start_rgb = parse_color(start_color)
    end_rgb = parse_color(end_color)
    
    parts = re.split(r'(\033\[[0-9;]*[a-zA-Z])', text)
    
    gradient_text = ''
    visible_char_count = sum(len(part) for part in parts if not part.startswith('\033'))
    current_char = 0
    
    for part in parts:
        if part.startswith('\033'):
            gradient_text += part
        else:
            for char in part:
                r = start_rgb[0] + int((end_rgb[0] - start_rgb[0]) * (current_char / visible_char_count))
                g = start_rgb[1] + int((end_rgb[1] - start_rgb[1]) * (current_char / visible_char_count))
                b = start_rgb[2] + int((end_rgb[2] - start_rgb[2]) * (current_char / visible_char_count))
                color = f'\033[38;2;{r};{g};{b}m'
                gradient_text += f'{color}{char}'
                current_char += 1
    
    return gradient_text + '\033[0m'

def gradient_print(text: str, start_color: str = 'cyan', end_color: str = 'yellow'):
    print(gradient_string(text, start_color, end_color))

def print_table(headers: list[str], rows: list[list[str]]):
    col_widths = [max(len(str(x)) for x in col) for col in zip(*rows, headers)]
    header = ' | '.join(f'{h:<{w}}' for h, w in zip(headers, col_widths))
    separator = '-+-'.join('-' * w for w in col_widths)
    
    gradient_print(header, 'cyan', 'blue')
    gradient_print(separator, 'yellow', 'magenta')
    
    for row in rows:
        formatted_row = ' | '.join(f'{str(c):<{w}}' for c, w in zip(row, col_widths))
        sprint(formatted_row, start_color='green', end_color='cyan', delay=0.000001)

def print_status(message: str, status: str, success: bool = True, start_color: str = "cyan", end_color: str = "yellow"):
    start_color = "green" if success else "red"
    full_message = f"\n\n\n[{status}] {message}"
    gradient_print(full_message, start_color, end_color)

def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', decimals: int = 2, fill: str = '█', print_end: str = "\r"):
    percent = f"{100 * (iteration / float(total)):.{decimals}f}%"
    length = get_terminal_size()[0] - len(f"{prefix} {percent} | | {iteration}/{total}")
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    terminal_width = get_terminal_size()[0]

    print(f'\r{gradient_string(truncate_line(f'{prefix} {percent} |{bar}| {iteration}/{total}', terminal_width) + "\033[1B", 'cyan', 'magenta')}', end=print_end)
    print(f'\r{gradient_string(truncate_line(suffix, terminal_width) + "\033[1A", 'cyan', 'magenta')}', end=print_end)
    
    if iteration == total:
        print()

def print_menu(title: str, options: list[str]):
    print_header(title, 'cyan', 'magenta')
    for i, option in enumerate(options, 1):
        gradient_print(f"{i}. {option}", 'yellow', 'green')
    print()

def confirm_action(message: str) -> bool:
    while True:
        while msvcrt.kbhit():
            msvcrt.getch()
        response = get_input(f"\n{message} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            gradient_print("Invalid input. Please enter 'y' or 'n'.", 'red', 'yellow')