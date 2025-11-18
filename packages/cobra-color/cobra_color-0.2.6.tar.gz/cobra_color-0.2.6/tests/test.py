# tests/test_ctext.py
import sys
sys.path.append("/data/tianzhen/my_packages/cobra-color/src")


from cobra_color import ctext


def test_ctext():
    
    a = ctext("abcd", bg="lm", styles=["bold", "udl"])
    
    print(a.plain)
    
    print(a)
    
    print(a.color_only)
    
    print(a.style_only)
    
    # for i in range(0, 256):
    #     a = ctext("\u2588", fg=(0, 0, i))
    #     assert isinstance(a, str)
    #     print(a, end="")
    #     if (i + 1) % 32 == 0:
    #         print()


test_ctext()