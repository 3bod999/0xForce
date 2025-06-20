# Fast Parallel Brute-force Tool

![image](https://github.com/user-attachments/assets/f85ea2e2-de2a-4897-bf72-f86aa951a635)


> Tool by **abdlurhman** aka **0xsilver**

---

## ✅ What It Does

* Uses placeholders like 0x1, 0x2, etc.
* Brute-force using wordlists
* Uses placeholders like `0x1`, `0x2`, etc.
* Shows clean results in panels
* Supports proxies and filters
* Saves output if needed

---

## 🧰 How To Use

```bash
python3 0xforce.py -u "https://target.com/login?user=0x1" --w1 users.txt
```

### Main Options

| Option      | What it means                          |
| ----------- | -------------------------------------- |
| `-u`        | URL to test (must include `0x1`, etc.) |
| `--w1`      | Wordlist for `0x1`                     |
| `--method`  | GET or POST (default: GET)             |
| `--header`  | Add headers like `Auth: 0x1`           |
| `--proxy`   | Use one proxy                          |
| `--proxies` | Use list of proxies                    |
| `--output`  | Save results to a file                 |
| `--threads` | Set number of threads (default: 10)    |
| `--fstatus` | Filter out unwanted status codes       |
| `--flength` | Filter by response size                |

---

## 🔍 Example

```bash
python3 0xforce.py \
  -u "https://site.com/page.php?id=0x1" \
  --w1 ids.txt \
  --fstatus 404 \
  --output found.txt
```

---

## 🖼️ Screenshot

Below is an example output of 0xForce when a valid result is found:
![image](https://github.com/user-attachments/assets/363bc1c3-0ab1-4e5e-b3eb-491b9a4e7893)


---

## 📦 Wordlists

Use simple `.txt` files, one word per line.

Supports placeholders:

* `0x1`, `0x2`, `0x3`, `0x4`

---

## 🌐 Proxy Use

```bash
--proxy http://127.0.0.1:8080
--proxies proxies.txt
```

---

## 💾 Install

```bash
pip install requests rich
```

---

## 👤 Author

Made with ❤️ by **abdlurhman** aka **0xsilver**
For learning & research only.

---
