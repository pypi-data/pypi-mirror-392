"""Python 구문 검증 테스트."""

import tempfile
from pathlib import Path

from keynet_core.validation import PythonSyntaxValidator


def test_validate_file_valid_python():
    """올바른 Python 파일은 검증 통과."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def hello():\n    return 'world'\n")
        f.flush()

        success, error = PythonSyntaxValidator.validate_file(Path(f.name))

        assert success is True
        assert error is None


def test_validate_file_syntax_error():
    """구문 오류가 있는 파일은 검증 실패."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def hello(\n    return 'world'\n")  # 괄호 누락
        f.flush()

        success, error = PythonSyntaxValidator.validate_file(Path(f.name))

        assert success is False
        assert error is not None
        assert ":" in error  # 파일:줄번호 형식


def test_validate_files_multiple():
    """여러 파일 동시 검증."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 올바른 파일
        valid_file = tmp_path / "valid.py"
        valid_file.write_text("x = 1\n")

        # 오류 파일
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("def broken(\n")

        success, errors = PythonSyntaxValidator.validate_files(
            [valid_file, invalid_file]
        )

        assert success is False
        assert len(errors) == 1
        assert "invalid.py" in errors[0]


def test_validate_files_skip_non_python():
    """Python 파일이 아닌 경우 건너뛰기."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("not python")

        success, errors = PythonSyntaxValidator.validate_files([txt_file])

        assert success is True
        assert len(errors) == 0
