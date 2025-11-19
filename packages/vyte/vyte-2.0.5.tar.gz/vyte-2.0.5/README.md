# 🚀 vyte - Rapid Development Tool

<p align="center">
  <img src="images/Logo_V_Transparente.png" alt="Vyte Logo" width="400"/>
</p>

<p align="center">
  <strong>Professional API project generator for Python. Create production-ready REST APIs in seconds.</strong>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/vyte"><img src="https://badge.fury.io/py/vyte.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python Version"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://github.com/PabloDomi/Vyte/actions"><img src="https://github.com/PabloDomi/Vyte/actions/workflows/lint-test.yml/badge.svg" alt="Tests"></a>
  <a href="https://codecov.io/gh/PabloDomi/Vyte"><img src="https://codecov.io/gh/PabloDomi/Vyte/branch/main/graph/badge.svg" alt="codecov"></a>
  <a href="https://github.com/pre-commit/pre-commit"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit" alt="Pre-commit"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <br>
  <a href="https://pablodomi.github.io/Vyte/"><img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation"></a>
</p>

______________________________________________________________________

## ✨ Features

- 🎯 **Multiple Frameworks**: Flask-Restx, FastAPI, Django-Rest
- 🗄️ **Multiple ORMs**: SQLAlchemy, TortoiseORM, Peewee, Django ORM
- 💾 **Database Support**: PostgreSQL, MySQL, SQLite
- 🔐 **JWT Authentication**: Secure authentication out of the box
- 🐳 **Docker Ready**: Complete Docker and docker-compose setup
- 🧪 **Testing Suite**: Pytest with coverage reports
- 📚 **Auto Documentation**: Swagger/OpenAPI automatic docs
- ⚡ **Modern Stack**: Python 3.11+, Pydantic v2, async support
- 🎨 **Beautiful CLI**: Rich terminal UI with interactive setup

## 🚀 Quick Start

### Installation

```bash
# Using pip
pip install vyte

# Using pipx (recommended)
pipx install vyte

# From source
git clone https://github.com/PabloDomi/Vyte.git
cd vyte
pip install -e .
```

### Create Your First Project

```bash
# Interactive mode (recommended)
vyte create

# Or specify options directly
vyte create \
  --name my-api \
  --framework FastAPI \
  --orm SQLAlchemy \
  --database PostgreSQL
```

### What You Get

```
my-api/
├── src/
│   ├── __init__.py          # App factory
│   ├── main.py              # Entry point
│   ├── config/
│   │   └── config.py        # Pydantic settings
│   ├── models/
│   │   └── models.py        # Database models
│   ├── routes/
│   │   └── routes_example.py
│   ├── services/
│   └── security.py          # JWT & security
├── tests/
│   ├── test_api.py
│   ├── test_models.py
│   └── conftest.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

## 📖 Usage

### Interactive Mode

The easiest way to create a project:

```bash
vyte create
```

Follow the prompts to configure your project.

### Command Line Options

```bash
vyte create \
  --name my-api \
  --framework FastAPI \
  --orm SQLAlchemy \
  --database PostgreSQL \
  --auth \
  --docker \
  --tests \
  --git
```

### Available Commands

```bash
# Create new project
vyte create

# Show framework information
vyte info FastAPI

# List all frameworks and ORMs
vyte list

# Show dependencies for configuration
vyte deps FastAPI --orm SQLAlchemy

# Validate existing project
vyte validate ./my-api

# Open documentation
vyte docs

# Show version
vyte --version
```

## 🎯 Supported Combinations

| Framework   | Compatible ORMs                 | Async Support |
| ----------- | ------------------------------- | ------------- |
| Flask-Restx | SQLAlchemy, Peewee              | ❌ Sync       |
| FastAPI     | SQLAlchemy (async), TortoiseORM | ✅ Async      |
| Django-Rest | Django ORM                      | ❌ Sync       |

## 🔧 Configuration

Projects use Pydantic Settings for configuration:

```python
# .env file
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
JWT_SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=True
```

## 🧪 Testing

Generated projects include complete testing setup:

```bash
# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 🐳 Docker Support

Run your project with Docker:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📚 Documentation

- [Full Documentation](https://vyte.readthedocs.io)
- [API Reference](https://vyte.readthedocs.io/api)
- [Examples](./examples)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

```bash
# Clone repo
git clone https://github.com/PabloDomi/Vyte.git
cd vyte

# Setup development environment
pip install -e ".[dev]"
pip install pre-commit black ruff isort

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
make format

# Run linters
make lint

# Run full CI suite
make ci
```

## 🗺️ Roadmap

Check out our [Roadmap](ROADMAP.md) to see what's planned for future releases!

**Coming in v2.1.0:**

- `vyte upgrade` - Upgrade existing projects
- `vyte add-model` - Add models to projects
- Customizable templates
- MongoDB support

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/)
- UI powered by [Rich](https://rich.readthedocs.io/)
- Templates with [Jinja2](https://jinja.palletsprojects.com/)
- Validation with [Pydantic](https://docs.pydantic.dev/)

## 📊 Project Stats

- **Test Coverage**: 73%
- **Code Quality**: A+ (Ruff, Black)
- **Security**: Scanned with Bandit
- **Python Versions**: 3.11, 3.12, 3.13
- **Platforms**: Linux, macOS, Windows

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/PabloDomi/Vyte/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PabloDomi/Vyte/discussions)
- **Email**: Domi@usal.es

______________________________________________________________________

Made with ❤️ by Pablo Domínguez Blanco
