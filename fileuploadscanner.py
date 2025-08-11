import aiohttp
import asyncio
import argparse
import random
import string
import os

# Generate random token
def rand_token(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

async def try_upload(session, url, field, filename, payload_bytes, content_type, headers, proxy):
    data = aiohttp.FormData()
    data.add_field(field, payload_bytes, filename=filename, content_type=content_type)

    async with session.post(url, data=data, headers=headers, proxy=proxy) as resp:
        text = await resp.text()
        print(f"[UPLOAD] {filename} ({content_type}) -> {resp.status}")
        return resp.status, text

async def probe_url(session, guess_url, headers, proxy):
    async with session.get(guess_url, headers=headers, proxy=proxy) as resp:
        print(f"[PROBE] {guess_url} -> {resp.status}")
        return resp.status

async def worker(queue, args, magics, exts, content_types):
    async with aiohttp.ClientSession() as session:
        while not queue.empty():
            fname, magic_name, payload_bytes, ct, token = await queue.get()

            # Upload attempt
            await try_upload(session, args.url, args.field, fname, payload_bytes, ct, args.header_dict, args.proxy)

            # Optional guessing
            if args.guess_template:
                guessed_url = args.guess_template.format(filename=os.path.basename(fname))
                await probe_url(session, guessed_url, args.header_dict, args.proxy)

            queue.task_done()

async def main_async(args):
    # Load headers
    args.header_dict = {}
    if args.headers:
        for h in args.headers:
            k, v = h.split(":", 1)
            args.header_dict[k.strip()] = v.strip()

    # Load wordlist
    with open(args.wordlist, "r", encoding="utf-8") as f:
        exts = [line.strip() for line in f if line.strip()]

    # Load magic payloads
    magics = {}
    with open(args.magic_list, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                name, path = line.strip().split(":", 1)
                if os.path.isfile(path):
                    with open(path, "rb") as pf:
                        magics[name] = pf.read()
                else:
                    magics[name] = bytes.fromhex(path.strip())

    # Content types
    content_types = [
        "image/jpg",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/svg+xml"
    ]

    # Prepare jobs
    queue = asyncio.Queue()
    for pattern in exts:
        token = rand_token()
        fname = pattern.replace("{token}", token) if "{token}" in pattern else pattern
        for mname, mbytes in magics.items():
            for ct in content_types:
                await queue.put((fname, mname, mbytes, ct, token))

    # Workers
    workers = [asyncio.create_task(worker(queue, args, magics, exts, content_types)) for _ in range(args.concurrency)]
    await queue.join()
    for w in workers:
        w.cancel()

def main():
    parser = argparse.ArgumentParser(description="File Upload Vulnerability Scanner")
    parser.add_argument("--url", required=True, help="Upload endpoint URL")
    parser.add_argument("--field", required=True, help="Form field name for file upload")
    parser.add_argument("--wordlist", required=True, help="Path to wordlist of filenames/extensions")
    parser.add_argument("--magic-list", required=True, help="Magic headers or file paths list")
    parser.add_argument("--guess-template", help="URL template for guessing uploaded file location (optional)", required=False)
    parser.add_argument("--headers", nargs="*", help="Custom headers: 'Header: Value'")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent uploads")
    args = parser.parse_args()

    asyncio.run(main_async(args))

if __name__ == "__main__":
    main()
