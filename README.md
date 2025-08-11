# fileuploadscanner

## About

I created this scanner to simplify file upload vulnerability scanning. The idea was to create a scanner that able to brute-forces file extensions, content-types, and contents. It also supports Headers parameter so you can impersonate after the login phase and proxy for further analysis using burpsuite.

```
Extension		Content-Type		File Content (magic)
---------		------------		--------------------
.png.php 		image/png  			%PDF-
.php.png 		image/jpeg 			PNG IHDR
.php.svg 		image/svg 			...
.php%00.png 	...
...
```

## Usage

```bash
> python .\fileuploadscanner.py -h
usage: fileuploadscanner.py [-h] --url URL --field FIELD --wordlist WORDLIST --magic-list MAGIC_LIST
                            [--guess-template GUESS_TEMPLATE] [--headers [HEADERS ...]] [--proxy PROXY] [--concurrency CONCURRENCY]

File Upload Vulnerability Scanner

options:
  -h, --help            show this help message and exit
  --url URL             Upload endpoint URL
  --field FIELD         Form field name for file upload
  --wordlist WORDLIST   Path to wordlist of filenames/extensions
  --magic-list MAGIC_LIST
                        Magic headers or file paths list
  --guess-template GUESS_TEMPLATE
                        URL template for guessing uploaded file location (optional)
  --headers [HEADERS ...]
                        Custom headers: 'Header: Value'
  --proxy PROXY         Proxy URL (e.g., http://127.0.0.1:8080)
  --concurrency CONCURRENCY
                        Number of concurrent uploads
```

```bash
python upload_scanner.py \
    --url https://target.com/upload \
    --field file \
    --wordlist wordlist.txt \
    --magic-list magic-list.txt \
    --headers "Cookie: SESSION=abc123" \
    --proxy http://127.0.0.1:8080 \
    --guess-template "https://target.com/directory/{filename}"
```