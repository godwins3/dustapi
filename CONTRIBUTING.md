# Contributing to Dust

First of all, thank you for your interest in contributing to Dust! We appreciate any help you can provide in making this framework better.

## How to Contribute

### Reporting Bugs

If you find a bug in the framework, please report it by creating an issue on the [GitHub Issues](https://github.com/godwins3/dust/issues) page. Please include as much detail as possible to help us understand and reproduce the issue.

### Feature Requests

If you have a feature request or an idea for improving Dust, please open an issue on the [GitHub Issues](https://github.com/dust/dust/issues) page and label it as a "Feature Request". 

### Code Contributions

1. **Fork the Repository:**

    Fork the Dust repository to your own GitHub account and then clone it to your local machine to start working on the changes.

    ```bash
    git clone https://github.com/godwins3/dust.git
    cd dust
    ```

2. **Create a New Branch:**

    Create a new branch for your changes. It's good practice to name the branch according to the feature or bug fix you are working on.

    ```bash
    git checkout -b feature-or-bugfix-name
    ```

3. **Install Dependencies:**

    Create and activate a virtual environment, then install the necessary dependencies.

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

4. **Make Your Changes:**

    Implement your feature or bug fix. Make sure your code follows the project's coding standards.

5. **Write Tests:**

    Add or update tests to cover your changes. This ensures that the framework remains stable and that your changes do not introduce any new bugs.

6. **Run Tests:**

    Run the test suite to make sure all tests pass.

    ```bash
    python -m unittest discover -s tests
    ```

7. **Commit Your Changes:**

    Commit your changes with a clear and descriptive commit message.

    ```bash
    git add .
    git commit -m "Description of the feature or fix"
    ```

8. **Push to Your Fork:**

    Push your changes to your forked repository.

    ```bash
    git push origin feature-or-bugfix-name
    ```

9. **Open a Pull Request:**

    Go to the original Dust repository and open a pull request. Provide a clear description of your changes and why they are necessary.

## Coding Standards

- Follow PEP 8 guidelines for Python code.
- Write clear and concise commit messages.
- Ensure your code is well-documented.

## License

By contributing to Dust, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

Thank you for contributing!
