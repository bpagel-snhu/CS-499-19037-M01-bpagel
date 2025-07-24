import os
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def sample_pdf_files(test_dir):
    """Create sample PDF files for testing."""
    files = []
    for i in range(3):
        file_path = os.path.join(test_dir, f"test_file_{i}.pdf")
        with open(file_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')  # Minimal PDF header
        files.append(file_path)
    return files

@pytest.fixture(scope="function")
def backup_dir(test_dir):
    """Create a temporary directory for backup tests."""
    backup_dir = os.path.join(test_dir, "backups")
    os.makedirs(backup_dir)
    return backup_dir

@pytest.fixture(scope="function")
def mock_pdf_metadata():
    """Mock PDF metadata for testing."""
    return {
        'title': 'Test Title',
        'author': 'Test Author',
        'creation_date': '2024-01-01',
        'modification_date': '2024-01-01',
        'producer': 'Test Producer',
        'creator': 'Test Creator'
    }

@pytest.fixture(scope="function")
def mock_rename_options():
    """Create mock rename options for testing."""
    from batch_renamer.tools.bulk_rename.rename_logic import RenameOptions
    return RenameOptions(
        prefix="TEST_",
        suffix="_RENAMED",
        start_number=1,
        padding=3,
        use_metadata=False,
        metadata_format="{title}_{author}"
    ) 