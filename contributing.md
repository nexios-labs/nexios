# Contributing to Nexios

Welcome, developer. This guide will walk you through setting up your environment to contribute to Nexios effectively. Follow these steps carefully to ensure a smooth development experience.

---

## Clone the Repository

The first step is to clone the Nexios repository from GitHub. Open your terminal and execute the following command:

```sh
# Replace "your-username" with your GitHub username if you have forked the repository
git clone https://github.com/your-username/nexios.git
cd nexios
```

This will download the project and navigate into the directory.

---

## Install Poetry

Nexios uses Poetry for dependency management. To install Poetry globally, run:

```sh
pip install --user poetry
```

Once installed, verify the installation by checking the version:

```sh
poetry --version
```

If a version number is displayed, the installation was successful.

---

## Install Dependencies

After installing Poetry, set up the project environment by running:

```sh
poetry install
```

This command will install all required dependencies and create a virtual environment for the project.

---

## Set Up Tox

Tox is used to automate testing across multiple environments. Before running tests, install Tox inside the virtual environment by executing:

```sh
poetry shell  # Activates Poetry's virtual environment
pip install tox
```

Verify the installation by running:

```sh
tox --version
```

If the version number is displayed, Tox has been installed correctly.

---

## Run the Tests

Before submitting any code, ensure that all tests pass by running:

```sh
tox
```

Tox will execute tests in different environments to confirm that the application is functioning as expected.

---

## Work on Your Feature

Now that the environment is set up, you can begin implementing new features or fixing bugs. Ensure you follow these guidelines:

- Write unit tests for every new feature to maintain test coverage.
- Adhere to the existing coding style and project structure.
- Run `tox` again before pushing changes to verify that all tests pass.

Once your changes are complete, commit and push your code to your forked repository, then create a pull request.

---

By following this guide, you will contribute effectively to Nexios while maintaining code quality and consistency.

