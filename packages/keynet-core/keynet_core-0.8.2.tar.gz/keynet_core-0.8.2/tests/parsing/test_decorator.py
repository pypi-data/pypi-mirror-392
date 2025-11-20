"""Python 데코레이터 추출 테스트."""

import tempfile

from keynet_core.parsing import extract_decorator_argument


def test_extract_decorator_argument_with_string():
    """데코레이터에서 문자열 인자 추출."""
    code = """
@some_decorator("my_function")
def main(args):
    pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_decorator_argument(
            file_path=f.name, decorator_name="some_decorator", argument_index=0
        )

        assert result == "my_function"


def test_extract_decorator_argument_keyword():
    """데코레이터에서 키워드 인자 추출."""
    code = """
@trace_pytorch(
    model_name="resnet50",
    sample_input=torch.randn(1, 3, 224, 224)
)
def train():
    pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_decorator_argument(
            file_path=f.name, decorator_name="trace_pytorch", keyword_arg="model_name"
        )

        assert result == "resnet50"


def test_extract_decorator_argument_base_image():
    """데코레이터에서 base_image 키워드 인자 추출."""
    code = """
@keynet_function(
    name="my_function",
    base_image="openwhisk/action-python-v3.11"
)
def main(args):
    pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_decorator_argument(
            file_path=f.name, decorator_name="keynet_function", keyword_arg="base_image"
        )

        assert result == "openwhisk/action-python-v3.11"


def test_extract_decorator_argument_not_found():
    """데코레이터를 찾지 못하면 None 반환."""
    code = """
def main(args):
    pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_decorator_argument(
            file_path=f.name, decorator_name="missing_decorator", argument_index=0
        )

        assert result is None


def test_extract_decorator_argument_multiple_functions():
    """여러 함수 중 올바른 데코레이터 추출."""
    code = """
@decorator1("first")
def func1():
    pass

@decorator2("second")
def func2():
    pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_decorator_argument(
            file_path=f.name, decorator_name="decorator2", argument_index=0
        )

        assert result == "second"
