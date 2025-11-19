from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.validation import Validator, ValidationError
import requests

class PRESET():
    def __init__(self):
        self.api_failed = False
        self.software = {
            "v2rayN": {
                "url":"https://github.com/2dust/v2rayN",
                "default_version":"7.15.7",
                "default_files": [
                    "v2rayN-windows-64-desktop.zip",
                    "v2rayN-windows-64-SelfContained.zip",
                    "v2rayN-linux-64.deb",
                    "v2rayN-linux-rhel-x64.rpm",
                    "v2rayN-macos-64.zip",
                    "v2rayN-macos-arm64.zip",
                ]
                },
            "clash-verge": {
                "url":"https://github.com/clash-verge-rev/clash-verge-rev",
                "default_version":"v2.4.3",
                "default_files":[
                    "Clash.Verge_2.4.3_x64-setup.exe",
                    "Clash.Verge_2.4.3_aarch64.dmg",
                    "Clash.Verge_2.4.3_amd64.deb",
                    "Clash.Verge-2.4.3-1.x86_64.rpm",
                ]
            }
        }
        repo_url=self.select_software()
        self.select_software_release(repo_url)

    def select_software(self):
        """让用户选择软件并返回仓库地址"""
        base_completer = WordCompleter(
            list(self.software.keys()),
            ignore_case=True
        )
        
        # 创建验证器，只允许输入 self.software.keys() 中的内容
        class SoftwareValidator(Validator):
            def __init__(self, valid_options):
                self.valid_options = valid_options
            
            def validate(self, document):
                text = document.text.strip()
                if text and text not in self.valid_options:
                    raise ValidationError(
                        message=f"无效的选项，请从以下选项中选择: {', '.join(self.valid_options)}"
                    )
        
        completer = FuzzyCompleter(base_completer)
        validator = SoftwareValidator(list(self.software.keys()))
        
        selected = prompt(
            "请选择软件 (支持模糊搜索): ",
            completer=completer,
            validator=validator,
            validate_while_typing=False
        ).strip()
        
        if selected in self.software:
            repo_url = self.software[selected]["url"]
            print(f"\n软件: {selected}")
            print(f"仓库地址: {repo_url}")
            return repo_url
        else:
            print(f"\n错误: 未找到软件 '{selected}'")
            print(f"可用选项: {', '.join(self.software.keys())}")
            return None
    
    def select_software_release(self, repo_url):
        """
        通过 https://api.github.com/repos/{owner}/{repo}/releases 接口获取 软件release信息
        然后 让用户选择 release 版本(用 FuzzyCompleter)
        然后让用户选择 该release 版本当中的文件(用 FuzzyCompleter)
        然后 生成所需要下载文件的链接 
        """
        # 从仓库URL提取owner和repo
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        
        # 获取releases信息
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            releases = response.json()
        except Exception as e:
            print(f"\n错误: API请求失败 - {e}")
            print("将使用默认版本和文件列表")
            self.api_failed = True
            return self._select_default_version_and_files(owner, repo)
        
        if not releases:
            print("\n错误: 该仓库没有releases")
            return None
        
        # 让用户选择release版本
        release_names = [r['tag_name'] for r in releases]
        release_meta = {
            r['tag_name']: f"预发布: {r['prerelease']} | 发布时间: {r['published_at']}"
            for r in releases
        }
        release_completer = FuzzyCompleter(
            WordCompleter(release_names, meta_dict=release_meta, ignore_case=True)
        )
        
        selected_release = prompt(
            "请选择release版本 (支持模糊搜索): ",
            completer=release_completer
        ).strip()
        
        # 找到选中的release
        release = next((r for r in releases if r['tag_name'] == selected_release), None)
        if not release:
            print(f"\n错误: 未找到版本 '{selected_release}'")
            return None
        
        # 获取该release的所有文件
        assets = release.get('assets', [])
        if not assets:
            print(f"\n错误: 版本 '{selected_release}' 没有可下载的文件")
            return None
        
        # 让用户选择文件
        asset_names = [asset['name'] for asset in assets]
        asset_meta = {
            asset['name']: f"大小: {asset['size'] / 1024 / 1024:.2f} MB | 下载次数: {asset['download_count']}"
            for asset in assets
        }
        asset_completer = FuzzyCompleter(
            WordCompleter(asset_names, meta_dict=asset_meta, ignore_case=True)
        )
        
        selected_asset = prompt(
            "请选择要下载的文件 (支持模糊搜索): ",
            completer=asset_completer
        ).strip()
        
        # 找到选中的文件
        asset = next((a for a in assets if a['name'] == selected_asset), None)
        if not asset:
            print(f"\n错误: 未找到文件 '{selected_asset}'")
            return None
        
        download_url = asset['browser_download_url']
        print(f"\n版本: {selected_release}")
        print(f"文件: {selected_asset}")
        print(f"下载链接: {download_url}")
        
        return download_url


    def _select_default_version_and_files(self, owner, repo):
        """当API请求失败时，让用户从默认版本和文件中选择"""
        # 根据repo名称找到对应的软件配置
        software_config = None
        for name, config in self.software.items():
            if repo in config["url"]:
                software_config = config
                break
        
        if not software_config:
            print(f"\n错误: 未找到 {repo} 的默认配置")
            return None
        
        default_version = software_config.get("default_version")
        default_files = software_config.get("default_files", [])
        
        if not default_version or not default_files:
            print(f"\n错误: {repo} 没有配置默认版本或文件")
            return None
        
        print(f"\n默认版本: {default_version}")
        
        # 让用户选择默认文件
        file_completer = FuzzyCompleter(
            WordCompleter(default_files, ignore_case=True)
        )
        
        selected_file = prompt(
            "请从默认文件列表中选择 (支持模糊搜索): ",
            completer=file_completer
        ).strip()
        
        if selected_file not in default_files:
            print(f"\n错误: 未找到文件 '{selected_file}'")
            return None
        
        # 构造下载链接
        download_url = f"https://github.com/{owner}/{repo}/releases/download/{default_version}/{selected_file}"
        print(f"\n版本: {default_version}")
        print(f"文件: {selected_file}")
        print(f"下载链接: {download_url}")
        
        return download_url

    def download_software(self, software_name):
        """下载指定的软件"""
        if software_name in self.software:
            repo_url = self.software[software_name]["url"]
            print(f"开始下载 {software_name}...")
            print(f"仓库地址: {repo_url}")
            return repo_url
        else:
            print(f"错误: 未找到软件 '{software_name}'")
