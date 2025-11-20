"""AST 파싱을 이용한 Python 구문 검증."""

import ast
from pathlib import Path
from typing import Optional


class PythonSyntaxValidator:
    """
    Python 소스 파일의 구문을 검증하는 클래스.

    AST 파싱을 사용하여 Python 파일의 구문 오류를 확인하고,
    줄 번호와 컨텍스트가 포함된 자세한 오류 메시지를 제공합니다.
    """

    @staticmethod
    def validate_files(files: list[Path]) -> tuple[bool, list[str]]:
        """
        여러 파일의 Python 구문을 검증합니다.

        Args:
            files: 검증할 파일 경로 리스트

        Returns:
            (성공 여부, 오류 메시지 리스트) 튜플:
            - 성공: 모든 파일이 올바른 Python 구문이면 True
            - 오류 메시지: 잘못된 파일의 포맷된 오류 메시지 리스트

        Example:
            >>> validator = PythonSyntaxValidator()
            >>> files = [Path("train.py"), Path("model.py")]
            >>> success, errors = validator.validate_files(files)
            >>> if not success:
            ...     for error in errors:
            ...         print(error)

        """
        errors = []

        for file_path in files:
            # Python 파일이 아니면 건너뛰기
            if not file_path.name.endswith(".py"):
                continue

            try:
                # 파일 내용 읽기
                content = file_path.read_text(encoding="utf-8")

                # Python 구문 파싱 (오류 시 SyntaxError 발생)
                ast.parse(content, filename=str(file_path))

            except SyntaxError as e:
                # 파일, 줄 번호, 오류 상세 정보로 메시지 포맷
                error_msg = f"{file_path}:{e.lineno}: {e.msg}"
                if e.text:
                    error_msg += f"\n  {e.text.rstrip()}"
                    if e.offset:
                        error_msg += f"\n  {' ' * (e.offset - 1)}^"
                errors.append(error_msg)

            except UnicodeDecodeError as e:
                errors.append(f"{file_path}: UTF-8 인코딩 오류 - {e}")

            except Exception as e:
                errors.append(f"{file_path}: 예상치 못한 오류 - {e}")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_file(file_path: Path) -> tuple[bool, Optional[str]]:
        """
        단일 Python 파일을 검증합니다.

        Args:
            file_path: Python 파일 경로

        Returns:
            (성공 여부, 오류 메시지) 튜플:
            - 성공: 파일이 올바른 Python 구문이면 True
            - 오류 메시지: 잘못된 경우 메시지, 올바르면 None

        """
        success, errors = PythonSyntaxValidator.validate_files([file_path])
        return (success, errors[0] if errors else None)
