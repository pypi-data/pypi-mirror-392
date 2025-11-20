"""AST를 이용한 데코레이터 인자 추출."""

import ast
from pathlib import Path
from typing import Any, Optional, Union


def extract_decorator_argument(
    file_path: Union[str, Path],
    decorator_name: str,
    argument_index: Optional[int] = None,
    keyword_arg: Optional[str] = None,
) -> Optional[Any]:
    """
    함수 데코레이터에서 인자를 추출합니다.

    Args:
        file_path: Python 파일 경로
        decorator_name: 검색할 데코레이터 이름 (예: "trace_pytorch", "keynet_function")
        argument_index: 인자의 위치 (0부터 시작), 위치 인자용
        keyword_arg: 키워드 인자 이름 (예: "model_name", "base_image")

    Returns:
        추출된 인자 값, 찾지 못하면 None

    Examples:
        >>> # 위치 인자 추출
        >>> extract_decorator_argument("train.py", "keynet_function", argument_index=0)
        "my_function"

        >>> # 키워드 인자 추출
        >>> extract_decorator_argument("train.py", "trace_pytorch", keyword_arg="model_name")
        "resnet50"

        >>> # base_image 추출
        >>> extract_decorator_argument("function.py", "keynet_function", keyword_arg="base_image")
        "openwhisk/action-python-v3.11"

    """
    if argument_index is None and keyword_arg is None:
        raise ValueError(
            "argument_index 또는 keyword_arg 중 하나는 반드시 제공해야 합니다"
        )

    file_path = Path(file_path)
    try:
        code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(code, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # 데코레이터가 Call 노드인지 확인 (예: @decorator(...))
                    if isinstance(decorator, ast.Call):
                        decorator_func = decorator.func

                        # 단순 이름 처리 (예: @trace_pytorch(...))
                        if isinstance(decorator_func, ast.Name):  # noqa: SIM102
                            if decorator_func.id == decorator_name:
                                return _extract_argument(
                                    decorator, argument_index, keyword_arg
                                )

        return None

    except Exception:
        return None


def _extract_argument(
    decorator_call: ast.Call,
    argument_index: Optional[int],
    keyword_arg: Optional[str],
) -> Optional[Any]:
    """데코레이터 Call 노드에서 인자 추출."""
    # 위치 인자 추출
    if argument_index is not None and argument_index < len(decorator_call.args):
        arg_node = decorator_call.args[argument_index]
        return _get_constant_value(arg_node)

    # 키워드 인자 추출
    if keyword_arg is not None:
        for keyword in decorator_call.keywords:
            if keyword.arg == keyword_arg:
                return _get_constant_value(keyword.value)

    return None


def _get_constant_value(node: ast.AST) -> Optional[Any]:
    """AST 노드에서 상수 값 추출."""
    if isinstance(node, ast.Constant):
        return node.value
    # Python 3.7 호환성
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    return None
