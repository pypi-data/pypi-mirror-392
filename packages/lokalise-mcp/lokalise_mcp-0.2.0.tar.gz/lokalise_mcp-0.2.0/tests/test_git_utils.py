import pytest
from pathlib import Path
from git import Repo
from lokalise_mcp.git_utils import get_changed_files, GitDiffExtractor


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo = Repo.init(tmp_path)

    # Create initial commit on main
    test_file = tmp_path / "test.txt"
    test_file.write_text("initial content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create feature branch
    repo.create_head("feature")
    repo.heads.feature.checkout()

    return repo, tmp_path


def test_get_changed_files_returns_modified_files(git_repo):
    """Test that get_changed_files returns files changed in current branch."""
    repo, tmp_path = git_repo

    # Modify file on feature branch
    modified_file = tmp_path / "test.txt"
    modified_file.write_text("modified content")
    repo.index.add([str(modified_file)])
    repo.index.commit("Modify file")

    # Add new file
    new_file = tmp_path / "new.tsx"
    new_file.write_text("const x = t('key')")
    repo.index.add([str(new_file)])
    repo.index.commit("Add new file")

    changed_files = get_changed_files(str(tmp_path), base_branch="main")

    assert len(changed_files) >= 2
    assert any("test.txt" in str(f) for f in changed_files)
    assert any("new.tsx" in str(f) for f in changed_files)


def test_git_diff_extractor_filters_by_pattern(git_repo):
    """Test that GitDiffExtractor filters files by pattern."""
    repo, tmp_path = git_repo

    # Create files with different extensions
    tsx_file = tmp_path / "component.tsx"
    tsx_file.write_text("t('key')")
    py_file = tmp_path / "script.py"
    py_file.write_text("print('hello')")

    repo.index.add([str(tsx_file), str(py_file)])
    repo.index.commit("Add mixed files")

    extractor = GitDiffExtractor(
        repo_path=str(tmp_path),
        file_patterns=["**/*.tsx", "**/*.ts"],
        exclude_patterns=["**/node_modules/**"]
    )

    changed_files = extractor.get_changed_files(base_branch="main")

    assert len(changed_files) == 1
    assert "component.tsx" in str(changed_files[0])
    assert not any("script.py" in str(f) for f in changed_files)
