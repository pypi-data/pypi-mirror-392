"""Tests for build string normalization."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))
from conda_env_replicator import normalize_build_string


class TestNormalizeBuildString:
    """Test cases for normalize_build_string function."""

    def test_remove_regular_build(self):
        """Regular build strings should be removed."""
        assert normalize_build_string("py39h107f55c_0") == ""
        assert normalize_build_string("h1234567_0") == ""
        assert normalize_build_string("pyhd8ed1ab_0") == ""

    def test_preserve_cuda_major_minor(self):
        """CUDA versions should be preserved with wildcards."""
        assert normalize_build_string("cuda11.2_0") == "*cuda11*"
        assert normalize_build_string("cuda11.8_0") == "*cuda11*"
        assert normalize_build_string("cuda12.1_0") == "*cuda12*"

    def test_preserve_cuda_major_only(self):
        """CUDA major versions should be preserved."""
        assert normalize_build_string("cuda11_0") == "*cuda11*"
        assert normalize_build_string("cuda12_0") == "*cuda12*"

    def test_preserve_cuda_in_complex_build(self):
        """CUDA in complex build strings should be extracted."""
        assert normalize_build_string("gd367332_cuda11.2_0") == "*cuda11*"
        assert normalize_build_string("py39_cuda11.2_0") == "*cuda11*"

    def test_preserve_gpu_keyword(self):
        """GPU keyword should be preserved with wildcards."""
        assert normalize_build_string("gpu") == "*gpu*"
        assert normalize_build_string("gpu_0") == "*gpu*"
        assert normalize_build_string("h1234_gpu") == "*gpu*"

    def test_empty_build(self):
        """Empty build strings should return empty."""
        assert normalize_build_string("") == ""
        assert normalize_build_string(None) == ""

    def test_case_insensitive_gpu(self):
        """GPU matching should be case-insensitive."""
        assert normalize_build_string("GPU") == "*gpu*"
        assert normalize_build_string("Gpu_0") == "*gpu*"


class TestPackageSpecParsing:
    """Test package specification parsing."""

    def test_package_only(self):
        """Test parsing package name only."""
        spec = "numpy"
        parts = spec.split("=")
        assert parts[0] == "numpy"
        assert len(parts) == 1

    def test_package_with_version(self):
        """Test parsing package with version."""
        spec = "numpy=1.21.2"
        parts = spec.split("=")
        assert parts[0] == "numpy"
        assert parts[1] == "1.21.2"
        assert len(parts) == 2

    def test_package_with_version_and_build(self):
        """Test parsing package with version and build."""
        spec = "numpy=1.21.2=py39h20f2e39_0"
        parts = spec.split("=")
        assert parts[0] == "numpy"
        assert parts[1] == "1.21.2"
        assert parts[2] == "py39h20f2e39_0"
        assert len(parts) == 3

    def test_package_with_channel(self):
        """Test parsing package with channel prefix."""
        spec = "conda-forge::numpy=1.21.2"
        if "::" in spec:
            channel, pkg = spec.split("::")
            assert channel == "conda-forge"
            assert pkg == "numpy=1.21.2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
