# Import required modules
import argparse
import requests
import threading
import json as json_lib
import signal
import os
from itertools import product, cycle
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
import urllib3

# Disable SSL warnings (useful when working with self-signed certificates or unverified HTTPS)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup rich console for colorful CLI output
console = Console()

# Global control flags and shared data
stop_flag = False
completed_payloads = set()
lock = threading.Lock()
proxy_cycle = None

# Handle CTRL+C interrupt to safely stop the tool
def signal_handler(sig, frame):
    global stop_flag
    console.print("\n[bold red][!] Stopping...[/bold red]")
    stop_flag = True

signal.signal(signal.SIGINT, signal_handler)

# Load wordlist from a file
def load_wordlist(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

# Load proxy list from file or inline string
def load_proxy_list(proxies_arg):
    if os.path.isfile(proxies_arg):
        with open(proxies_arg, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    return [proxy.strip() for proxy in proxies_arg.split(',') if proxy.strip()]

# Check if a proxy is working by making a request to httpbin.org
def test_proxy(proxy):
    try:
        proxies = {"http": proxy, "https": proxy}
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5, verify=False)
        return r.status_code == 200
    except Exception:
        return False

# Get the next working proxy from the list
def get_working_proxy(proxy_iter):
    while True:
        try:
            proxy = next(proxy_iter)
            if test_proxy(proxy):
                return proxy
        except StopIteration:
            return None
        except Exception:
            continue

# Divide a list into roughly equal chunks for thread splitting
def chunk_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

# Generate combinations of payloads depending on how many wordlists are provided
def split_combinations_by_wordlist(wlists):
    if len(wlists) == 1:
        return [[(w, "0x2", "0x3", "0x4")] for w in wlists[0]]
    elif len(wlists) == 2:
        return [[(w1, w2, "0x3", "0x4")] for w1 in wlists[0] for w2 in wlists[1]]
    elif len(wlists) == 3:
        return [[(w1, w2, w3, "0x4")] for w1 in wlists[0] for w2 in wlists[1] for w3 in wlists[2]]
    else:
        return list(product(*wlists))

# Decide whether to skip the response based on status code or content length
def should_filter(response, args):
    if args.fstatus and str(response.status_code) in args.fstatus:
        return True
    if args.flength and len(response.text) in args.flength:
        return True
    return False

# Replace placeholders (e.g., 0x1, 0x2...) in text with payload values
def inject_payloads(text, payloads):
    if not text:
        return None
    for i, payload in enumerate(payloads):
        text = text.replace(f"0x{i + 1}", payload)
    return text

# Display formatted response information
def display_result(response, url, part_id):
    status_code = response.status_code
    length = len(response.text)

    # Assign color and icon based on status code
    if status_code >= 500:
        color, icon = "red", "❌"
    elif status_code >= 400:
        color, icon = "yellow", "⚠️"
    elif status_code >= 300:
        color, icon = "cyan", "➡️"
    else:
        color, icon = "green", "✅"

    content = f"""
[bold]🧪 Part {part_id}[/bold]
[bold]Status:[/] [{color}]{status_code}[/] {icon}
[bold]Length:[/] {length} bytes
[bold]URL:[/] [cyan]{url}[/cyan]
"""
    console.print(Panel(content.strip(), border_style=color, title="🛡️ 0xForce 🛡️", expand=False))

# Function that performs a single injection attempt
def worker(args, payloads, progress=None, task_id=None, part_id=None):
    global completed_payloads, proxy_cycle
    if stop_flag:
        return

    proxy = get_working_proxy(proxy_cycle) if proxy_cycle else None

    # Inject payloads into URL, body, JSON
    url = inject_payloads(args.url, payloads)
    data = inject_payloads(args.body, payloads)
    json_data = inject_payloads(args.json, payloads)

    # Prepare headers
    headers = {}
    if args.header:
        for h in args.header:
            key, val = h.split(":", 1)
            headers[key.strip()] = inject_payloads(val.strip(), payloads)

    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = requests.request(
            method=args.method.upper(),
            url=url,
            headers=headers,
            data=data,
            json=json_lib.loads(json_data) if json_data else None,
            proxies=proxies,
            timeout=10,
            verify=False
        )

        # Display response if it passes filters
        if not should_filter(response, args):
            display_result(response, url, part_id)
            if args.output:
                with threading.Lock():
                    with open(args.output, 'a') as out:
                        out.write(f"Part {part_id} | {response.status_code} | {len(response.text)} | {url}\n")

    except Exception:
        pass
    finally:
        if progress:
            progress.update(task_id, advance=1)

# Run attack logic for a chunk of payload combinations
def start_attacks(args, combos, part_id):
    if not combos:
        console.print(f"[ Part {part_id} - 0 combinations | Skipped ]", style="bold yellow")
        return

    threads = []
    console.print(f"[bold magenta]\n[ Part {part_id} - {len(combos)} combinations ][/bold magenta]")

    # Show live progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task_id = progress.add_task(f"Part {part_id} - Running 0xForce...", total=len(combos))

        for payloads in combos:
            if stop_flag:
                break
            while threading.active_count() > args.threads:
                pass  # Wait if too many threads
            t = threading.Thread(target=worker, args=(args, payloads, progress, task_id, part_id))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

# Entry point: parse arguments and kick off the attack
def main():
    parser = argparse.ArgumentParser(description="0xForce - Fast Injection Testing Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL with 0x placeholders")
    parser.add_argument("--body", help="Body with 0x placeholders")
    parser.add_argument("--json", help="JSON with 0x placeholders")
    parser.add_argument("--method", default="GET", help="HTTP method (GET/POST)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use")
    parser.add_argument("--header", action='append', help="Custom headers like 'Key: 0x1'")
    parser.add_argument("--w1")  # Wordlist 1
    parser.add_argument("--w2")  # Wordlist 2
    parser.add_argument("--w3")  # Wordlist 3
    parser.add_argument("--w4")  # Wordlist 4
    parser.add_argument("--fstatus", nargs='+', help="Filter by response status code")
    parser.add_argument("--flength", type=int, nargs='+', help="Filter by response length")
    parser.add_argument("--proxy", help="Single proxy for all requests")
    parser.add_argument("--proxies", help="Proxy list file or comma-separated proxies")
    parser.add_argument("--output", help="Write matching results to file")
    parser.add_argument("--split", type=int, default=1, help="Split work into N parts")
    args = parser.parse_args()

    global completed_payloads, proxy_cycle
    completed_payloads = set()

    # Load proxies
    if args.proxies:
        proxy_list = load_proxy_list(args.proxies)
        proxy_cycle = cycle(proxy_list)

    # Load wordlists
    w1 = load_wordlist(args.w1) if args.w1 else ["0x1"]
    w2 = load_wordlist(args.w2) if args.w2 else ["0x2"]
    w3 = load_wordlist(args.w3) if args.w3 else ["0x3"]
    w4 = load_wordlist(args.w4) if args.w4 else ["0x4"]

    # Generate all combinations and divide the work
    all_combos = split_combinations_by_wordlist([w1, w2, w3, w4])
    combo_parts = chunk_list(all_combos, max(1, args.split))

    # Start testing each chunk of combinations
    for idx, combo_chunk in enumerate(combo_parts, 1):
        if stop_flag:
            break
        start_attacks(args, combo_chunk, idx)

# Run main if script is executed directly
if __name__ == '__main__':
    main()
