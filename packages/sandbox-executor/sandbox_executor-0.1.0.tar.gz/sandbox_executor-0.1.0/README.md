# 🔒 Python Sandbox Executor

A secure Python code execution library with **dual-mode architecture**: run code locally for fast development or connect to a remote API server for production workloads. Perfect for AI agents, code playgrounds, and educational platforms.

## ✨ Key Features

- 🏠 **Local Execution**: Direct subprocess execution for fast iteration and debugging
- 🌐 **Remote Execution**: HTTP client for connecting to sandbox API servers
- 🔄 **Unified Interface**: Same API works for both local and remote modes
- 🤖 **AI Agent Ready**: Easy integration with LangChain, AutoGen, and custom agents
- **Multi-layered Security**: AST validation, resource limits, network control
- 📁 **File I/O Support**: Upload input files and retrieve output files
- ⚡ **Platform Agnostic**: Works on Linux, Windows, macOS, Docker, Kubernetes, and serverless

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/dinhhungitsoft/secure-python-sandbox.git
cd secure-python-sandbox

# Install the package (includes local + remote client)
pip install -e .

# Optional: Install with API server support
pip install -e ".[api]"
```

## 💡 Usage Modes

### Mode 1: Local Execution (Development)

**Best for**: Development, debugging, fast iteration, local AI agents

**How it works**: Executes code directly on your machine using subprocess isolation

**Installation**:
```bash
pip install -e .
```

**Example**:
```python
from sandbox_executor import SandboxClient

# Create client without server_url = local execution
client = SandboxClient()

code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = [fibonacci(i) for i in range(10)]
print("Fibonacci:", result)
"""

result = client.execute(code)
print(result.stdout)
# Output: Fibonacci: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

**Advantages**:
- ⚡ **Fastest**: No network overhead
- 🐛 **Easy debugging**: Direct execution with full error messages
- 🔧 **Simple setup**: No server required
- 💻 **Offline capable**: Works without internet

**Use cases**:
- Local development and testing
- AI agent prototyping
- Educational tools
- Code snippets execution
- Quick scripts and automation

---

### Mode 2: Remote Execution (Production)

**Best for**: Production, scaling, untrusted code, multi-tenant systems

**How it works**: Sends code to a remote API server via HTTP requests

**Installation**:
```bash
# Install package with remote support (already included in core)
pip install -e .

# Set up API server
pip install -e ".[api]"
docker-compose up -d  # Start the sandbox API server
```

**Example**:
```python
from sandbox_executor import SandboxClient

# Create client with server_url = remote execution
client = SandboxClient(
    server_url="http://localhost:8000",
    timeout=30
)

code = """
import math

radius = 5
area = math.pi * radius ** 2
print(f"Circle area: {area:.2f}")
"""

result = client.execute(code)
print(result.stdout)
# Output: Circle area: 78.54
```

**Advantages**:
- 🔒 **Enhanced security**: Code runs in isolated containers
- 📈 **Scalable**: Handle multiple concurrent executions
- 🌐 **Distributed**: Execute code on powerful remote machines
- 🛡️ **Better isolation**: Full container-level isolation

**Use cases**:
- Production AI agents
- Multi-tenant code execution platforms
- Online code playgrounds
- Serverless functions
- Educational platforms with many users

---

## 🎯 Comparison: Local vs Remote

| Feature | Local Execution | Remote Execution |
|---------|----------------|------------------|
| **Speed** | ⚡ Fastest (no network) | 🌐 Network latency |
| **Setup** | ✅ Zero config | ⚙️ Needs API server |
| **Security** | 🛡️ Process isolation | 🔒 Container isolation |
| **Scalability** | 💻 Single machine | 📈 Distributed |
| **Use Case** | 🐛 Development | 🚀 Production |
| **Internet** | ❌ Not required | ✅ Required |

## Configuration

### Local Mode Configuration

```python
from sandbox_executor import SandboxClient, ClientConfig, ExecutionMode

config = ClientConfig(
    server_url=None,  # None = local execution
    mode=ExecutionMode.SECURE,
    timeout=60,
    allow_network=False,
    max_memory_mb=256
)

client = SandboxClient.from_config(config)
```

### Remote Mode Configuration

```python
from sandbox_executor import SandboxClient, ClientConfig

config = ClientConfig(
    server_url="http://your-api-server.com",
    timeout=30,
    api_timeout=60,  # HTTP request timeout
    api_key="your-secret-key"  # Optional authentication
)

client = SandboxClient.from_config(config)
```

### Environment Variables

Create a `.env` file:
```bash
SANDBOX_MODE=secure
SANDBOX_TIMEOUT=30
SANDBOX_ALLOW_NETWORK=false
SANDBOX_MAX_MEMORY_MB=128
```

Load automatically:
```python
client = SandboxClient.from_env()
```

## Advanced Examples

### Working with Files

```python
from sandbox_executor import SandboxClient

client = SandboxClient()

# Provide input files
input_files = {
    "data.csv": b"id,value\n1,100\n2,200\n3,300\n"
}

code = """
import csv

# Read CSV
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Calculate total
total = sum(int(row['value']) for row in data)
print(f"Total: {total}")

# Write output
with open('result.txt', 'w') as f:
    f.write(f"Sum: {total}\\n")
"""

result = client.execute(code, input_files=input_files)
print(result.stdout)  # Total: 600

# Get output file
output = result.get_file_content('result.txt')
print(output.decode())  # Sum: 600
```

### AI Agent Integration

```python
from sandbox_executor import SandboxClient

class PythonExecutorTool:
    """Tool for AI agents to execute Python code"""
    
    name = "python_executor"
    description = "Execute Python code safely in a sandbox"
    
    def __init__(self, use_remote=False):
        # Switch between local and remote based on environment
        server_url = "http://api.example.com" if use_remote else None
        self.client = SandboxClient(server_url=server_url)
    
    def run(self, code: str) -> str:
        """Execute code and return output"""
        result = self.client.execute(code)
        return result.stdout if result.success else f"Error: {result.stderr}"

# For development (local)
tool = PythonExecutorTool(use_remote=False)

# For production (remote)
tool = PythonExecutorTool(use_remote=True)
```

### Error Handling

```python
from sandbox_executor import SandboxClient, SandboxException

client = SandboxClient()

code = "print(1/0)"  # Will raise ZeroDivisionError

try:
    result = client.execute(code)
    if not result.success:
        print(f"Execution failed with code {result.return_code}")
        print(f"Error: {result.stderr}")
except SandboxException as e:
    print(f"Sandbox error: {e}")
```

## 🐳 Running the API Server (Remote Mode)

### Using Docker Compose (Recommended)

```bash
# Start the server
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### Using Docker

```bash
# Build image
docker build -t python-sandbox .

# Run container
docker run -d -p 8000:8000 \
  -e EXECUTION_MODE=secure \
  -e SANDBOX_TIMEOUT=30 \
  python-sandbox
```

### Manual Setup

```bash
# Install with API dependencies
pip install -e ".[api]"

# Run server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### `GET /` - Health Check
```bash
curl http://localhost:8000/
```

#### `POST /execute` - Execute Code
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "timeout": 30,
    "allow_network": false
  }'
```

## 🏗️ Architecture

### Security Layers

```
┌─────────────────────────────────────┐
│   1. AST Validation                 │  Compile-time filtering
├─────────────────────────────────────┤
│   2. Import Restrictions            │  Module whitelist/blacklist
├─────────────────────────────────────┤
│   3. Resource Limits                │  CPU, Memory, Processes
├─────────────────────────────────────┤
│   4. Filesystem Isolation           │  Temporary directory sandbox
├─────────────────────────────────────┤
│   5. Network Blocking               │  Socket monkey-patching
├─────────────────────────────────────┤
│   6. Execution Timeout              │  Hard timeout enforcement
└─────────────────────────────────────┘
```

### Execution Modes

**Secure Mode (Default)**:
- AST validation and restricted imports
- Resource limits (CPU, memory, processes)
- Filesystem isolation with temporary directories
- Network blocking (configurable)
- Execution timeout enforcement

**Simple Mode**:
- Basic subprocess isolation
- Timeout and output limits
- Suitable for trusted code

## 📚 Examples

See the [`examples/`](./examples/) directory for complete examples:

- **`basic_usage.py`** - Basic execution patterns
- **`client_usage.py`** - Local vs Remote client usage  
- **`agent_integration.py`** - AI agent integration examples
- **`with_files.py`** - Working with input/output files
- **`security_tests.py`** - Security feature demonstrations

Run examples:
```bash
python examples/basic_usage.py
python examples/client_usage.py
python examples/agent_integration.py
```

## ⚙️ Configuration

### Environment Variables

Configure the sandbox behavior using environment variables (in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SANDBOX_MODE` | `secure` | Execution mode: `secure` or `simple` |
| `SANDBOX_TIMEOUT` | `30` | Default execution timeout (seconds) |
| `SANDBOX_ALLOW_NETWORK` | `false` | Allow network access by default |
| `SANDBOX_MAX_MEMORY_MB` | `128` | Maximum memory usage (MB) |

### Security Configuration

The secure executor includes configurable whitelists and blacklists:

**Safe Modules** (allowed by default):
- `math`, `random`, `datetime`, `json`, `base64`, `hashlib`
- `collections`, `itertools`, `functools`, `re`, `string`
- `decimal`, `fractions`, `statistics`, `uuid`, `secrets`

**Blocked Modules** (always restricted):
- `os`, `sys`, `subprocess`, `multiprocessing`, `threading`
- `socket`, `urllib`, `requests`, `http`, `ftplib`, `smtplib`
- `importlib`, `eval`, `exec`, `compile`

## 🛡️ Security Considerations

### What's Protected

✅ **Import restrictions**: Dangerous modules are blocked  
✅ **Resource limits**: CPU, memory, and process limits enforced  
✅ **Filesystem isolation**: Code runs in temporary directories  
✅ **Network blocking**: Optional socket-level blocking  
✅ **Timeout enforcement**: Hard timeout prevents infinite loops  
✅ **AST validation**: Compile-time code analysis

### What's NOT Protected

⚠️ **DoS attacks**: Malicious code can still consume allowed resources  
⚠️ **Side-channel attacks**: Timing and cache attacks are possible  
⚠️ **Data exfiltration**: If network is enabled, data can be sent out  
⚠️ **Cryptographic operations**: CPU-intensive operations within limits  

### Best Practices

1. **Always use secure mode** in production
2. **Keep network access disabled** unless required
3. **Set appropriate resource limits** based on your use case
4. **Monitor resource usage** and adjust limits accordingly
5. **Run in containers** for additional isolation
6. **Keep dependencies updated** for security patches
7. **Validate user input** before sending to the sandbox
8. **Implement rate limiting** to prevent abuse

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_sandbox_executor.py
```

See [`tests/README.md`](./tests/README.md) for detailed testing documentation.

## 🔧 Development

### Project Structure

```
python_sandbox/
├── src/
│   ├── main.py                          # FastAPI application (API server)
│   ├── executor_factory.py              # Legacy factory pattern
│   └── sandbox_executor/                # Main package
│       ├── __init__.py                  # Package exports
│       ├── client.py                    # Unified client (local/remote)
│       ├── executor.py                  # Local executor
│       ├── config.py                    # Configuration classes
│       ├── exceptions.py                # Custom exceptions
│       └── executors/                   # Backend implementations
│           ├── sandbox_executor.py      # Simple mode
│           └── secure_sandbox_executor.py  # Secure mode
├── examples/                            # Usage examples
│   ├── basic_usage.py                   # Basic patterns
│   ├── client_usage.py                  # Local vs Remote
│   ├── agent_integration.py             # AI agent examples
│   └── ...
├── tests/                               # Test suite
├── docker-compose.yml                   # Docker Compose config
├── Dockerfile                           # Docker image
└── pyproject.toml                       # Package configuration
```

## 🚢 Deployment

### Local Development
```bash
pip install -e .
python examples/basic_usage.py
```

### API Server (Docker)
```bash
docker-compose up -d
```

## Documentation
- **[examples/](./examples/)** - Code examples

### Cloud Platforms

The sandbox is compatible with:
- **AWS Fargate**: Deploy as ECS task
- **Azure Container Apps**: Deploy as container app
- **Google Cloud Run**: Deploy as Cloud Run service
- **Heroku**: Deploy as Docker container
- **DigitalOcean App Platform**: Deploy as Docker app

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/dinhhungitsoft/secure-python-sandbox/issues)
- **Examples**: Check the [examples/](./examples/) directory
- **API Docs**: Visit http://localhost:8000/docs when running the server

## ⭐ Star History

If you find this project useful, please give it a star! ⭐

---

**Made with ❤️ for the Python & AI community**

**⚠️ Security Note**: While this sandbox provides multiple layers of security, no sandbox is 100% foolproof. Always run in isolated environments and implement additional security measures for production use with untrusted code.