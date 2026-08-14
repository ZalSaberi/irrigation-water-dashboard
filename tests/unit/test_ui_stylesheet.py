from aqualog.ui.theme.stylesheet import build_stylesheet


def test_stylesheet_builds_without_fstring_name_errors():
    css = build_stylesheet("Shabnam")
    assert "QLabel#HeroTitle {" in css
    assert "QFrame#SidebarLogoCard {" in css
    assert "font-size: 30px;" in css
