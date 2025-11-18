"""
BlakPort - FastAPI wrapper for Ollama server
Exposes Ollama API to local network with optional security
"""

import os
import sys
import signal
import subprocess
import time
import socket
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import logging
import click
from platformdirs import user_config_dir

# TOML support - Python 3.11+ has tomllib built-in
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python < 3.11
    except ImportError:
        tomllib = None

# Version
__version__ = "1.0.0"

# Paths
PID_FILE = Path.home() / ".blakport" / "blakport.pid"
LOG_FILE = Path.home() / ".blakport" / "blakport.log"
PID_DIR = PID_FILE.parent
CONFIG_DIR = Path(user_config_dir("blakport"))
CONFIG_FILE = CONFIG_DIR / "config.toml"

# Ensure directories exist
PID_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration Management
class Config:
    """Configuration manager with priority: CLI > ENV > Config file > Defaults"""
    
    DEFAULTS = {
        "host": "127.0.0.1",
        "port": 11434,
        "provider": "ollama",
    }
    
    def __init__(self, cli_overrides: Optional[Dict[str, Any]] = None):
        self.cli_overrides = cli_overrides or {}
        self._config_data = self._load_config_file()
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        if not CONFIG_FILE.exists():
            return {}
        
        if tomllib is None:
            logger.warning("TOML support not available. Install tomli for Python < 3.11")
            return {}
        
        try:
            with open(CONFIG_FILE, "rb") as f:
                data = tomllib.load(f)
                # Support both flat and nested [ollama] section
                if "ollama" in data:
                    return data["ollama"]
                return data
        except Exception as e:
            logger.warning(f"Error loading config file {CONFIG_FILE}: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with priority: CLI > ENV > Config file > Defaults"""
        # 1. CLI overrides (highest priority)
        if key in self.cli_overrides:
            return self.cli_overrides[key]
        
        # 2. Environment variables
        env_key = f"OLLAMA_{key.upper()}" if key in ["host", "port"] else key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            if key == "port":
                return int(env_value)
            return env_value
        
        # 3. Config file
        if self._config_data and key in self._config_data:
            value = self._config_data[key]
            if key == "port" and isinstance(value, str):
                return int(value)
            return value
        
        # 4. Defaults
        return self.DEFAULTS.get(key, default)
    
    def save_config_file(self, config_data: Dict[str, Any]):
        """Save configuration to TOML file"""
        # Merge with existing config
        existing = self._load_config_file()
        existing.update(config_data)
        
        # Write TOML file manually (simpler than adding tomli-w dependency)
        with open(CONFIG_FILE, "w") as f:
            f.write("# BlakPort Configuration\n")
            f.write("# This file is managed by 'blakport init' or 'blakport configure'\n\n")
            f.write("[ollama]\n")
            f.write(f'host = "{existing.get("host", self.DEFAULTS["host"])}"\n')
            f.write(f'port = {existing.get("port", self.DEFAULTS["port"])}\n')
            f.write(f'provider = "{existing.get("provider", self.DEFAULTS["provider"])}"\n')
        
        # Note: Success message is shown by the calling function


# Global config instance (will be initialized with CLI overrides when needed)
_config: Optional[Config] = None


def get_config(cli_overrides: Optional[Dict[str, Any]] = None) -> Config:
    """Get or create configuration instance"""
    global _config
    if _config is None or cli_overrides:
        _config = Config(cli_overrides)
    return _config


# Security (still from env vars for now)
API_KEY = os.getenv("API_KEY", None)  # Set API_KEY env var to enable auth
REQUIRE_API_KEY = API_KEY is not None


# Colorful CLI styling helpers
def style_success(text: str) -> str:
    """Style success messages"""
    return click.style(text, fg="green", bold=True)


def style_error(text: str) -> str:
    """Style error messages"""
    return click.style(text, fg="red", bold=True)


def style_warning(text: str) -> str:
    """Style warning messages"""
    return click.style(text, fg="yellow", bold=True)


def style_info(text: str) -> str:
    """Style info messages"""
    return click.style(text, fg="blue", bold=True)


def style_highlight(text: str) -> str:
    """Style highlighted text"""
    return click.style(text, fg="cyan", bold=True)


def style_dim(text: str) -> str:
    """Style dimmed text"""
    return click.style(text, dim=True)


def style_label(text: str) -> str:
    """Style labels"""
    return click.style(text, fg="white", bold=True)


def get_ollama_base_url(config_instance: Optional[Config] = None) -> str:
    """Get Ollama base URL from config"""
    if config_instance is None:
        config_instance = get_config()
    host = config_instance.get("host")
    port = config_instance.get("port")
    return f"http://{host}:{port}"

app = FastAPI(
    title="BlakPort - Ollama API Gateway",
    description="Lightweight FastAPI wrapper for Ollama server",
    version=__version__
)

# CORS middleware - allow LAN access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to LAN subnets
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for API key authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if REQUIRE_API_KEY:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


# Pydantic models
class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: Optional[bool] = False
    options: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    ollama_available: bool
    ollama_url: str


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - verifies Ollama server availability"""
    config_instance = get_config()
    ollama_url = get_ollama_base_url(config_instance)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to connect to Ollama
            response = await client.get(f"{ollama_url}/api/tags")
            ollama_available = response.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        ollama_available = False
    
    return HealthResponse(
        status="ok",
        ollama_available=ollama_available,
        ollama_url=ollama_url
    )


@app.get("/api/tags")
async def list_models(_: bool = Depends(verify_api_key)):
    """List available Ollama models"""
    config_instance = get_config()
    ollama_url = get_ollama_base_url(config_instance)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama server timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama server")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate(request: GenerateRequest, _: bool = Depends(verify_api_key)):
    """Generate text using Ollama"""
    config_instance = get_config()
    ollama_url = get_ollama_base_url(config_instance)
    
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": request.stream,
    }
    if request.options:
        payload["options"] = request.options
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            if request.stream:
                # Stream response - Ollama returns JSON lines
                async with client.stream(
                    "POST",
                    f"{ollama_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async def generate_stream():
                        async for line in response.aiter_lines():
                            if line:
                                yield line + "\n"
                    
                    return StreamingResponse(
                        generate_stream(),
                        media_type="application/x-ndjson"
                    )
            else:
                # Regular response
                response = await client.post(
                    f"{ollama_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Generation timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama server")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information"""
    config_instance = get_config()
    ollama_url = get_ollama_base_url(config_instance)
    
    return {
        "service": "BlakPort",
        "version": __version__,
        "ollama_url": ollama_url,
        "endpoints": {
            "health": "/api/health",
            "list_models": "/api/tags",
            "generate": "/api/generate"
        },
        "authentication": "required" if REQUIRE_API_KEY else "disabled"
    }


def is_port_listening(host: str, port: int, timeout: float = 0.1) -> bool:
    """Check if a port is listening"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host if host != "0.0.0.0" else "127.0.0.1", port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_server(background: bool = False, cli_overrides: Optional[Dict[str, Any]] = None):
    """Start BlakPort server"""
    import uvicorn
    
    # Update config with CLI overrides
    config_instance = get_config(cli_overrides)
    ollama_url = get_ollama_base_url(config_instance)
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")  # Listen on all interfaces for LAN access
    
    if background:
        # Start in background immediately
        log_file = open(LOG_FILE, "a")
        
        # Use uvicorn command - works when installed as package
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", host, "--port", str(port)]
        
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True
        )
        
        # Save PID
        PID_FILE.write_text(str(process.pid))
        click.echo(style_success("✓ BlakPort started in background"))
        click.echo(f"  {style_label('PID:')} {style_highlight(str(process.pid))}")
        click.echo(f"  {style_label('Ollama:')} {style_highlight(ollama_url)}")
        click.echo(f"  {style_label('Logs:')} {style_dim(str(LOG_FILE))}")
        log_file.close()
    else:
        # Start in foreground, show logs, then move to background when ready
        click.echo(style_info("🚀 Starting BlakPort server..."))
        click.echo(f"  {style_label('Ollama:')} {style_highlight(ollama_url)}")
        auth_status = style_success("enabled") if REQUIRE_API_KEY else style_dim("disabled")
        click.echo(f"  {style_label('Auth:')} {auth_status}")
        click.echo("")
        
        # Open log file for writing
        log_file = open(LOG_FILE, "a")
        
        # Start uvicorn in subprocess
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", host, "--port", str(port)]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read logs and display until server is ready
        server_ready = False
        max_wait_time = 30  # Maximum seconds to wait
        start_time = time.time()
        
        click.echo(style_info("⏳ Waiting for server to start..."), nl=False)
        
        # Read output line by line
        output_lines = []
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                click.echo("")  # New line after waiting message
                click.echo(style_error(f"✗ Timeout waiting for server to start after {max_wait_time} seconds"))
                process.terminate()
                log_file.close()
                sys.exit(1)
            
            # Check if process died
            if process.poll() is not None:
                click.echo("")  # New line after waiting message
                click.echo(style_error("✗ Server process exited unexpectedly"))
                # Read remaining output
                remaining = process.stdout.read()
                if remaining:
                    click.echo(remaining, err=True)
                    log_file.write(remaining)
                log_file.close()
                sys.exit(1)
            
            # Check if port is listening
            if is_port_listening(host, port):
                if not server_ready:
                    server_ready = True
                    # Give it a moment to fully initialize
                    time.sleep(0.5)
                    break
            
            # Try to read a line
            try:
                line = process.stdout.readline()
                if line:
                    line_stripped = line.rstrip()
                    output_lines.append(line)
                    log_file.write(line)
                    log_file.flush()
                    
                    # Show startup logs
                    if "Started server process" in line_stripped or "Uvicorn running on" in line_stripped or "Application startup complete" in line_stripped:
                        click.echo("")  # New line after waiting message
                        click.echo(style_success(f"  {line_stripped}"))
                        # Check port again after seeing startup message
                        if is_port_listening(host, port):
                            server_ready = True
                            time.sleep(0.5)
                            break
                    elif "ERROR" in line_stripped or "CRITICAL" in line_stripped:
                        click.echo("")  # New line after waiting message
                        click.echo(style_error(f"  {line_stripped}"))
            except Exception:
                pass
            
            time.sleep(0.1)
        
        # Server is ready, now detach it
        server_url = f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}"
        click.echo("")  # New line after waiting message
        click.echo(style_success(f"✓ Server is ready on {style_highlight(server_url)}"))
        click.echo(style_info("📦 Moving to background..."))
        
        # Save PID - process is already running
        PID_FILE.write_text(str(process.pid))
        
        # Start a thread to continue reading output and writing to log file
        def log_writer():
            try:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        # Process ended
                        break
                    log_file.write(line)
                    log_file.flush()
            except Exception:
                pass
            finally:
                try:
                    log_file.close()
                except Exception:
                    pass
        
        # Start background thread to write logs
        log_thread = threading.Thread(target=log_writer, daemon=True)
        log_thread.start()
        
        click.echo("")
        click.echo(style_success("✓ BlakPort is running in background"))
        click.echo(f"  {style_label('PID:')} {style_highlight(str(process.pid))}")
        click.echo(f"  {style_label('Logs:')} {style_dim(str(LOG_FILE))}")
        click.echo(f"  {style_label('Status:')} {style_dim('blakport status')}")
        click.echo(f"  {style_label('Stop:')} {style_dim('blakport stop')}")


def stop_server():
    """Stop BlakPort server"""
    if not PID_FILE.exists():
        click.echo(style_warning("⚠ BlakPort is not running (PID file not found)"))
        sys.exit(1)
    
    try:
        pid = int(PID_FILE.read_text().strip())
        
        # Check if process exists
        try:
            os.kill(pid, 0)  # Signal 0 just checks if process exists
        except ProcessLookupError:
            click.echo(style_warning(f"⚠ Process {pid} not found (may have crashed)"))
            PID_FILE.unlink()
            sys.exit(1)
        except PermissionError:
            click.echo(style_error(f"✗ Permission denied: Cannot access process {pid}"))
            sys.exit(1)
        
        # Kill the process
        click.echo(style_info("🛑 Stopping BlakPort server..."))
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        click.echo(style_success(f"✓ BlakPort stopped (PID: {pid})"))
    except ValueError:
        click.echo(style_error(f"✗ Invalid PID file: {PID_FILE}"))
        PID_FILE.unlink()
        sys.exit(1)
    except Exception as e:
        click.echo(style_error(f"✗ Error stopping server: {e}"))
        sys.exit(1)


def show_status():
    """Show BlakPort server status"""
    if not PID_FILE.exists():
        click.echo(f"{style_label('Status:')} {style_warning('Not running')}")
        return
    
    try:
        pid = int(PID_FILE.read_text().strip())
        
        # Check if process exists
        try:
            os.kill(pid, 0)
            click.echo(f"{style_label('Status:')} {style_success('Running')}")
            click.echo(f"  {style_label('PID:')} {style_highlight(str(pid))}")
            
            # Try to get port from environment or default
            port = int(os.getenv("PORT", "8000"))
            host = os.getenv("HOST", "0.0.0.0")
            server_url = f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}"
            click.echo(f"  {style_label('URL:')} {style_highlight(server_url)}")
            click.echo(f"  {style_label('Host:')} {style_dim(host)}")
            click.echo(f"  {style_label('Port:')} {style_dim(str(port))}")
            click.echo(f"  {style_label('Logs:')} {style_dim(str(LOG_FILE))}")
        except ProcessLookupError:
            click.echo(f"{style_label('Status:')} {style_warning('Not running (stale PID file)')}")
            PID_FILE.unlink()
        except PermissionError:
            click.echo(f"{style_label('Status:')} {style_warning(f'Unknown (cannot access process {pid})')}")
    except ValueError:
        click.echo(f"{style_label('Status:')} {style_error('Error (invalid PID file)')}")
    except Exception as e:
        click.echo(f"{style_label('Status:')} {style_error(f'Error - {e}')}")


def show_logs(follow: bool = False, lines: int = 50):
    """Show BlakPort server logs"""
    if not LOG_FILE.exists():
        click.echo(style_error(f"✗ Log file not found: {LOG_FILE}"))
        sys.exit(1)
    
    try:
        if follow:
            # Tail -f equivalent
            click.echo(style_info(f"📋 Following logs from {style_highlight(str(LOG_FILE))}"))
            click.echo(style_dim("Press Ctrl+C to stop..."))
            click.echo("")
            try:
                subprocess.run(["tail", "-f", str(LOG_FILE)])
            except KeyboardInterrupt:
                click.echo("")
                click.echo(style_info("✓ Stopped following logs"))
            except FileNotFoundError:
                # Fallback for systems without tail command
                click.echo(style_error("✗ tail command not found. Use --no-follow to view logs."))
                sys.exit(1)
        else:
            # Show last N lines
            click.echo(style_info(f"📋 Last {lines} lines from {style_highlight(str(LOG_FILE))}"))
            click.echo("")
            with open(LOG_FILE, "r") as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    # Color code log lines
                    line_stripped = line.rstrip()
                    if "ERROR" in line_stripped or "CRITICAL" in line_stripped:
                        click.echo(style_error(f"  {line_stripped}"))
                    elif "WARNING" in line_stripped:
                        click.echo(style_warning(f"  {line_stripped}"))
                    elif "INFO" in line_stripped or "Started" in line_stripped or "Uvicorn" in line_stripped:
                        click.echo(style_info(f"  {line_stripped}"))
                    else:
                        click.echo(style_dim(f"  {line_stripped}"))
    except Exception as e:
        click.echo(style_error(f"✗ Error reading log file: {e}"))
        sys.exit(1)


@click.group()
@click.version_option(version=__version__)
def cli():
    """BlakPort - FastAPI wrapper for Ollama server"""
    pass


@cli.command()
@click.option("--background", "-b", is_flag=True, help="Start server in background")
@click.option("--host", help="Ollama server host (overrides config/env)")
@click.option("--port", type=int, help="Ollama server port (overrides config/env)")
@click.option("--provider", default="ollama", help="Provider name (default: ollama)")
def start(background, host, port, provider):
    """Start the BlakPort server"""
    # Build CLI overrides
    cli_overrides = {}
    if host:
        cli_overrides["host"] = host
    if port:
        cli_overrides["port"] = port
    if provider:
        cli_overrides["provider"] = provider
    
    if background:
        # Check if already running
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text().strip())
                os.kill(pid, 0)  # Check if process exists
                click.echo(f"BlakPort is already running (PID: {pid})", err=True)
                sys.exit(1)
            except (ProcessLookupError, ValueError):
                # Stale PID file, remove it
                PID_FILE.unlink()
        
        start_server(background=True, cli_overrides=cli_overrides if cli_overrides else None)
    else:
        start_server(background=False, cli_overrides=cli_overrides if cli_overrides else None)


@cli.command()
def stop():
    """Stop the BlakPort server"""
    stop_server()


@cli.command()
@click.option("--follow", "-f", is_flag=True, help="Follow log file (like tail -f)")
@click.option("--lines", "-n", default=50, help="Number of lines to show (default: 50)")
def log(follow, lines):
    """Show BlakPort server logs"""
    show_logs(follow=follow, lines=lines)


@cli.command()
def status():
    """Show BlakPort server status"""
    show_status()


@cli.command(name="init")
@click.option("--host", help="Ollama server host")
@click.option("--port", type=int, help="Ollama server port")
@click.option("--provider", help="Provider name")
def init_config(host, port, provider):
    """Initialize or update BlakPort configuration file"""
    click.echo(style_info("⚙️  Initializing BlakPort configuration..."))
    config_instance = get_config()
    
    # Use provided values or prompt for missing ones
    if not host:
        host = click.prompt(f"{style_label('Ollama server host')}", default="127.0.0.1")
    if port is None:
        port = click.prompt(f"{style_label('Ollama server port')}", default=11434, type=int)
    if not provider:
        provider = click.prompt(f"{style_label('Provider')}", default="ollama")
    
    config_data = {
        "host": host,
        "port": port,
        "provider": provider
    }
    config_instance.save_config_file(config_data)
    click.echo("")
    click.echo(style_success("✓ Configuration initialized successfully!"))
    click.echo(f"  {style_label('Config:')} {style_highlight(str(CONFIG_FILE))}")


@cli.command(name="configure")
@click.option("--host", help="Ollama server host")
@click.option("--port", type=int, help="Ollama server port")
@click.option("--provider", help="Provider name")
def configure(host, port, provider):
    """Configure BlakPort settings interactively or via CLI args"""
    click.echo(style_info("⚙️  Configuring BlakPort..."))
    config_instance = get_config()
    
    # Load current config
    current_host = config_instance.get("host")
    current_port = config_instance.get("port")
    current_provider = config_instance.get("provider")
    
    # Use provided values or prompt for missing ones
    if not host:
        host = click.prompt(f"{style_label('Ollama server host')}", default=current_host)
    if port is None:
        port = click.prompt(f"{style_label('Ollama server port')}", default=current_port, type=int)
    if not provider:
        provider = click.prompt(f"{style_label('Provider')}", default=current_provider)
    
    config_data = {
        "host": host,
        "port": port,
        "provider": provider
    }
    config_instance.save_config_file(config_data)
    click.echo("")
    click.echo(style_success("✓ Configuration updated successfully!"))
    click.echo(f"  {style_label('Config:')} {style_highlight(str(CONFIG_FILE))}")


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()

