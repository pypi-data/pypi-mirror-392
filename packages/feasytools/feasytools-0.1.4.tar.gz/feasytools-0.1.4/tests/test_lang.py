from pathlib import Path
from feasytools.i18n import LangLib, LangConfig

def test_load_pylanglib():
    print(Path(__file__).absolute().stem)
    _ = LangLib.LoadFrom("tests/langs")
    print(_("MESSAGE"))
    LangConfig.SetLangCode("zh_CN")
    print(_("MESSAGE"))
    LangConfig.SetLangCode("en_US")
    print(_("MESSAGE"))
    LangConfig.SetLangCode("en_GB")
    print(_("MESSAGE"))

    _ = LangLib.LoadFor(__file__)
    print(_("MESSAGE"))
    LangConfig.SetLangCode("zh_CN")
    print(_("MESSAGE"))
    LangConfig.SetLangCode("en_US")
    print(_("MESSAGE"))
    LangConfig.SetLangCode("en_GB")
    print(_("MESSAGE"))

if __name__ == "__main__":
    test_load_pylanglib()