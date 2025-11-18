
````markdown
# ytq

`ytq` is a lightweight and fast Python library for searching YouTube videos using the official MWeb API.  
It supports both synchronous and asynchronous usage, making it suitable for scripts, bots, and larger applications.

---

## Features

- Simple and fast YouTube search
- Asynchronous and synchronous support
- Returns structured JSON results
- Includes video title, ID, URL, and thumbnail
- Supports result limiting (`limit` parameter)
- Works without any API keys

---

## Installation

You can install `ytq` from PyPI (after publishing):

```bash
pip install ytq
````

Or from source:

```bash
git clone https://github.com/ahmeddreas/ytq.git
cd ytq
pip install .
```

---

## Example Usage

### Synchronous

```python
from ytq import search

results = search("lofi music", limit=5)

for video in results:
    print(video["title"], video["url"])
```

### Asynchronous

```python
import asyncio
from ytq import asearch

async def main():
    results = await asearch("python tutorials", limit=3)
    print(results[0]["title"], results[0]["url"])

asyncio.run(main())
```

---

## Parameters

| Parameter    | Type            | Description                                                            |
| ------------ | --------------- | ---------------------------------------------------------------------- |
| `query`      | `str`           | The search query (e.g., "python programming")                          |
| `limit`      | `int` or `None` | Number of results to return. If `None`, returns all available results. |
| `auto_print` | `bool`          | If `True`, prints formatted results to console. Default is `True`.     |

---

## Returned JSON Structure

Each search result is a dictionary with the following keys:

```python
{
  "video_id": "abcd1234",
  "title": "Example video title",
  "url": "https://m.youtube.com/watch?v=abcd1234",
  "thumbnail": "https://i.ytimg.com/vi/abcd1234/hqdefault.jpg"
}
```

---

## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for more details.

---

## Author

**Ahmed D. Ismail**
GitHub: [Ahmed d. Ismail](https://github.com/valhalla803)