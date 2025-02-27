# Installation Guide

### Prerequisites

Before installing Nexios, ensure that you have the following installed:

- **Python 3.10+**: Nexios requires Python 3.10 or later.
- **Poetry**: Used for dependency management and package installation.
- **Git**: Required if installing from GitHub.

### Installing Python 3.10+
If you don’t have Python 3.10 or higher installed, you can download it from the official website:

- [Download Python](https://www.python.org/downloads/)

Alternatively, if you use **Pyenv** for managing multiple Python versions, install Python 3.10+ with:

```sh
pyenv install 3.10.0
pyenv global 3.10.0
```

Verify the installation:

```sh
python --version
```
It should display `Python 3.10.x` or higher.

## Installing Poetry
If you do not have Poetry installed, you can install it using the following command:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Verify the installation:
```sh
poetry --version
```

---

## Installing Nexios

### 1. Install Nexios from PyPI (Recommended)
The easiest way to install Nexios is through PyPI.

1. **Create a new virtual environment (optional but recommended):**
   ```sh
   python -m venv nexios_env
   source nexios_env/bin/activate  # On Windows: nexios_env\Scripts\activate
   ```

2. **Install Nexios using pip:**
   ```sh
   pip install nexios
   ```

3. **Verify installation:**
   ```sh
   python -c "import nexios; print(nexios.__version__)"
   ```
   This should print the installed version of Nexios.

---

### 2. Install Nexios using Poetry
If you prefer managing dependencies with Poetry:

1. **Create and activate a virtual environment:**
   ```sh
   python -m venv nexios_env
   source nexios_env/bin/activate  # On Windows: nexios_env\Scripts\activate
   ```

2. **Install Nexios using Poetry:**
   ```sh
   poetry add nexios
   ```

3. **Verify installation:**
   ```sh
   python -c "import nexios; print(nexios.__version__)"
   ```

---

### 3. Install Nexios from a Specific GitHub Branch
If you want to install Nexios from a specific branch on GitHub, follow these steps:

1. **Clone the repository and navigate into it:**
   ```sh
   git clone -b <branch-name> https://github.com/your-username/nexios.git
   cd nexios
   ```
   Replace `<branch-name>` with the name of the branch you want to install.

2. **Install dependencies using Poetry:**
   ```sh
   poetry install
   ```

3. **If you prefer installing directly from GitHub without cloning the repo, use:**
   ```sh
   poetry add git+https://github.com/your-username/nexios.git@<branch-name>
   ```

4. **Verify installation:**
   ```sh
   python -c "import nexios; print(nexios.__version__)"
   ```

---



Now you have Nexios installed and ready to use! 🚀

