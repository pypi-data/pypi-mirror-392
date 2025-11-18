"""
Tests for package initialization and exports
"""
import pytest
from osclient import OpenStack, OpenStack2, __version__, __all__


class TestPackageExports:
    """Test package-level exports"""

    def test_version_exported(self):
        """Test that __version__ is exported"""
        assert __version__ == '0.1.0'

    def test_all_exported(self):
        """Test that __all__ contains expected exports"""
        assert 'OpenStack' in __all__
        assert 'OpenStack2' in __all__
        assert len(__all__) == 2

    def test_openstack_class_importable(self):
        """Test that OpenStack class can be imported"""
        from osclient import OpenStack
        assert OpenStack is not None
        assert hasattr(OpenStack, '__init__')

    def test_openstack2_class_importable(self):
        """Test that OpenStack2 class can be imported"""
        from osclient import OpenStack2
        assert OpenStack2 is not None
        assert hasattr(OpenStack2, '__init__')

    def test_direct_imports_work(self):
        """Test that direct imports from submodules work"""
        from osclient.openstack import OpenStack as OpenStackDirect
        from osclient.openstack2 import OpenStack2 as OpenStack2Direct

        assert OpenStackDirect is OpenStack
        assert OpenStack2Direct is OpenStack2

