"""
Pytest configuration and fixtures for HiC-SCA tests.

Provides session-scoped fixtures for loading test data and running HiC-SCA pipeline.
"""

import pytest
from pathlib import Path
from hicsca.formats import from_hdf5
from hicsca.hicsca import HiCSCA
from hicsca.evals import CrossResolutionAnalyzer


# Test data paths
TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "test_data"
TEST_HIC_FILE = TEST_DATA_DIR / "ENCFF216ZNY_Intra_Only.hic"
REF_RESULTS_FILE = TEST_DATA_DIR / "reference.h5"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (regression tests)"
    )


@pytest.fixture(scope="session")
def test_data_available():
    """
    Check if test data files are available.

    Returns
    -------
    dict
        Dictionary with 'hic_file' and 'ref_file' boolean availability status
    """
    return {
        'hic_file': TEST_HIC_FILE.exists(),
        'ref_file': REF_RESULTS_FILE.exists()
    }


@pytest.fixture(scope="session")
def reference_results(test_data_available):
    """
    Load reference results from ref.h5 file.

    Session-scoped to load only once per test session.

    Returns
    -------
    dict or None
        Reference results dictionary with structure: results[resolution][chr_name]
        Returns None if ref.h5 is not available.
    """
    if not test_data_available['ref_file']:
        pytest.skip(f"Reference results file not found: {REF_RESULTS_FILE}")

    # Load HiCSCA instance and extract just the results dict for backward compatibility
    hicsca_inst = from_hdf5(str(REF_RESULTS_FILE))
    return hicsca_inst.results


@pytest.fixture(scope="session")
def hicsca_instance(test_data_available):
    """
    Create and process HiCSCA instance for testing.

    Session-scoped to run only once per test session.
    This is an expensive operation that can take several minutes.

    Returns
    -------
    HiCSCA or None
        Processed HiCSCA instance with results available in .results attribute
        Returns None if test.hic is not available.
    """
    if not test_data_available['hic_file']:
        pytest.skip(f"Test Hi-C file not found: {TEST_HIC_FILE}")

    # Initialize HiC-SCA with specific resolutions for testing
    hicsca_inst = HiCSCA(
        str(TEST_HIC_FILE),
        chr_names=None,  # Auto-detect all chromosomes
        resolutions=[500000, 250000, 100000, 50000],
        data_type="observed",
        norm_type="NONE",
        smoothing_cutoff=400
    )

    # Process all chromosomes at all resolutions
    hicsca_inst.process_all_chromosomes()

    return hicsca_inst


@pytest.fixture(scope="session")
def computed_results(hicsca_instance):
    """
    Get computed results dictionary from processed HiCSCA instance.

    Derived from hicsca_instance fixture. Session-scoped for consistency.

    Returns
    -------
    dict or None
        Computed results dictionary with structure: results[resolution][chr_name]
        Returns None if hicsca_instance is not available.
    """
    return hicsca_instance.results


@pytest.fixture
def reference_resolution_list(reference_results):
    """
    Extract list of resolutions from reference results.

    Returns
    -------
    list
        Sorted list of resolutions (integers)
    """
    if reference_results is None:
        return []
    return sorted(reference_results.keys())


@pytest.fixture
def reference_chr_names(reference_results, reference_resolution_list):
    """
    Extract list of chromosome names from reference results.

    Returns
    -------
    list
        Sorted list of chromosome names
    """
    if reference_results is None or not reference_resolution_list:
        return []

    first_res = reference_resolution_list[0]
    return sorted(reference_results[first_res].keys())


@pytest.fixture
def computed_resolution_list(computed_results):
    """
    Extract list of resolutions from computed results.

    Returns
    -------
    list
        Sorted list of resolutions (integers)
    """
    if computed_results is None:
        return []
    return sorted(computed_results.keys())


@pytest.fixture
def computed_chr_names(computed_results, computed_resolution_list):
    """
    Extract list of chromosome names from computed results.

    Returns
    -------
    list
        Sorted list of chromosome names
    """
    if computed_results is None or not computed_resolution_list:
        return []

    first_res = computed_resolution_list[0]
    return sorted(computed_results[first_res].keys())


@pytest.fixture(scope="session")
def reference_cross_res_analyzer(reference_results):
    """
    Create CrossResolutionAnalyzer from reference results.

    Session-scoped to analyze only once per test session.

    Returns
    -------
    CrossResolutionAnalyzer or None
        Analyzer instance with cross-resolution MCC matrices computed
        Returns None if reference results not available.
    """
    if reference_results is None:
        pytest.skip("Reference results not available")

    analyzer = CrossResolutionAnalyzer(reference_results)
    analyzer.analyze()  # Compute cross-resolution MCC matrices
    return analyzer


@pytest.fixture(scope="session")
def computed_cross_res_analyzer(computed_results):
    """
    Create CrossResolutionAnalyzer from computed results.

    Session-scoped to analyze only once per test session.

    Returns
    -------
    CrossResolutionAnalyzer or None
        Analyzer instance with cross-resolution MCC matrices computed
        Returns None if computed results not available.
    """
    if computed_results is None:
        pytest.skip("Computed results not available")

    analyzer = CrossResolutionAnalyzer(computed_results)
    analyzer.analyze()  # Compute cross-resolution MCC matrices
    return analyzer
