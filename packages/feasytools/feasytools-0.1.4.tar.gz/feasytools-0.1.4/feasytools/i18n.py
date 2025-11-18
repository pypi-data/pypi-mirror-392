from typing import List, Optional, Tuple, Union, Dict
from pathlib import Path
import locale, os

def _get_saved_lang(app_name:str) -> str:
    config_dir = Path.home() / f".{app_name}"
    config_dir.mkdir(exist_ok=True, parents=True)
    config_file = config_dir / "lang.conf"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                lang_code = f.read().strip()
                if lang_code == "<auto>":
                    return _get_system_lang()
                return lang_code
        except:
            pass
    return _get_system_lang()

def _get_system_lang() -> str:
    try:
        sys_locale = locale.getdefaultlocale()[0]
    except:
        sys_locale = None
    if sys_locale is None:
        sys_locale = os.environ.get("LANG", "")
    if sys_locale == "":
        sys_locale = "en_US"
    else:
        sys_locale = sys_locale.split(".")[0]
    return sys_locale

class LangConfig:
    _lib_cache: Dict[str, 'LangLib'] = {}
    _app_name: str = ""
    _cl = _get_saved_lang("feasytools")

    @staticmethod
    def SetAppName(app_name: str):
        """Set application name for saving language configuration."""
        LangConfig._app_name = app_name
        LangConfig._cl = _get_saved_lang(app_name)

    @staticmethod
    def GetSystemLang() -> str:
        """Get system language code, such as 'en_US' or 'zh_CN'."""
        return _get_system_lang()
    
    @staticmethod
    def GetLangCode() -> str:
        """Get current language code for feasytools, such as 'en_US' or 'zh_CN'."""
        return LangConfig._cl
    
    @staticmethod
    def SetLangCode(lang_code: str):
        """Set current language code for feasytools, such as 'en_US' or 'zh_CN'. 
        A special case is '<auto>', standing for system language. No validation is performed. """
        if LangConfig._app_name == "":
            raise RuntimeError("Please set application name first using LangConfig.SetAppName(app_name).")
        config_dir = Path.home() / f".{LangConfig._app_name}"
        config_dir.mkdir(exist_ok=True, parents=True)
        config_file = config_dir / "lang.conf"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(lang_code)
        LangConfig._cl = lang_code
    
class LangLib:
    def __init__(self, supports_lang: Optional[List[str]] = None):
        if supports_lang is None:
            supports_lang = []
        self.__supports = supports_lang
        self.__lib = {lang: {} for lang in supports_lang}
        self.__similar_cache = {}
    
    def FindSimilarLang(self, lang_code: str) -> Union[str, None]:
        """Find the most similar supported language code to the given lang_code."""
        if lang_code in self.__supports:
            return lang_code
        if lang_code in self.__similar_cache:
            return self.__similar_cache[lang_code]
        lang_prefix = lang_code.split("_")[0]

        # First try to find an exact match with the same prefix
        for lang in self.__supports:
            if lang.startswith(lang_prefix):
                self.__similar_cache[lang_code] = lang
                return lang
        
        # If no similar language found, return an English if supported
        for lang in self.__supports:
            if lang.startswith("en_"):
                self.__similar_cache[lang_code] = lang
                return lang
        
        return None
    
    @staticmethod
    def Load(path:Union[str, Path]):
        """
        Load default language library.
        It should be used like this:
            _ = LangLib.Load(__file__)
        Equals to:
            _ = LangLib.LoadFrom(Path(__file__).parent / "_lang")
        """
        if isinstance(path, str):
            path = Path(path)
        return LangLib.LoadFrom(path.parent / "_lang")
    
    @staticmethod
    def LoadFor(path:Union[str, Path]):
        """
        Load language library for a given python file
        It should be used like this:
            _ = LangLib.LoadFor(__file__)
        Equals to:
            _ = LangLib.LoadFrom(Path(__file__).parent / (Path(__file__).stem + ".langs"))
        For example, if the python file is "tests/test_lang.py",
        it will load language library from "tests/test_lang.langs".
        Here "tests/test_lang.langs" can be either a single file or a directory of .lang files.
        """
        if isinstance(path, str):
            path = Path(path)
        return LangLib.LoadFrom(path.parent / (path.stem + ".langs"))
    
    @staticmethod
    def LoadFrom(path:Union[str, Path]):
        """
        Load language library from a given path.
        The path can be either a single .langs file or a directory of .lang files.
        """
        if isinstance(path, str):
            path = Path(path)
        path_str = str(path)

        if path_str in LangConfig._lib_cache:
            return LangConfig._lib_cache[path_str]
        
        assert path.exists(), f"Path {path} does not exist."

        if path.is_file():
            lib = LangLib([])
            lib.LoadLangsLib(path)
            return lib
        
        langs = []
        for pc in path.iterdir():
            if pc.is_file() and pc.suffix == ".lang":
                langs.append(pc.stem)
        lib = LangLib(langs)
        for lang in langs:
            lib.LoadLangLib(lang, path / f"{lang}.lang")
        
        LangConfig._lib_cache[path_str] = lib
        return lib
    
    @property
    def SupportedLanguage(self):
        return self.__supports
    
    def SetLangLib(self, lang:str, **kwargs):
        self.__lib[lang].clear()
        for key, val in kwargs.items():
            self.__lib[lang][key] = val
    
    def LoadLangLib(self, lang:str, path:Union[Path, str]):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                key, val = line.split("=", 1)
                self.__lib[lang][key.strip()] = val.replace("\\n", "\n")
    
    def LoadLangsLib(self, path:Union[Path, str]):
        with open(path, "r", encoding="utf-8") as f:
            # Identify language first
            for line in f:
                line = line.strip()
                if not line: continue
                if line.startswith("[") and line.endswith("]"):
                    cur_lang = line[1:-1].strip()
                    if cur_lang not in self.__supports:
                        self.__supports.append(cur_lang)
                        self.__lib[cur_lang] = {}
                    break
            
            # Load translations only after identifying a language
            for line in f:
                line = line.strip()
                if not line: continue
                if line.startswith("[") and line.endswith("]"):
                    cur_lang = line[1:-1].strip()
                    if cur_lang not in self.__supports:
                        self.__supports.append(cur_lang)
                        self.__lib[cur_lang] = {}
                    continue
                key, val = line.split("=", 1)
                self.__lib[cur_lang][key.strip()] = val.replace("\\n", "\n")
    
    def __setitem__(self, key:Tuple[str, str], value:str):
        """Set translation for a specific language and key."""
        assert isinstance(key, tuple)
        assert len(key) == 2
        assert isinstance(key[0], str)
        assert isinstance(key[1], str)
        self.__lib[key[0]][key[1]] = value
    
    def __getitem__(self, key) -> str:
        assert isinstance(key, str)
        try:
            return self.__lib[LangConfig._cl][key]
        except KeyError:
            try:
                similar_lang = self.FindSimilarLang(LangConfig._cl)
                if similar_lang is not None:
                    return self.__lib[similar_lang][key]
            except KeyError:
                pass
            return key
    
    def __call__(self, key) -> str:
        assert isinstance(key, str)
        try:
            return self.__lib[LangConfig._cl][key]
        except KeyError:
            try:
                similar_lang = self.FindSimilarLang(LangConfig._cl)
                if similar_lang is not None:
                    return self.__lib[similar_lang][key]
            except KeyError:
                pass
            return key

__all__ = ["LangLib", "LangConfig"]