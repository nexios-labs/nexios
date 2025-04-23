---
icon: code-branch
---

# Contributing&#x20;

Welcome, developer. Contributing to Nexios is a serious endeavor, and we appreciate your commitment to maintaining the quality and integrity of the project. This guide will walk you through setting up your environment, adhering to contribution rules, and following best practices for committing code and writing documentation. Follow these steps carefully to ensure a smooth and professional development experience.

***

## Contribution Rules

Before diving into the technical setup, familiarize yourself with the rules and expectations for contributing to Nexios:

1. **Code Quality**: Write clean, maintainable, and efficient code. Follow PEP 8 guidelines for Python code.
2. **Testing**: Every new feature or bug fix must include corresponding unit tests. Ensure all tests pass before submitting a pull request.
3. **Documentation**: Update or add documentation for any new features or changes. Documentation is written using **Docsify**.
4. **Branching**: Create a new branch for each feature or bug fix. Do not work directly on the `main` branch.
5. **Pull Requests**: Submit a pull request (PR) for review. Ensure your PR includes a clear description of the changes and references any related issues.
6. **Code Reviews**: Be responsive to feedback during code reviews. Address comments and make necessary changes promptly.
7. **Respect the Community**: Be professional and respectful in all interactions with other contributors.

***

## Setting Up Your Environment

### 1. Clone the Repository

Start by cloning the Nexios repository from GitHub. Open your terminal and execute the following command:

```sh
# Replace "your-username" with your GitHub username if you have forked the repository
git clone https://github.com/nexios-labs/nexios.git
cd nexios
```

This will download the project and navigate into the directory.

***

### 2. Install Poetry

Nexios uses **Poetry** for dependency management. To install Poetry globally, run:

```sh
pip install --user poetry
```

Once installed, verify the installation by checking the version:

```sh
poetry --version
```

If a version number is displayed, the installation was successful.

***

### 3. Install Dependencies

After installing Poetry, set up the project environment by running:

```sh
poetry install
```

This command will install all required dependencies and create a virtual environment for the project.

***

### 4. Set Up Tox

**Tox** is used to automate testing across multiple environments. Before running tests, install Tox inside the virtual environment by executing:

```sh
poetry shell  # Activates Poetry's virtual environment
pip install tox
```

Verify the installation by running:

```sh
tox --version
```

If the version number is displayed, Tox has been installed correctly.

***

### 5. Run the Tests

Before submitting any code, ensure that all tests pass by running:

```sh
tox
```

Tox will execute tests in different environments to confirm that the application is functioning as expected.

***

## Working on Your Feature

Now that the environment is set up, you can begin implementing new features or fixing bugs. Follow these guidelines:

1.  **Create a Branch**: Always work on a new branch for your changes. Use a descriptive branch name, such as `feature/add-new-endpoint` or `bugfix/fix-login-issue`.

    ```sh
    git checkout -b your-branch-name
    ```
2. **Write Unit Tests**: Every new feature or bug fix must include corresponding unit tests. Ensure your tests cover edge cases and potential failures.
3. **Adhere to Coding Style**: Follow the existing coding style and project structure. Use tools like `black` and `flake8` to format and lint your code.
4. **Run Tests Locally**: Before pushing your changes, run `tox` to ensure all tests pass in all environments.
5. **Commit Your Changes**: Follow the commit message guidelines outlined below.

***

## Commit Message Guidelines

Commit messages should be clear, concise, and follow the **Conventional Commits** format. This helps maintain a clean and understandable commit history. The format is as follows:

```
<type>(<scope>): <description>
```

* **Type**: Describes the purpose of the commit. Common types include:
  * `feat`: A new feature.
  * `fix`: A bug fix.
  * `docs`: Documentation changes.
  * `style`: Code style or formatting changes.
  * `refactor`: Code refactoring without changing functionality.
  * `test`: Adding or modifying tests.
  * `chore`: Maintenance or tooling changes.
* **Scope**: Optional. Specifies the part of the codebase affected by the change (e.g., `auth`, `api`, `docs`).
* **Description**: A brief summary of the changes.

Example commit messages:

```
feat(auth): add OAuth2 support for user authentication
fix(api): resolve 500 error on invalid input
docs(readme): update installation instructions
```

***

## Documentation with Docsify

Nexios uses **Docsify** for documentation. Docsify is a lightweight and powerful documentation generator that renders Markdown files into a beautiful documentation site. Follow these steps to contribute to the documentation:

1.  **Install Docsify**: If you want to preview your documentation changes locally, install Docsify globally:

    ```sh
    npm install -g docsify-cli
    ```
2.  **Serve the Documentation**: Navigate to the `docs` directory and start the Docsify server:

    ```sh
    cd docs
    docsify serve
    ```

    This will start a local server, and you can view the documentation at `http://localhost:3000`.
3. **Edit Documentation**: Documentation files are written in Markdown and located in the `docs` directory. Make your changes and preview them locally.
4. **Commit Documentation Changes**: Follow the commit message guidelines and include `docs` in the type (e.g., `docs(readme): update contributing guide`).

***

## Submitting a Pull Request

Once your changes are complete, follow these steps to submit a pull request:

1.  **Push Your Branch**: Push your branch to your forked repository:

    ```sh
    git push origin your-branch-name
    ```
2. **Create a Pull Request**: Go to the Nexios repository on GitHub and create a pull request from your branch to the `main` branch.
3. **Describe Your Changes**: Provide a clear and detailed description of your changes in the PR. Reference any related issues using keywords like `Closes #123`.
4. **Address Feedback**: Be responsive to feedback during the code review process. Make necessary changes and push updates to your branch.

***



By following this guide, you will contribute effectively to Nexios while maintaining code quality, consistency, and professionalism. Thank you for your dedication to the project, and we look forward to your contributions!

If you have any questions or need assistance, feel free to reach out to the maintainers or the community. Happy coding! 🚀
