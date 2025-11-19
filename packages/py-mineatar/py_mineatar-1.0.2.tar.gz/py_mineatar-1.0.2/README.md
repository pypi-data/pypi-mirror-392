# py-mineatar
[![Tests](https://github.com/rzn1r/py-mineatar/actions/workflows/test.yml/badge.svg)](https://github.com/rzn1r/py-mineatar/actions/workflows/test.yml)
[![Ruff Lint](https://github.com/rzn1r/py-mineatar/actions/workflows/lint.yml/badge.svg)](https://github.com/rzn1r/py-mineatar/actions/workflows/lint.yml)
![PyPI - Version](https://img.shields.io/pypi/v/py-mineatar)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-mineatar)
![License](https://img.shields.io/github/license/rzn1r/py-mineatar)

A Python wrapper for mineatar.io

## Installation
You can install the package via pip:

```bash
pip install py-mineatar
```

## Usage
Here's an example of how to use the `py-mineatar` package:

### Synchronous Example

```python
from mineatar import MineatarClient

with MineatarClient() as client:
    avatar_bytes = client.get_skin("069a79f4-44e9-4726-a5be-fca90e38aaf5") # Notch's UUID

    # Save the avatar image
    with open("notch_skin.png", "wb") as f:
        f.write(avatar_bytes)
```

### Asynchronous Example

```python
import asyncio
from mineatar import AsyncMineatarClient

async def main():
    async with AsyncMineatarClient() as client:
        avatar_bytes = await client.get_skin("069a79f4-44e9-4726-a5be-fca90e38aaf5") # Notch's UUID

        # Save the avatar image
        with open("notch_skin.png", "wb") as f:
            f.write(avatar_bytes)

asyncio.run(main())
```

## Features
- Fast and easy access to Minecraft avatars and skins.
- Supports both synchronous and asynchronous operations.
- Simple and easy-to-use.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.
