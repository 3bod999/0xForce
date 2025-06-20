# 0xForce - Fast Injection Tool

![0xForce Banner](./22469fcc-5a14-4e92-9fa7-c308a752f22c.png)

> Tool by **abdlurhman** aka **0xsilver**

---

## ✅ What It Does

* Fast injection tests
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
