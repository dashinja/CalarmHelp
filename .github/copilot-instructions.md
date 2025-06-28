## Development Protocol
- **Planning Required**: Before generating code, investigate requirements, analyze existing codebase patterns, identify components, determine approach, and create test plan. Always offer solution and ask for confirmation before proceeding. Do not generate code without user confirmation.
- **Planning Review**: Stop and ask user to review the plan, and wait for instructions to either modify or continue on with the plan.
- **Implementing Code**: Ensure to put classes with other classes and functions with other functions, so as not to disrupt the flow and organization of files.
- **DEBUG and Troubleshooting**: Ensure cleanup after debugging as in removing DEBUG statements, and unnecessary print statements, so as to maintain only streamlined and useful terminal printing.
- **Final Planning Step**: Always review `copilot-instructions.md` to ensure plan compliance.
- **Azure**: Use Azure best practices tools when working with Azure services, deployments, or operations.

## Python Standards
- Use `poetry` for dependency management, `pytest` for testing
- Use Sphinx format for docstrings
- No deprecated code; resolve all terminal warnings in both normal CLI output and test runs

## Testing Requirements
- Generate comprehensive tests: unit tests for libraries, integration tests for applications
- Explicitly Mock ALL external dependencies, CRUD operations, and DELETE endpoints
- Never modify or delete real files - use temporary directories if needed, clean up after
- Using vscode's test panel, run the complete existing test suite after new code; fix any breakages
- Tests must be isolated from external systems and real data
- Do not add new files to root for testing, debugging, or validation, etc. Add in a folder of appropriate name inside the `tests` folder.
- Cleanup any temporary files or resources created during testing.
- Cleanup involves removing print DEBUG statements from tests as well.
- If any tests that involve API calls, external dependencies, etc. make real calls - then rewrite them so that they do not.

## Code Quality & Security
- Include error handling, input validation, edge case handling, and logging
- Validate inputs to prevent injection attacks
- Use environment variables for secrets (never hard-code sensitive data)
- Add inline comments for complex logic

## Documentation & Versioning
- Create `README.md` for feature sets with usage examples and cross-references
- Maintain single root `CHANGELOG.md` using Keep a Changelog format
- Follow semantic versioning: patch (bugs), minor (features), major (breaking changes)
- Update `pyproject.toml` version to match changelog
- Keep all documentation current with code changes
- Only append to changelog, never modify previous versions

## Final Step
Always ensure your final step is always to look at, check for, and if necessary, update the `copilot-instructions.md` file to ensure that the instructions are up to date and reflect the latest best practices and standards for the project.
- **Final Review**: Ensure all generated code adheres to the guidelines in `copilot-instructions.md` before finalizing changes.