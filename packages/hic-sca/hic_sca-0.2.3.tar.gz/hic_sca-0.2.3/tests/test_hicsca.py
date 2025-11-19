"""
Test suite for HiC-SCA package.

Tests include:
- Data availability checks
- Result structure validation
- Regression testing against reference results
- Field-by-field comparison
"""

import pytest
import numpy as np
from pathlib import Path


class TestDataAvailability:
    """Test that required test data files are available."""

    def test_hic_file_exists(self, test_data_available):
        """Test that test.hic file exists."""
        if not test_data_available['hic_file']:
            pytest.skip("test.hic not found. See tests/test_data/DOWNLOAD.md")

        assert test_data_available['hic_file'], \
            "test.hic file not found in tests/test_data/"

    def test_ref_file_exists(self, test_data_available):
        """Test that ref.h5 file exists."""
        if not test_data_available['ref_file']:
            pytest.skip("ref.h5 not found. See tests/test_data/DOWNLOAD.md")

        assert test_data_available['ref_file'], \
            "ref.h5 file not found in tests/test_data/"


class TestResultStructure:
    """Test the structure of HiC-SCA results dictionary."""

    def test_results_has_resolution_keys(self, reference_results, reference_resolution_list):
        """Test that results dictionary has resolution keys at top level."""
        assert len(reference_resolution_list) > 0, \
            "No resolutions found in reference results"

        for resolution in reference_resolution_list:
            assert resolution in reference_results, \
                f"Resolution {resolution} missing from results"
            assert isinstance(reference_results[resolution], dict), \
                f"results[{resolution}] should be a dictionary"

    def test_results_has_chromosome_keys(self, reference_results, reference_resolution_list,
                                         reference_chr_names):
        """Test that results[resolution] has chromosome keys."""
        assert len(reference_chr_names) > 0, \
            "No chromosomes found in reference results"

        for resolution in reference_resolution_list:
            for chr_name in reference_chr_names:
                assert chr_name in reference_results[resolution], \
                    f"Chromosome {chr_name} missing from results[{resolution}]"

    def test_result_dict_has_required_fields(self, reference_results, reference_resolution_list,
                                             reference_chr_names):
        """Test that each result dictionary has required fields."""
        # Fields that are always present regardless of Success status
        always_present_fields = [
            'Success',
            'Eig Converged',
            'deg',
            'OE_normed_diag',
            'non_zero_not_included_bool',
            'include_bool',
            'cutoff'
        ]

        # Fields that are only present when Success=True
        success_only_fields = [
            'assigned_AB_compartment',
            'selected_eig_idx',
            'modified_inter_eigval_score',
            'unmodified_inter_AB_score',
            'eigvals',
            'eigenvects'
        ]

        for resolution in reference_resolution_list:
            for chr_name in reference_chr_names:
                result = reference_results[resolution][chr_name]

                # Check fields that should always be present
                for field in always_present_fields:
                    assert field in result, \
                        f"Field '{field}' missing for {chr_name} at {resolution}"

                # If successful, check success-only fields
                if result['Success']:
                    for field in success_only_fields:
                        assert field in result, \
                            f"Field '{field}' missing for successful result {chr_name} at {resolution}"

    def test_assigned_AB_compartment_is_ndarray(self, reference_results, reference_resolution_list,
                                            reference_chr_names):
        """Test that assigned_AB_compartment is a numpy array."""
        for resolution in reference_resolution_list:
            for chr_name in reference_chr_names:
                result = reference_results[resolution][chr_name]

                if result['Success']:
                    assert isinstance(result['assigned_AB_compartment'], np.ndarray), \
                        f"assigned_AB_compartment should be numpy array for {chr_name} at {resolution}"

    def test_selected_eig_idx_is_int(self, reference_results, reference_resolution_list,
                                    reference_chr_names):
        """Test that selected_eig_idx is an integer."""
        for resolution in reference_resolution_list:
            for chr_name in reference_chr_names:
                result = reference_results[resolution][chr_name]

                if result['Success']:
                    assert isinstance(result['selected_eig_idx'], (int, np.integer)), \
                        f"selected_eig_idx should be integer for {chr_name} at {resolution}"
                    assert 1 <= result['selected_eig_idx'] <= 10, \
                        f"selected_eig_idx should be 1-10 for {chr_name} at {resolution}"


@pytest.mark.slow
class TestRegressionComparison:
    """
    Regression tests comparing computed results against reference results.

    These tests run the full HiC-SCA pipeline and are marked as slow.
    """

    def test_resolutions_match(self, computed_resolution_list, reference_resolution_list):
        """Test that computed and reference results have same resolutions."""
        assert computed_resolution_list == reference_resolution_list, \
            f"Resolution mismatch: computed={computed_resolution_list}, " \
            f"reference={reference_resolution_list}"

    def test_chromosomes_match(self, computed_chr_names, reference_chr_names):
        """Test that computed and reference results have same chromosomes."""
        assert computed_chr_names == reference_chr_names, \
            f"Chromosome mismatch: computed={computed_chr_names}, " \
            f"reference={reference_chr_names}"

    def test_success_status_matches(self, computed_results, reference_results,
                                   computed_resolution_list, computed_chr_names):
        """Test that Success status matches between computed and reference."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_success = computed_results[resolution][chr_name]['Success']
                reference_success = reference_results[resolution][chr_name]['Success']

                assert computed_success == reference_success, \
                    f"Success status mismatch for {chr_name} at {resolution}: " \
                    f"computed={computed_success}, reference={reference_success}"

    def test_compartment_predictions_match(self, computed_results, reference_results,
                                          computed_resolution_list, computed_chr_names):
        """Test that compartment predictions match within tolerance."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_result = computed_results[resolution][chr_name]
                reference_result = reference_results[resolution][chr_name]

                # Only compare if both succeeded
                if computed_result['Success'] and reference_result['Success']:
                    computed_comp = computed_result['assigned_AB_compartment']
                    reference_comp = reference_result['assigned_AB_compartment']

                    # Check shapes match
                    assert computed_comp.shape == reference_comp.shape, \
                        f"Shape mismatch for {chr_name} at {resolution}: " \
                        f"computed={computed_comp.shape}, reference={reference_comp.shape}"

                    # Check values match within tolerance
                    # Use allclose for floating point comparison
                    assert np.allclose(computed_comp, reference_comp, rtol=1e-5, atol=1e-5), \
                        f"Compartment values mismatch for {chr_name} at {resolution}"

    def test_selected_eig_idx_matches(self, computed_results, reference_results,
                                    computed_resolution_list, computed_chr_names):
        """Test that selected eigenvector indices match."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_result = computed_results[resolution][chr_name]
                reference_result = reference_results[resolution][chr_name]

                if computed_result['Success'] and reference_result['Success']:
                    computed_eig = computed_result['selected_eig_idx']
                    reference_eig = reference_result['selected_eig_idx']

                    assert computed_eig == reference_eig, \
                        f"Selected eigenvector index mismatch for {chr_name} at {resolution}: " \
                        f"computed=Eig{computed_eig}, reference=Eig{reference_eig}"

    def test_scores_match(self, computed_results, reference_results,
                         computed_resolution_list, computed_chr_names):
        """Test that modified and unmodified scores match within tolerance."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_result = computed_results[resolution][chr_name]
                reference_result = reference_results[resolution][chr_name]

                if computed_result['Success'] and reference_result['Success']:
                    # Check modified score
                    computed_modified = computed_result['modified_inter_eigval_score']
                    reference_modified = reference_result['modified_inter_eigval_score']

                    assert np.isclose(computed_modified, reference_modified, rtol=1e-5, atol=1e-5), \
                        f"Modified score mismatch for {chr_name} at {resolution}: " \
                        f"computed={computed_modified:.6f}, reference={reference_modified:.6f}"

                    # Check unmodified score
                    computed_unmodified = computed_result['unmodified_inter_AB_score']
                    reference_unmodified = reference_result['unmodified_inter_AB_score']

                    assert np.isclose(computed_unmodified, reference_unmodified, rtol=1e-5, atol=1e-5), \
                        f"Unmodified score mismatch for {chr_name} at {resolution}: " \
                        f"computed={computed_unmodified:.6f}, reference={reference_unmodified:.6f}"


class TestFieldComparison:
    """Field-by-field comparison tests for specific result dictionary fields."""

    def test_eigvals_match(self, computed_results, reference_results,
                          computed_resolution_list, computed_chr_names):
        """Test that eigenvalues match within tolerance."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_result = computed_results[resolution][chr_name]
                reference_result = reference_results[resolution][chr_name]

                if computed_result['Success'] and reference_result['Success']:
                    computed_eigvals = computed_result['eigvals']
                    reference_eigvals = reference_result['eigvals']

                    assert computed_eigvals.shape == reference_eigvals.shape, \
                        f"Eigvals shape mismatch for {chr_name} at {resolution}"

                    assert np.allclose(computed_eigvals, reference_eigvals, rtol=1e-5, atol=1e-5), \
                        f"Eigenvalues mismatch for {chr_name} at {resolution}"

    def test_include_bool_match(self, computed_results, reference_results,
                               computed_resolution_list, computed_chr_names):
        """Test that include_bool arrays match."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_result = computed_results[resolution][chr_name]
                reference_result = reference_results[resolution][chr_name]

                if computed_result['Success'] and reference_result['Success']:
                    computed_include = computed_result['include_bool']
                    reference_include = reference_result['include_bool']

                    assert computed_include.shape == reference_include.shape, \
                        f"include_bool shape mismatch for {chr_name} at {resolution}"

                    assert np.array_equal(computed_include, reference_include), \
                        f"include_bool values mismatch for {chr_name} at {resolution}"

    def test_cutoff_match(self, computed_results, reference_results,
                         computed_resolution_list, computed_chr_names):
        """Test that cutoff values match within tolerance."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_result = computed_results[resolution][chr_name]
                reference_result = reference_results[resolution][chr_name]

                # Cutoff is available even if processing failed after filtering
                if 'cutoff' in computed_result and 'cutoff' in reference_result:
                    computed_cutoff = computed_result['cutoff']
                    reference_cutoff = reference_result['cutoff']

                    assert np.isclose(computed_cutoff, reference_cutoff, rtol=1e-5, atol=1e-5), \
                        f"Cutoff mismatch for {chr_name} at {resolution}: " \
                        f"computed={computed_cutoff:.6f}, reference={reference_cutoff:.6f}"

    def test_eig_converged_match(self, computed_results, reference_results,
                                computed_resolution_list, computed_chr_names):
        """Test that Eig Converged status matches."""
        for resolution in computed_resolution_list:
            for chr_name in computed_chr_names:
                computed_converged = computed_results[resolution][chr_name]['Eig Converged']
                reference_converged = reference_results[resolution][chr_name]['Eig Converged']

                assert computed_converged == reference_converged, \
                    f"Eig Converged mismatch for {chr_name} at {resolution}: " \
                    f"computed={computed_converged}, reference={reference_converged}"


@pytest.mark.slow
class TestCrossResolutionAnalysis:
    """
    Test cross-resolution analysis using CrossResolutionAnalyzer.

    These tests verify that the cross-resolution MCC correlation matrices
    match between computed and reference results.
    """

    def test_reference_analyzer_has_mcc_matrices(self, reference_cross_res_analyzer):
        """Test that reference analyzer has computed MCC matrices."""
        assert hasattr(reference_cross_res_analyzer, 'mcc_matrices'), \
            "Reference analyzer missing mcc_matrices attribute"
        assert len(reference_cross_res_analyzer.mcc_matrices) > 0, \
            "Reference analyzer has empty mcc_matrices"

    def test_computed_analyzer_has_mcc_matrices(self, computed_cross_res_analyzer):
        """Test that computed analyzer has computed MCC matrices."""
        assert hasattr(computed_cross_res_analyzer, 'mcc_matrices'), \
            "Computed analyzer missing mcc_matrices attribute"
        assert len(computed_cross_res_analyzer.mcc_matrices) > 0, \
            "Computed analyzer has empty mcc_matrices"

    def test_mcc_matrices_have_genome_wide_key(self, reference_cross_res_analyzer,
                                               computed_cross_res_analyzer):
        """Test that MCC matrices have 'all' key for genome-wide results."""
        assert 'all' in reference_cross_res_analyzer.mcc_matrices, \
            "Reference MCC matrices missing 'all' key for genome-wide results"
        assert 'all' in computed_cross_res_analyzer.mcc_matrices, \
            "Computed MCC matrices missing 'all' key for genome-wide results"

    def test_genome_wide_mcc_matrix_matches(self, reference_cross_res_analyzer,
                                           computed_cross_res_analyzer):
        """Test that genome-wide MCC correlation matrix matches."""
        ref_mcc = reference_cross_res_analyzer.mcc_matrices['all']
        comp_mcc = computed_cross_res_analyzer.mcc_matrices['all']

        # Check shapes match
        assert ref_mcc.shape == comp_mcc.shape, \
            f"Genome-wide MCC matrix shape mismatch: " \
            f"reference={ref_mcc.shape}, computed={comp_mcc.shape}"

        # Check values match within tolerance
        # Note: -1 values indicate N/A (incompatible resolution pairs)
        # Only compare valid MCC values (>= 0)
        valid_mask = (ref_mcc >= 0) & (comp_mcc >= 0)

        assert np.allclose(ref_mcc[valid_mask], comp_mcc[valid_mask],
                          rtol=1e-5, atol=1e-5), \
            "Genome-wide MCC values mismatch"

    def test_per_chromosome_mcc_matrices_match(self, reference_cross_res_analyzer,
                                              computed_cross_res_analyzer,
                                              reference_chr_names):
        """Test that per-chromosome MCC correlation matrices match."""
        for chr_name in reference_chr_names:
            # Skip if chromosome not in MCC matrices
            if chr_name not in reference_cross_res_analyzer.mcc_matrices:
                continue
            if chr_name not in computed_cross_res_analyzer.mcc_matrices:
                pytest.fail(f"Chromosome {chr_name} missing from computed MCC matrices")

            ref_mcc = reference_cross_res_analyzer.mcc_matrices[chr_name]
            comp_mcc = computed_cross_res_analyzer.mcc_matrices[chr_name]

            # Check shapes match
            assert ref_mcc.shape == comp_mcc.shape, \
                f"MCC matrix shape mismatch for {chr_name}: " \
                f"reference={ref_mcc.shape}, computed={comp_mcc.shape}"

            # Check values match within tolerance (only valid MCC values >= 0)
            valid_mask = (ref_mcc >= 0) & (comp_mcc >= 0)

            assert np.allclose(ref_mcc[valid_mask], comp_mcc[valid_mask],
                              rtol=1e-5, atol=1e-5), \
                f"MCC values mismatch for {chr_name}"

    def test_orientation_matrices_match(self, reference_cross_res_analyzer,
                                       computed_cross_res_analyzer):
        """Test that orientation agreement matrices match."""
        # Test genome-wide orientation matrix
        ref_orient = reference_cross_res_analyzer.orientation_matrices['all']
        comp_orient = computed_cross_res_analyzer.orientation_matrices['all']

        assert ref_orient.shape == comp_orient.shape, \
            "Genome-wide orientation matrix shape mismatch"

        assert np.array_equal(ref_orient, comp_orient), \
            "Genome-wide orientation agreement values mismatch"

    def test_resolutions_match(self, reference_cross_res_analyzer,
                              computed_cross_res_analyzer):
        """Test that resolutions match between reference and computed analyzers."""
        ref_resolutions = sorted(reference_cross_res_analyzer.resolutions)
        comp_resolutions = sorted(computed_cross_res_analyzer.resolutions)

        assert ref_resolutions == comp_resolutions, \
            f"Resolution mismatch: reference={ref_resolutions}, " \
            f"computed={comp_resolutions}"
