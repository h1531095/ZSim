from dataclasses import dataclass
import time
from typing import Sequence
import streamlit as st
import toml
import os

from .constants import CHAR_CID_MAPPING
from define import DEFAULT_APL_DIR, COSTOM_APL_DIR, saved_char_config


@dataclass
class APLArchive:
    default_apl_map: dict[str, dict] = None  # {relative_path: apl_toml}
    custom_apl_map: dict[str, dict] = None  # {relative_path: apl_toml}
    options: Sequence[str] = None
    title_apl_map: dict[str, dict] = None  # {title: apl_toml}
    title_path_map: dict[str, str] = None  # {title: relative_path}

    def __post_init__(self):
        self.refresh()

    def refresh(self):
        self.default_apl_map = self.__get_apl_toml(DEFAULT_APL_DIR)
        self.custom_apl_map = self.__get_apl_toml(COSTOM_APL_DIR)
        all_apl_list: list[dict] = list(self.default_apl_map.values()) + list(
            self.custom_apl_map.values()
        )
        all_apl_map: dict[str, dict] = self.default_apl_map | self.custom_apl_map
        self.title_apl_map = {
            apl.get("general", {}).get("title", None): apl for apl in all_apl_list
        }
        self.title_path_map = {
            apl.get("general", {}).get("title", None): relative_path
            for relative_path, apl in all_apl_map.items()
        }
        self.options = (
            title for title in self.title_apl_map.keys() if title is not None
        )

    def dump_toml(self, apl_path):
        raise NotImplementedError()

    def get_general(self, title: str):
        return self.title_apl_map.get(title, {}).get("general", {})

    def change_title(self, former_title: str, new_title: str, new_comment: str = None):
        # Step 1: Check if the former title exists
        if former_title not in self.title_apl_map.keys():
            st.error(f"错误：原标题 '{former_title}' 不存在。")
            return

        # Step 2: Check if the new title already exists (and is not the same as the former title)
        if new_title != former_title and new_title in self.title_apl_map.keys():
            st.error(f"错误：新标题 '{new_title}' 已被其他APL使用。")
            return

        # Step 3: Check if the new title is the same as the former title
        if new_title == former_title and new_comment == self.title_apl_map.get(
            former_title
        ).get("general", {}).get("comment", None):
            st.warning("新旧标题相同，且未提供新注释，无需更改。")
            return

        # Step 4: Get the relative path for the former title
        relative_path = self.title_path_map.get(former_title)
        if not relative_path:
            st.error(
                f"内部错误：找不到标题 '{former_title}' 对应的文件路径。"
            )  # Should not happen if step 1 passed
            return

        # Determine the absolute path
        if relative_path in self.default_apl_map:
            base_dir = DEFAULT_APL_DIR
        elif relative_path in self.custom_apl_map:
            base_dir = COSTOM_APL_DIR
        else:
            st.error(
                f"内部错误：无法确定文件 '{relative_path}' 的所属目录。"
            )  # Should not happen
            return

        absolute_path = os.path.abspath(os.path.join(base_dir, relative_path))

        # Step 5 & 6: Update the title and comment in the TOML file and save
        try:
            with open(absolute_path, "r", encoding="utf-8") as f:
                apl_data = toml.load(f)

            if "general" not in apl_data:
                apl_data["general"] = {}

            apl_data["general"]["title"] = new_title
            if new_comment is not None:
                apl_data["general"]["comment"] = new_comment
            # Optionally update latest_change_time
            # from datetime import datetime
            # apl_data['general']['latest_change_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(absolute_path, "w", encoding="utf-8") as f:
                toml.dump(apl_data, f)

            st.success("正在保存...")
            time.sleep(1)

            # Step 7: Refresh the APL archive
            self.refresh()

        except FileNotFoundError:
            st.error(f"错误：找不到文件 '{absolute_path}'。")
        except Exception as e:
            st.error(f"保存APL文件时出错：{e}")

    def __get_apl_toml(self, apl_path: str) -> dict[str, dict]:
        """根据APL地址获取APL toml的内容
        :param apl_path: APL文件或目录路径
        :return: {relative_path: toml_content} 字典，如果路径无效则返回空字典
        """
        toml_dict_map = {}
        # 将输入路径转换为绝对路径
        base_path = os.path.abspath(apl_path)
        try:
            if os.path.isfile(base_path):
                # 如果是文件，直接处理
                if base_path.endswith(".toml"):
                    try:
                        with open(base_path, "r", encoding="utf-8") as f:
                            toml_dict: dict = toml.load(f)
                            if toml_dict.get("apl_logic", {}).get("logic") is not None:
                                relative_path = os.path.basename(base_path)
                                toml_dict_map[relative_path] = toml_dict
                    except Exception as e:
                        st.exception(f"Error loading TOML file {base_path}: {e}")
            elif os.path.isdir(base_path):
                # 如果是目录，遍历所有toml文件
                for root, _, files in os.walk(base_path):
                    for file in files:
                        if file.endswith(".toml"):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    toml_dict: dict = toml.load(f)
                                    if (
                                        toml_dict.get("apl_logic", {}).get("logic")
                                        is not None
                                    ):
                                        relative_path = os.path.relpath(
                                            file_path, base_path
                                        )
                                        toml_dict_map[relative_path] = toml_dict
                            except Exception as e:
                                st.exception(
                                    f"Error loading TOML file {file_path}: {e}"
                                )
            else:
                # 如果路径既不是文件也不是目录，则记录警告或错误
                st.warning(
                    f"APL path does not exist or is not a file/directory: {apl_path}"
                )
            return toml_dict_map
        except Exception as e:
            raise ValueError(f"读取APL文件失败：{str(e)}")


class APLJudgeTool:
    def __init__(self, raw_apl: dict) -> None:
        self.raw_apl: dict = raw_apl
        self.characters: dict = raw_apl.get("characters", {})
        self.required_chars: list[str] = [
            self._convert_to_name(char) for char in self.characters.get("required", [])
        ]
        self.optional_chars: list[str] = [
            self._convert_to_name(char) for char in self.characters.get("optional", [])
        ]
        self.char_configs: dict[str, dict] = {
            self._convert_to_name(k): v
            for k, v in self.characters.items()
            if k not in ["required", "optional"]
        }  # {name: {config}}
        self.apl_logic: str = raw_apl.get("apl_logic", {}).get("logic", "")

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
            if char not in self.saved_char_config.get("name_box", []):
                missing_chars.append(char)
        return len(missing_chars) == 0, missing_chars

    def judge_optional_chars(self) -> tuple[bool, list[str]]:
        """判断是否满足所有可选角色"""
        missing_chars = []
        for char in self.optional_chars:
            if char not in self.saved_char_config.get("name_box", []):
                missing_chars.append(char)
        return len(missing_chars) == 0, missing_chars

    def judge_char_config(self) -> tuple[bool, dict[str, str | int]]:
        """判断是否满足所有角色配置"""
        missing_configs = {}
        char_name: str  # 角色名称
        config: dict  # 角色配置字典
        key: str  # 配置项名称
        value: str | int  # 配置项值
        saved_value: str | int | list[str | int]  # 保存的配置项值
        for char_name, config in self.char_configs.items():
            for key, value in config.items():
                saved_value = self.saved_char_config.get(char_name, {}).get(key)
                target_value = str(value)
                pass_through_values = ["", "None", "-1"]
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


def listed_alp_options():
    apl_archive = APLArchive()
    st.write("选择一个APL")
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        selected_title = st.selectbox(
            "APL选项", apl_archive.options, label_visibility="collapsed"
        )
    with col2:

        @st.dialog("APL详情")
        def show_apl_detail():
            general = apl_archive.get_general(selected_title)
            st.markdown(
                f"""
                <div style='background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px;
                     border: 1px solid var(--primary-color);'>
                    <h3 style='color: var(--primary-color); margin-bottom: 15px;'>{general.get("title", "无标题")}</h3>
                    <div style='margin-left: 10px;'>
                        <h4 style='color: var(--text-color); margin: 10px 0;'>👤 作者：{general.get("author", "佚名")}</h4>
                        <h4 style='color: var(--text-color); margin: 10px 0;'>📅 创建时间：{general.get("create_time", "无")}</h4>
                        <h4 style='color: var(--text-color); margin: 10px 0;'>🔄 上次修改：{general.get("latest_change_time", "无")}</h4>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button("确定", use_container_width=True):
                st.rerun()

        if st.button("更多", use_container_width=True):
            show_apl_detail()
    with col3:

        @st.dialog("APL重命名")
        def rename_apl():
            relative_path = apl_archive.title_path_map.get(selected_title)
            if relative_path in apl_archive.default_apl_map:
                st.warning("警告：正在修改非自建APL，你需要知道自己在做什么", icon="⚠️")
            new_title = st.text_input("新标题", value=selected_title)
            new_comment = st.text_input(
                "新注释",
                value=apl_archive.get_general(selected_title).get("comment", ""),
            )
            if st.button("确定", use_container_width=True):
                apl_archive.change_title(selected_title, new_title, new_comment)
                st.rerun()

        if st.button("重命名", use_container_width=True):
            rename_apl()
    with col4:
        st.button("新建", use_container_width=True)
