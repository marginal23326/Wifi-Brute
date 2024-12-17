# WiFi-Brute

WiFi-Brute is a WiFi password cracking tool designed for educational purposes. It uses a wordlist-based approach to attempt cracking WiFi passwords, providing real-time progress updates and ETA.

## Features

- 🔍 Scans for available WiFi networks
- 📊 Displays network information in a formatted table 
- 🔐 Attempts to crack WiFi passwords using a provided wordlist
- ⏱️ Real-time progress tracking with ETA
- ⏯️ Pause/Resume functionality
- 🛑 Ability to stop cracking at any time
- 🎨 Colorful and informative console output
- 💾 Saves cracked and attempted passwords for future reference

## Prerequisites

- Windows operating system
- Python 3.10+

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/marginal23326/Wifi-Brute
   ```

2. Navigate to the Wifi-Brute directory:
   ```
   cd Wifi-Brute
   ```

## Usage

Run the script with the following command:

```
python wifi-brute.py [-h] [-w WORDLIST] [-t TIMEOUT]
```

### Command-line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-h`, `--help` | Show help message | - |
| `-w WORDLIST`, `--wordlist WORDLIST` | Path to the wordlist file | `probable-v2-wpa-top4800.txt` |
| `-t TIMEOUT`, `--timeout TIMEOUT` | Timeout for each connection attempt | 5 seconds |

### Example Usage

1. Use the default wordlist:
   ```
   python wifi-brute.py
   ```

2. Specify a custom wordlist:
   ```
   python wifi-brute.py -w my_wordlist.txt
   ```

3. Set a custom timeout:
   ```
   python wifi-brute.py -t 3
   ```
   **Note**: Set the timeout to at least 3 seconds to allow enough time for each cracking attempt.

4. Use a custom wordlist and timeout:
   ```
   python wifi-brute.py -w my_wordlist.txt -t 7
   ```
   **Note**: A longer timeout will give more time per attempt but will increase the total time to try all passwords.

## Interactive Commands

During the cracking process, you can use the following keyboard commands:

- Press `p` to pause or unpause the cracking process
- Press `q` to stop cracking and rescan or exit the program

## Output Files

The script logs attempts into two separate files to avoid repetition:

1. `cracked_passwords.txt`: Contains successfully cracked WiFi passwords
2. `attempted_passwords.txt`: Records all attempted passwords for each network

## Disclaimer

This tool is intended for educational purposes only. Unauthorized access to networks is illegal. Use this tool only on networks you own or have explicit permission to test. I am not responsible for any misuse or damage caused by this program.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
