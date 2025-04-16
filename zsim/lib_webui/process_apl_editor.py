from dataclasses import dataclass
import streamlit as st
import toml
import os

from .constants import CHAR_CID_MAPPING
from define import DEFAULT_APL_DIR, COSTOM_APL_DIR, saved_char_config


@dataclass
class APLArchive:
    default_apl_list: list[dict] = None
    custom_apl_list: list[dict] = None

    def __post_init__(self):
        self.refresh()

    def refresh(self):
        self.default_apl_list = self.__get_apl_toml(DEFAULT_APL_DIR)
        self.custom_apl_list = self.__get_apl_toml(COSTOM_APL_DIR)
        
    def __get_apl_toml(self, apl_path: str) -> list[dict]:
        """根据APL地址获取APL toml的内容
        :param apl_path: APL文件或目录路径
        :return: toml字典列表，如果文件不存在则返回空列表
        """
        toml_dict_list = []
        # 将输入路径转换为绝对路径
        abs_apl_path = os.path.abspath(apl_path)
        try:
            if os.path.isfile(apl_path):
                # 如果是文件，直接处理
                if apl_path.endswith('.toml'):
                    with open(apl_path, 'rb') as f:
                        toml_dict: dict = toml.load(f)
                        if toml_dict.get('apl_logic', {}).get('logic') is not None:
                            toml_dict_list.append(toml_dict)
            elif os.path.isdir(apl_path):
                # 如果是目录，遍历所有toml文件
                for root, _, files in os.walk(apl_path):
                    for file in files:
                        if file.endswith('.toml'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    toml_dict: dict = toml.load(f)
                                    if toml_dict.get('apl_logic', {}).get('logic') is not None:
                                        toml_dict_list.append(toml_dict)
                            except Exception as e:
                                st.exception(e)
            else:
                raise ValueError(f"路径不存在：{apl_path}")
            return toml_dict_list
        except Exception as e:
            raise ValueError(f"读取APL文件失败：{str(e)}")


class APLJudgeTool:
    def __init__(self, raw_apl: dict) -> None:
        self.raw_apl: dict = raw_apl
        self.characters: dict = raw_apl.get('characters', {})
        self.required_chars: list[str] = [self._convert_to_name(char) for char in self.characters.get('required', [])]
        self.optional_chars: list[str] = [self._convert_to_name(char) for char in self.characters.get('optional', [])]
        self.char_configs: dict[str, dict] = {
            self._convert_to_name(k): v 
            for k, v in self.characters.items() 
            if k not in ['required', 'optional']
        }   # {name: {config}}
        self.apl_logic: str = raw_apl.get('apl_logic', {}).get('logic', '')
        
        self.saved_char_config: dict = saved_char_config
    
    def _convert_to_name(self, char_identifier: str | int) -> str:
        """将任何角色标识（名称或CID）统一转换为角色名称"""
        # 如果输入的是CID，通过反向查找获取名称
        for name, cid in CHAR_CID_MAPPING.items():
            if cid == char_identifier:
                return name
        # 如果输入的是名称或未知标识，直接返回
        return char_identifier

    def judge_requried_chars(self) -> tuple[bool, list[str]]:
        """判断是否满足所有必须角色"""
        missing_chars = []
        for char in self.required_chars:
            if char not in self.saved_char_config.get('name_box', []):
                missing_chars.append(char)
        return len(missing_chars) == 0, missing_chars

    def judge_optional_chars(self) -> tuple[bool, list[str]]:
        """判断是否满足所有可选角色"""
        missing_chars = []
        for char in self.optional_chars:
            if char not in self.saved_char_config.get('name_box', []):
                missing_chars.append(char)
        return len(missing_chars) == 0, missing_chars

    def judge_char_config(self) -> tuple[bool, dict[str, str|int]]:
        """判断是否满足所有角色配置"""
        missing_configs = {}
        char_name: str   # 角色名称
        config: dict    # 角色配置字典
        key: str    # 配置项名称
        value: str | int  # 配置项值
        saved_value: str | int | list[str | int]   # 保存的配置项值
        for char_name, config in self.char_configs.items():
            for key, value in config.items():
                saved_value = self.saved_char_config.get(char_name, {}).get(key)
                target_value = str(value)
                pass_through_values = ['', 'None', '-1']
                # 如果目标值在pass_through中，直接跳过后续判断
                if target_value in pass_through_values:
                    continue
                # 判断saved_value是否为列表
                if isinstance(saved_value, list):
                    # 如果是列表，检查目标值是否在列表中
                    if target_value not in [str(v) for v in saved_value]:
                        missing_configs[char_name] = missing_configs.get(char_name, {})
                        missing_configs[char_name][key] = value
                else:
                    # 如果不是列表，按相等判断
                    if str(saved_value) != target_value:
                        missing_configs[char_name] = missing_configs.get(char_name, {})
                        missing_configs[char_name][key] = value
                        
        return len(missing_configs) == 0, missing_configs
    
    
def process_apl_editor():
    apl_archive = APLArchive()
    apl_archive.refresh()
    st.text(apl_archive.default_apl_list + apl_archive.custom_apl_list)
    st.selectbox(
        '选择APL',
        options=apl_archive.default_apl_list + apl_archive.custom_apl_list,
        format_func=lambda x: x.get('apl_logic', {}).get('logic', ''),
        key='apl_editor'
    )