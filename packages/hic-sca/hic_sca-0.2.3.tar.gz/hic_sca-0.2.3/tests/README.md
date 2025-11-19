# HiC-SCA Test Suite

This directory contains the test suite for the HiC-SCA package.
Please run all commands in the parent "hicsca" folder

## Setup

### 1. Install Test Dependencies

Install the hic-sca package with test dependencies:
```bash
pip install -e ".[tests]"
```

This installs pytest and other testing tools required for running the test suite.

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories

```bash
# Only data availability tests
pytest tests/test_hic_sca.py::TestDataAvailability

# Only structure tests
pytest tests/test_hic_sca.py::TestResultStructure
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=hic_sca --cov-report=html
```

Then open `htmlcov/index.html` in a browser to view the coverage report.

## Test Structure

### Test Files

- `conftest.py` - Pytest fixtures and configuration
- `test_hic_sca.py` - Main test suite
- `test_data/` - Directory for test data files

### Test Classes

#### TestDataAvailability
Verifies that required test data files exist before running other tests.

#### TestResultStructure
Fast structural tests that verify:
- Results dictionary structure (`results[resolution][chr_name]`)
- Presence of required fields (Success, assigned_AB_compartment, etc.)
- Array shapes and data types

#### TestRegressionComparison (marked as `@pytest.mark.slow`)
Regression tests that run HiC-SCA on test.hic and compare against reference results:
- Compartment predictions match (using numpy.allclose)
- Selected eigenvector indices match
- Scores match within tolerance

#### TestFieldComparison
Field-by-field comparison tests for specific result dictionary fields.

## Fixtures

### `reference_results` (session-scoped)
Loads ref.h5 once per test session and caches it.

### `computed_results` (session-scoped)
Runs HiC-SCA on test.hic once per test session and caches results.

Session-scoped fixtures ensure expensive operations (loading data, running HiC-SCA) only happen once per test run.

## Test Markers

The test suite uses pytest markers to categorize tests:
- `@pytest.mark.slow` - Tests that take significant time to run (regression tests)

## Contributing

When adding new features to HiC-SCA:
1. Add corresponding tests to `test_hic_sca.py`
2. Ensure all existing tests still pass
3. Add test markers (`@pytest.mark.slow`) for expensive tests
4. Update this README if adding new test categories
