# BlakPort

<div align="center">

**Fast, lightweight FastAPI wrapper for exposing Ollama server to your local network**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

</div>

## Overview

BlakPort is a lightweight API gateway that exposes your local Ollama server to devices on your local network. It provides a simple REST API wrapper around Ollama, making it easy to access your LLM models from any device on your LAN.

## Installation

### From PyPI

```bash
pip install blakport
```

### From Source

```bash
git clone https://github.com/yourusername/blakport.git
cd blakport
pip install -e .
```

## CLI Commands

### `blakport start`

Start the BlakPort server.

```bash
blakport start                    # Foreground (auto-moves to background)
blakport start --background       # Background immediately
blakport start --host 192.168.1.100 --port 11435  # Override Ollama config
```

### `blakport stop`

Stop the running server.

```bash
blakport stop
```

### `blakport status`

Show server status.

```bash
blakport status
```

### `blakport log`

View server logs.

```bash
blakport log              # Last 50 lines
blakport log --lines 100  # Last 100 lines
blakport log --follow     # Follow logs (tail -f)
```

### `blakport init` / `blakport configure`

Initialize or update configuration.

```bash
blakport init                          # Interactive setup
blakport init --host 127.0.0.1 --port 11434
blakport configure --host 192.168.1.100
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ in London

</div>
