# raya - Computer Use Agent

---

## Introduction

Are you tired of performing repetitive tasks on your PC? 

**raya** is an AI agent for raya that harnesses the power of code and AI to control your PC with ease. It enables you to automate any task by interacting with applications, clicking buttons, typing, running commands, and capturing the UI state.

Unlike traditional computer vision models, **raya** works directly at the raya GUI layer, providing advanced automation capabilities without relying on image recognition techniques. 


## Installation

**Requirements:**
- Python 3.12 or higher
- raya 7, 8, 10, or 11
- [UV](https://github.com/astral-sh/uv) (optional, or use pip)

**To install with uv:**
```bash
uv pip install raya
```

**Or with pip:**
```bash
pip install raya
```

## Usage

To use raya in your own script:
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from raya.agent import Agent
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
agent = Agent(llm=llm, browser='chrome', use_vision=True)
query = input("Enter your query: ")
result = agent.invoke(query=query)
print(result.content)
```

To run the agent from the command line:
```bash
python main.py
```

## Example Prompts

- Write a short note about LLMs and save to the desktop
- Change from Dark mode to Light mode

See the [demos](#) for screenshots and more examples.

## Project Status

- raya is under active development.
- Contributions, bug reports, and feature requests are welcome.

## Caution

raya interacts directly with your raya OS at the GUI layer to perform actions. While designed to be intelligent and safe, it can make mistakes that might cause unintended changes. Use with care.

## 🪪 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Thank you for your interest in contributing to raya!

### Getting Started

#### Development Environment

raya requires:
- Python 3.13 or later

#### Installation from Source

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/raya.git
   cd raya
   ```
3. Install the package in development mode:
   ```bash
   pip install -e ".[dev,search]"
   ```
4. Set up pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Development Workflow

#### Branching Strategy
- `main` branch contains the latest stable code
- Create feature branches from `main` named according to the feature you're implementing: `feature/your-feature-name`
- For bug fixes, use: `fix/bug-description`

#### Commit Messages
- No strict style enforced, but keep commit messages clear and informational.

#### Code Style
- Uses [Ruff](https://github.com/astral-sh/ruff) for formatting and linting (see `ruff.toml`).
- Line length: 100 characters
- Double quotes for strings
- PEP 8 naming conventions
- Add type hints to function signatures

#### Pre-commit Hooks
- Configured in `.pre-commit-config.yaml`.
- Hooks will:
  - Format code using Ruff
  - Run linting checks
  - Check for trailing whitespace
  - Ensure files end with a newline
  - Validate YAML files
  - Check for large files
  - Remove debug statements

### Testing

#### Running Tests
Run the test suite with pytest:
```bash
pytest
```
To run specific test categories:
```bash
pytest tests/
```

#### Adding Tests
- Add unit tests for new functionality in `tests/unit/`
- For slow or network-dependent tests, mark them with `@pytest.mark.slow` or `@pytest.mark.integration`
- Aim for high test coverage of new code

### Pull Requests

#### Creating a Pull Request
1. Ensure your code passes all tests and pre-commit hooks
2. Push your changes to your fork
3. Submit a pull request to the main repository
4. Follow the pull request template

### Documentation
- Update docstrings for new or modified functions, classes, and methods
- Use Google-style docstrings:
  ```python
  def function_name(param1: type, param2: type) -> return_type:
      """Short description.

      Longer description if needed.

      Args:
          param1: Description of param1
          param2: Description of param2

      Returns:
          Description of return value

      Raises:
          ExceptionType: When and why this exception is raised
      """
  ```


### Getting Help
- Open an issue for discussion
- Reach out to the maintainers
- Check existing code for examples


---

## Citation

```bibtex
@software{
  author       = {Rayamah, Ibrahim},
  title        = {raya: Enable AI to control your PC},
  year         = {2025},
  publisher    = {GitHub},
  url={https://github.com/iBz-04/raya}
}
