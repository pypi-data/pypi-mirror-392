# tests/test_ctext.py
import sys
sys.path.append("/data/tianzhen/my_packages/cobra-color/src")


from cobra_color import ctext
from cobra_color.draw import fmt_font, FontName


def test_fmt_font():
    result = fmt_font(
        "Hello, cobra-color!",
        font=FontName.LLDISCO,
        trim_border=True,
        mode="half-gray",
        font_size=10,
        fore_rgb=(255, 120, 0),
        back_rgb=(0, 120, 0)
    )
    assert isinstance(result, str)
    print(result)


def test_ctext():
    
    a = ctext("abcd", bg="lm", styles=["bold", "udl"])
    
    b = ctext("1234ff", fg="r", styles=["italic", "delete"])
    a = a + b
    a *= 2
    
    print(a.apply_to("XYZ"))

    print(b.upper())
    
    print(len(a))
    
    print(a[0])
    
    print(repr(a))
    
    print(a.iscolored())
    
    print("====")
    
    print(a.color_only)
    print(a.color_only)
    
    print(a.style_only)
    
    exit()
    
    print(b)
    
    print(c)
    print(c.plain)
    print(c.color_only)
    print(c.style_only)
    
    print(a)
    print(b)
    


def test_ctext_1():
    for i in range(0, 256):
        a = ctext("\u2588", fg=(0, 0, i))
        assert isinstance(a, str)
        print(a, end="")
        if (i + 1) % 32 == 0:
            print()


test_ctext()

# test_ctext_1()

# test_fmt_font()
