# tests/test_ctext.py
from cobra_color import ctext, compile_template


def test_ctext():
    for i in range(0, 256):
        a = ctext("\u2588", fg=(0, 0, i))
        assert isinstance(a, str)
        print(a, end="")
        if (i + 1) % 32 == 0:
            print()


def test_compile_template():
    template = compile_template(bg="b", styles=["bold", "udl"])
    c_str = template("Hello World!")
    assert isinstance(c_str, str)
