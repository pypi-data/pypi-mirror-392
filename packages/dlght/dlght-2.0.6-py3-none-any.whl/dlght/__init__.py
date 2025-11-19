
import fire
from .dgx import DGX
from .preset import PRESET  

class ENTRY(object):
    def x(self, url: str, output: str = None, resume: bool = True, unzip: bool = False, proxy: bool = False):
        """下载GitHub文件（支持断点续传和自动解压）"""
        DGX(url, output, resume, unzip, proxy)


    def preset(self):
        PRESET() 

    def from_file():
        pass


def main() -> None:
    try:
        fire.Fire(ENTRY)
    except KeyboardInterrupt:
        print("\n操作已取消")
        exit(0)
