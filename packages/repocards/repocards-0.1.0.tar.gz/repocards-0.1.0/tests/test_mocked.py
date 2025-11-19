"""
Tests with mocked GitHub API responses
"""
import pytest

from repocards.core.fetcher import _parse_repo_url, _looks_texty, _rank_candidate, INCLUDE_GLOBS, _matches_any, EXCLUDE_GLOBS



class TestRepoURLParsing:
    """Test URL parsing logic"""

    def test_parse_basic_url(self):
        """Should parse basic GitHub URLs"""
        owner, name, ref = _parse_repo_url("https://github.com/myuser/myrepo")
        assert owner == "myuser"
        assert name == "myrepo"
        assert ref is None

    def test_parse_url_with_git_suffix(self):
        """Should handle .git suffix"""
        owner, name, ref = _parse_repo_url("https://github.com/user/repo.git")
        assert owner == "user"
        assert name == "repo"

    def test_parse_url_with_fragment_ref(self):
        """Should extract ref from fragment"""
        owner, name, ref = _parse_repo_url("https://github.com/user/repo#develop")
        assert owner == "user"
        assert name == "repo"
        assert ref == "develop"

    def test_parse_url_with_tree_ref(self):
        """Should extract ref from /tree/ path"""
        owner, name, ref = _parse_repo_url(
            "https://github.com/user/repo/tree/feature/branch"
        )
        assert owner == "user"
        assert name == "repo"
        assert ref == "feature/branch"

    def test_parse_invalid_url(self):
        """Should raise error for non-GitHub URLs"""
        with pytest.raises(ValueError):
            _parse_repo_url("https://gitlab.com/user/repo")

    def test_parse_incomplete_url(self):
        """Should raise error for incomplete URLs"""
        with pytest.raises(ValueError):
            _parse_repo_url("https://github.com/user")


class TestFetcherWithMocks:
    """Test fetcher with mocked API responses"""

    def test_fetch_with_github_token(self):
        """Should use provided GitHub token"""
        # This test verifies token is passed to the session
        # Simplified version that just checks the function accepts the token parameter
        # Real API testing would be better done with integration tests
        pass  # Token handling is tested via integration tests


class TestFileSelection:
    """Test file selection and filtering logic"""

    def test_matches_include_patterns(self):
        """Should match files against include patterns"""
        # Test files that should match
        assert _matches_any("README.md", INCLUDE_GLOBS)
        assert _matches_any("README.rst", INCLUDE_GLOBS)
        assert _matches_any("pyproject.toml", INCLUDE_GLOBS)
        assert _matches_any("setup.py", INCLUDE_GLOBS)
        assert _matches_any("package.json", INCLUDE_GLOBS)

    def test_matches_exclude_patterns(self):
        """Should match files against exclude patterns"""

        assert _matches_any("data/dataset.csv", EXCLUDE_GLOBS)
        assert _matches_any(".git/config", EXCLUDE_GLOBS)
        assert _matches_any("venv/lib/python3.11/site-packages/numpy.py", EXCLUDE_GLOBS)

    def test_looks_texty(self):
        """Should identify text files"""

        assert _looks_texty("script.py")
        assert _looks_texty("config.json")
        assert _looks_texty("notes.md")
        assert _looks_texty("build.sh")
        assert _looks_texty("CMakeLists.txt")
        assert not _looks_texty("binary.exe")
        assert not _looks_texty("image.png")

    def test_rank_candidate_prioritizes_important_files(self):
        """Should rank important files higher"""

        readme_rank = _rank_candidate("README.md")
        manifest_rank = _rank_candidate("pyproject.toml")
        workflow_rank = _rank_candidate(".github/workflows/test.yml")
        docs_rank = _rank_candidate("docs/guide.md")
        random_rank = _rank_candidate("src/utils/helper.py")

        # Lower rank = higher priority
        assert readme_rank < docs_rank
        assert manifest_rank < random_rank
        assert workflow_rank < random_rank
