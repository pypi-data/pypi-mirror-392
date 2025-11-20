# Linting Setup Specification

## Overview

Add support for code quality linting (using Ruff) as part of the generated GitHub Actions workflows. This feature will ensure all code is automatically checked for style issues, common errors, and Python best practices during CI/CD pipeline execution.

**Key Design Decision**: Linting is **always enabled** in generated workflows (no configuration flags). This opinionated approach simplifies implementation, reduces code complexity, and promotes best practices. Users who don't want linting can manually remove the step from generated files.

## Summary of Changes

- **Templates**: Add linting step to `_reusable_test_build.yml.j2` (no conditionals)
- **Templates**: Add Ruff configuration to `pyproject.toml.j2`
- **Tests**: Verify linting is always present in generated workflows
- **Dogfooding**: This project will use its own generated workflows with linting
- **No CLI/MCP changes**: No new parameters or flags needed

## Background

### Current State

The pypi-workflow-generator currently generates three GitHub Actions workflows:
- `_reusable-test-build.yml` - Shared reusable workflow for testing and building
- `test-pr.yml` - PR testing workflow that publishes to TestPyPI
- `release.yml` - Production release workflow that publishes to PyPI

Current quality checks in `_reusable-test-build.yml`:
1. Checkout repository with full history
2. Set up Python environment
3. Install dependencies via pip
4. Run pytest tests
5. Build package

**Gap**: No linting or code quality checks are performed.

### Why Ruff?

Ruff is the recommended choice because:
- **Speed**: 10-100x faster than traditional Python linters (written in Rust)
- **All-in-one**: Replaces Flake8, Black, isort, pyupgrade, and more
- **Modern**: Active development, excellent VS Code integration
- **Industry standard**: Widely adopted in modern Python projects
- **Simple configuration**: Minimal setup required via pyproject.toml

## Requirements

### Functional Requirements

1. **FR1: Linting Integration in Reusable Workflow**
   - Add a linting step to `_reusable_test_build.yml.j2` template
   - Linting should run BEFORE tests (fail fast approach)
   - Linting failures should block the workflow execution

2. **FR2: Ruff as Primary Linter**
   - Use Ruff for all linting checks
   - Include both linting (`ruff check`) and formatting (`ruff format --check`)
   - Support configuration via pyproject.toml in generated projects

3. **FR3: Configuration Generation**
   - Add basic Ruff configuration to `pyproject.toml.j2` template
   - Include sensible defaults for Python projects
   - Make configuration customizable by users

4. **FR4: Dependency Management**
   - Add Ruff to generated pyproject.toml's dev dependencies
   - Ensure Ruff is installed during CI/CD pipeline

### Non-Functional Requirements

1. **NFR1: Backward Compatibility**
   - Existing workflows generated without linting should continue to work
   - All newly generated workflows will include linting by default
   - Users can manually remove the linting step if unwanted

2. **NFR2: Performance**
   - Linting step should add minimal overhead (<30 seconds for typical projects)
   - Leverage Ruff's speed advantage

3. **NFR3: Configurability**
   - Users should be able to customize Ruff rules via pyproject.toml
   - Support ignoring specific files/directories

4. **NFR4: Clear Error Messages**
   - Workflow failures due to linting should clearly indicate the issue
   - Users should understand what needs to be fixed

## Proposed Solution

### Files to Modify

1. **Templates**:
   - `_reusable_test_build.yml.j2` - Add linting step (always included)
   - `pyproject.toml.j2` - Add Ruff configuration and dependency

2. **Tests**:
   - `test_generator.py` - Add tests to verify linting step is always present in generated workflows
   - `test_server.py` - Add tests to verify linting configuration in generated files

**Note**: No changes needed to `generator.py`, `main.py`, or `server.py` - linting is always included without configuration parameters.

### Changes to Template Files

#### 1. `_reusable_test_build.yml.j2`

Add a new step after dependency installation:

```yaml
- name: Lint with Ruff
  run: |
    python -m pip install ruff
    ruff check .
    ruff format --check .
```

**Placement**: After "Install dependencies" step, before "Run tests with pytest" step.

**Rationale**: Fail fast - if code doesn't meet quality standards, don't waste time running tests.

**Note**: This step is always included in generated workflows. Users who don't want linting can manually delete this step from the generated file.

#### 2. `pyproject.toml.j2`

Add Ruff configuration section:

```toml
[project.optional-dependencies]
dev = [
    "twine",
    "wheel",
    "setuptools_scm",
    "build",
    "ruff",  # NEW
]

# NEW SECTION
[tool.ruff]
# Enable pycodestyle (`E`) and Pyflakes (`F`) codes by default.
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "DTZ", "T10", "EM", "ISC", "ICN", "PIE", "PT", "Q", "RET", "SIM", "TID", "ARG", "PTH", "PD", "PL", "NPY", "PERF", "RUF"]
ignore = []

# Exclude common directories
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
]

# Allow fix for all enabled rules (when `--fix` is used)
fixable = ["ALL"]
unfixable = []

# Line length to match Black default
line-length = 88

# Target Python version
target-version = "py38"

[tool.ruff.format]
# Use Black-compatible formatting
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

#### Why This Configuration?

This comprehensive rule set represents Ruff's best practices for modern Python development. While strict, it catches real bugs and enforces consistency:

**Core Rules (E, F, W)**:
- `E` (pycodestyle errors): PEP 8 violations that affect readability
- `F` (Pyflakes): Unused imports, undefined variables, syntax errors
- `W` (pycodestyle warnings): Style issues that can lead to bugs

**Code Quality (I, N, UP, B)**:
- `I` (isort): Consistent import ordering
- `N` (pep8-naming): Proper naming conventions (classes, functions, variables)
- `UP` (pyupgrade): Modern Python syntax (f-strings, type hints)
- `B` (flake8-bugbear): Common bug patterns and anti-patterns

**Bug Prevention (A, C4, DTZ, T10, EM)**:
- `A` (flake8-builtins): Avoid shadowing built-in names
- `C4` (flake8-comprehensions): Proper list/dict comprehensions
- `DTZ` (flake8-datetimez): Timezone-aware datetime usage
- `T10` (flake8-debugger): Catch forgotten debugger statements
- `EM` (flake8-errmsg): Proper exception message formatting

**Code Clarity (ISC, ICN, PIE, Q, RET, SIM)**:
- `ISC` (flake8-implicit-str-concat): Explicit string concatenation
- `ICN` (flake8-import-conventions): Standard import conventions (pd, np)
- `PIE` (flake8-pie): Misc improvements and simplifications
- `Q` (flake8-quotes): Consistent quote style
- `RET` (flake8-return): Proper return statement usage
- `SIM` (flake8-simplify): Code simplification suggestions

**Best Practices (TID, ARG, PTH)**:
- `TID` (flake8-tidy-imports): Clean import structure
- `ARG` (flake8-unused-arguments): Catch unused function arguments
- `PTH` (flake8-use-pathlib): Modern pathlib instead of os.path

**Framework-Specific (PD, PT, NPY)**:
- `PD` (pandas-vet): Pandas best practices (if using pandas)
- `PT` (flake8-pytest-style): Pytest best practices (for test files)
- `NPY` (NumPy): NumPy-specific rules (if using numpy)

**Performance & Ruff-Specific (PL, PERF, RUF)**:
- `PL` (Pylint): Additional code quality checks
- `PERF` (Perflint): Performance anti-patterns
- `RUF` (Ruff-specific): Ruff's own custom rules

**Note on Strictness**: While this configuration is comprehensive, it represents industry best practices. Users can customize their generated `pyproject.toml` after creation to adjust rules based on their project's needs. The opinionated defaults ensure high code quality from the start.

### Example Workflow Output

After implementation, the `_reusable-test-build.yml` will contain:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install build
    pip install .[test]

- name: Lint with Ruff
  run: |
    python -m pip install ruff
    ruff check .
    ruff format --check .

- name: Run tests with pytest
  run: python -m pytest ${{ inputs.test_path }}
```

## Implementation Plan

### Phase 1: Preparation and Template Updates

**Critical**: The generator codebase must be made lint-compliant BEFORE updating templates to avoid circular dependency during implementation.

0. **Fix Generator Codebase Linting Violations** (prerequisite)
   - Add Ruff to this project's `pyproject.toml` dev dependencies
   - Run `ruff check .` and `ruff format --check .` on the generator codebase
   - Fix all linting violations using `ruff check --fix .` and `ruff format .`
   - Manually address any remaining issues
   - Verify codebase is fully lint-compliant before proceeding

1. **Update Templates** (after codebase is clean)
   - Update `_reusable_test_build.yml.j2` to add linting step (no conditionals)
   - Update `pyproject.toml.j2` with Ruff configuration and dev dependency

2. **Update Tests**
   - Update `test_generator.py` to verify linting step is always present in generated workflows
   - Verify tests pass with clean codebase

### Phase 2: Dogfooding

**Note**: Steps 1-2 from Phase 1 (fixing generator codebase) are prerequisites completed BEFORE this phase.

1. Regenerate this project's own workflows using the updated templates
2. Verify Ruff configuration is already in this project's `pyproject.toml` (from Phase 1, Step 0)
3. Verify linting passes on the generator codebase (already fixed in Phase 1, Step 0)
4. Test workflows end-to-end with linting enabled

### Phase 3: Documentation
1. Update README.md with linting feature documentation
2. Add section on customizing Ruff configuration
3. Add dogfooding section explaining how this project uses its own generated workflows
4. Update examples to show linting in action
5. Add troubleshooting guide for common linting issues

## Testing Strategy

### Unit Tests

1. **Template Rendering Tests** (`test_generator.py`)
   - Verify `_reusable_test_build.yml.j2` always renders with linting step
   - Verify linting step is placed before test step
   - Verify `pyproject.toml.j2` includes Ruff configuration and dependency
   - Verify Ruff configuration contains expected rules and settings

2. **Workflow Generation Tests** (`test_generator.py`)
   - Test `generate_workflows()` creates files with linting included
   - Verify generated workflow files contain "Lint with Ruff" step
   - Verify generated pyproject.toml contains Ruff in dev dependencies

### Integration Tests

1. **End-to-End Generation Tests**
   - Generate complete set of workflows in test directory
   - Parse generated YAML and verify linting step exists
   - Verify linting commands are correct (`ruff check .` and `ruff format --check .`)

2. **Dogfooding Tests**
   - Run this project's own generated workflows (with linting)
   - Verify linting passes on the generator codebase
   - Ensure no linting errors in pypi-workflow-generator code itself

## Migration Guide for Existing Users

### For Users with Existing Workflows

Existing workflows will NOT be automatically updated. Users have two options:

**Option 1: Regenerate workflows (recommended)**

Simply regenerate your workflows to get linting automatically:

```bash
hitoshura25-pypi-workflow-generator
```

This will create new workflow files with linting included by default.

**If you don't want linting:**
After regenerating, manually delete the linting step from `.github/workflows/_reusable-test-build.yml` and remove `ruff` from your `pyproject.toml`.

**Option 2: Manual update**

Add the linting step to `.github/workflows/_reusable-test-build.yml` after the "Install dependencies" step:

```yaml
- name: Lint with Ruff
  run: |
    python -m pip install ruff
    ruff check .
    ruff format --check .
```

Add to `pyproject.toml` (see "Proposed Solution" section above for the full Ruff configuration including all rules and formatting settings):

```toml
[project.optional-dependencies]
dev = [
    # ... existing deps ...
    "ruff",
]

[tool.ruff]
# Add the complete configuration from the "Proposed Solution > pyproject.toml.j2" section above
```

## Configuration Examples

### Minimal Configuration

```toml
[tool.ruff]
select = ["E", "F"]  # Only errors and warnings
line-length = 88
```

### Strict Configuration

```toml
[tool.ruff]
select = ["ALL"]  # Enable all rules
ignore = ["D"]    # Except docstring rules

[tool.ruff.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests
```

### Custom Exclusions

```toml
[tool.ruff]
extend-exclude = ["migrations", "old_code"]
```

## Rollout Plan

1. **v0.x.x**: Current version (no linting)
2. **v0.x+1.0**: Add linting feature (always enabled in generated workflows)
3. **Dogfooding**: Regenerate this project's workflows with linting
4. **Documentation**: Update README with linting information and migration guide
5. **Communication**: Announce in release notes, update PyPI description

## Dependencies

### New Dependencies
- **Ruff**: Added to generated pyproject.toml dev dependencies
- **No new build/runtime dependencies** for pypi-workflow-generator itself

### Version Constraints
- Ruff: No specific version constraint (use latest)
- Compatible with Python 3.8+ (same as current project requirements)

## Risks and Mitigations

### Risk 1: Breaking Changes for Existing Users
**Impact**: Low to Medium
**Mitigation**:
- Existing workflows continue to work (no automatic updates)
- Clear migration guide in documentation
- Workflows can be regenerated easily
- Users can manually delete linting step if unwanted
- Opinionated approach is simpler and follows best practices

### Risk 2: False Positives from Ruff
**Impact**: Low
**Mitigation**:
- Use conservative default rule set
- Users can customize via pyproject.toml
- Clear documentation on configuration options
- Ruff is widely used and well-tested

### Risk 3: Performance Impact
**Impact**: Low
**Mitigation**:
- Ruff is extremely fast (typically <5 seconds)
- Runs before tests (fail fast)
- Users can disable if needed

### Risk 4: Configuration Complexity
**Impact**: Low
**Mitigation**:
- Provide sensible defaults
- Document common configuration patterns
- Link to official Ruff documentation

## Success Metrics

1. **Adoption**: % of newly generated projects using linting (target: >80%)
2. **Performance**: Average linting step duration (target: <30 seconds)
3. **User Satisfaction**: GitHub issues/feedback about linting feature
4. **Code Quality**: Reduction in common Python errors in generated projects

## Design Decisions

1. **Q: Should linting be configurable or always enabled?**
   - **A: Always enabled** - Opinionated approach is simpler, follows best practices, and reduces code complexity. Users who don't want linting can manually remove the step from generated files.

2. **Q: Should we support other linters besides Ruff?**
   - **A: No** - Ruff is comprehensive, fast, and well-maintained. Supporting multiple linters adds complexity without significant benefit.

3. **Q: Should linting errors block the workflow or just warn?**
   - **A: Block (fail the workflow)** - Enforces code quality standards and prevents merging code with issues.

4. **Q: Should we add auto-fixing capabilities?**
   - **A: Not in initial version** - Auto-fixing in CI could lead to unexpected changes. Users can run `ruff check --fix` locally when needed.

## Future Enhancements

1. **Auto-fix PR bot**: Automatically create PRs with linting fixes
2. **Custom rule sets**: Predefined configurations for different project types
3. **Pre-commit hooks**: Generate pre-commit configuration alongside workflows
4. **IDE integration guidance**: Documentation on VS Code/PyCharm Ruff integration
5. **Type checking**: Add mypy or pyright support in future versions

## Dogfooding Strategy

### Why Dogfooding Matters

Dogfooding (using our own tool) is critical for this feature because:
- **Validates the feature works** - If we can't use it ourselves, users can't either
- **Builds confidence** - Users see we trust our own generated workflows
- **Catches edge cases** - Real-world usage on this codebase reveals issues
- **Documents by example** - Users can see actual working examples in our repo
- **Ensures quality** - We won't ship linting that breaks our own builds

### Implementation Steps

1. **Add Ruff to Project Dependencies**

   Update this project's `pyproject.toml` to include Ruff as a dev dependency and add the Ruff configuration.

   See the "Proposed Solution > pyproject.toml.j2" section above for the complete Ruff configuration to add.

   Key additions:
   ```toml
   [project.optional-dependencies]
   dev = [
       "twine",
       "wheel",
       "setuptools_scm",
       "build",
       "ruff",  # NEW
   ]

   [tool.ruff]
   # Add complete configuration from "Proposed Solution" section
   # (includes comprehensive rule set, exclusions, and formatting options)
   ```

2. **Fix Existing Linting Issues**

   **CRITICAL TIMING**: This step must be completed BEFORE implementing the linting feature in templates (Phase 1, Step 0). This prevents a circular dependency where the generator's workflows would fail due to linting violations in the generator's own code.

   ```bash
   # Install ruff
   pip install ruff

   # Check for issues
   ruff check .
   ruff format --check .

   # Auto-fix what can be fixed
   ruff check --fix .
   ruff format .

   # Manually fix remaining issues
   ```

   Only proceed to template updates (step 3 below) after the generator codebase is fully lint-compliant.

3. **Regenerate Workflows with Linting**

   After implementing the linting feature:
   ```bash
   # Regenerate this project's workflows using the new templates
   hitoshura25-pypi-workflow-generator \
     --python-version 3.11 \
     --test-path hitoshura25_pypi_workflow_generator/
   ```

   This will create workflows that include the linting step.

4. **Verify Workflows Pass**

   - Create a test branch
   - Push changes to trigger workflow
   - Verify linting step passes
   - Fix any issues found
   - Merge when green

5. **Document in README**

   Add/update the "Dogfooding" section in README.md:

   ```markdown
   ## Dogfooding

   This project uses itself to generate its own GitHub Actions workflows! The workflow files at:
   - `.github/workflows/_reusable-test-build.yml`
   - `.github/workflows/release.yml`
   - `.github/workflows/test-pr.yml`

   Were all created by running:

   ```bash
   hitoshura25-pypi-workflow-generator \
     --python-version 3.11 \
     --test-path hitoshura25_pypi_workflow_generator/
   ```

   **New in v0.x+1.0**: The generated workflows now include Ruff linting by default!

   This ensures:
   - ✅ The tool actually works (we use it ourselves)
   - ✅ All features including linting are tested in production
   - ✅ The templates stay consistent with real-world usage
   - ✅ We practice what we preach
   - ✅ Users can see real examples of the generated output
   ```

### Expected Outcomes

After dogfooding:
- ✅ This project's workflows include linting step
- ✅ This project's code passes Ruff linting
- ✅ CI/CD pipeline enforces code quality on all PRs
- ✅ Users have a working reference implementation
- ✅ Any issues with linting integration are discovered and fixed

### Testing Dogfooding

1. **Local Testing**:
   ```bash
   # Verify linting works locally
   ruff check hitoshura25_pypi_workflow_generator/
   ruff format --check hitoshura25_pypi_workflow_generator/
   ```

2. **CI Testing**:
   - Create PR with intentional linting issue
   - Verify workflow fails at linting step
   - Fix issue and verify workflow passes

3. **Release Testing**:
   - Ensure release workflow passes with linting
   - Verify published package was built with linting validation

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [GitHub Actions: Python Application](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [PEP 8: Style Guide for Python Code](https://peps.python.org/pep-0008/)
