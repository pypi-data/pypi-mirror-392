# aiocache-pro

**Fastest cache for production**:

- LRU / MRU / LFU / TTL caching strategies  
- Works with **gevent**  
- Custom keys support  
- Optimized with **C / Cython** for speed  

---

## Features

- **LRU (Least Recently Used)** – automatically removes least recently used items when maxsize is reached.  
- **MRU (Most Recently Used)** – removes most recently used items first.  
- **LFU (Least Frequently Used)** – removes items with the lowest access count.  
- **TTL (Time To Live)** – items expire automatically after a given time.  
- **Custom keys** – generate keys from function arguments.  
- **C optimization** – speed improvements via Cython.

---

## Installation

You can install from you:

```bash
pip install aiocache_pro
