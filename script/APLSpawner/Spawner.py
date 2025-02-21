import platform
import gradio as gr
import sys
import pandas as pd

# 系统路径设置
os_name = platform.system()
if os_name == "Windows":
    sys.path.append("F:/GithubProject/ZZZ_Calculator")
elif os_name == "Darwin":
    sys.path.append("/Users/steinway/Code/ZZZ_Calculator")
else:
    raise NotImplementedError("Unsupported OS")
from define import CHARACTER_DATA_PATH

# 初始化角色数据
char_data = pd.read_csv(CHARACTER_DATA_PATH)
full_char_name_list = char_data['name'].tolist()


class SpawnerManager:
    def __init__(self):
        self.selected = {1: None, 2: None, 3: None}
        self.locked = False  # 新增锁定状态

    def all_selected(self) -> bool:
        """检查是否所有位置都已选择"""
        return all(v is not None for v in self.selected.values())

    def get_available_chars(self, current_pos: int) -> list:
        """获取指定位置的可用角色列表（只排除其他位置的选择）"""
        other_selected = {
            k: v for k, v in self.selected.items()
            if k != current_pos and v is not None
        }
        return [c for c in full_char_name_list if c not in other_selected.values()]


def handle_select(pos: int, value: str, current_vals: tuple) -> tuple:
    if manager.locked:  # 如果已锁定，直接返回当前状态
        return (manager.selected[pos],) + current_vals

    # 更新选择数据
    manager.selected[pos] = value

    updates = []
    for i in [1, 2, 3]:
        # 获取该菜单专属的可用列表
        available = manager.get_available_chars(current_pos=i)
        current_val = current_vals[i - 1]

        if i == pos:
            # 当前菜单：强制保留选择并确保选项包含该值
            valid_choices = available + [value] if value not in available else available
            new_value = value
        else:
            # 其他菜单：严格校验有效性
            valid_choices = available
            new_value = current_val if current_val in valid_choices else None

        updates.append(gr.update(
            choices=valid_choices,
            value=new_value,
            interactive=not manager.locked  # 根据锁定状态设置交互性
        ))

    return (value, *updates)


# 新增按钮状态更新函数
def update_button_state(m1, m2, m3, locked):
    # 如果已锁定：按钮始终可点击（用于解锁）
    if locked:
        return gr.Button(interactive=True)

    # 未锁定时：仅当全部选择时可点击
    all_selected = all([m1, m2, m3])
    return gr.Button(interactive=all_selected)


def toggle_lock(locked):
    new_locked = not locked
    manager.locked = new_locked
    return [
        new_locked,
        gr.update(open=not new_locked),  # 控制折叠面板
        gr.update(interactive=not new_locked),  # 菜单1
        gr.update(interactive=not new_locked),  # 菜单2
        gr.update(interactive=not new_locked),  # 菜单3
        gr.Button(value="🔓 解锁" if new_locked else "🔒 锁定")  # 更新按钮图标
    ]


# 初始化管理器
manager = SpawnerManager()

# 构建界面
with gr.Blocks(title="角色选择器", css=".locked { opacity: 0.6; }") as demo:
    # 锁定状态存储
    locked_state = gr.State(value=False)

    # 可折叠面板
    with gr.Accordion("角色选择面板", open=True) as accordion:
        with gr.Row():
            menu1 = gr.Dropdown(label="1号位", choices=full_char_name_list)
            menu2 = gr.Dropdown(label="2号位", choices=full_char_name_list)
            menu3 = gr.Dropdown(label="3号位", choices=full_char_name_list)

    # 结果显示行
    with gr.Row():
        display1 = gr.Textbox(label="1号位选择", interactive=False)
        display2 = gr.Textbox(label="2号位选择", interactive=False)
        display3 = gr.Textbox(label="3号位选择", interactive=False)

    # 事件绑定
    for idx, (menu, display) in enumerate(zip([menu1, menu2, menu3], [display1, display2, display3]), 1):
        menu.change(
            fn=lambda val, m1, m2, m3, pos=idx: handle_select(pos, val, (m1, m2, m3)),
            inputs=[menu, menu1, menu2, menu3],
            outputs=[display, menu1, menu2, menu3]
        )
    # 锁定按钮
    lock_button = gr.Button("🔒 锁定并进入下一步", variant="primary", interactive=False)
    gr.on(
        triggers=[menu1.change, menu2.change, menu3.change, locked_state.change],
        fn=update_button_state,
        inputs=[menu1, menu2, menu3, locked_state],
        outputs=lock_button
    )

    # 锁定按钮事件
    lock_button.click(
        fn=toggle_lock,
        inputs=locked_state,
        outputs=[locked_state, accordion, menu1, menu2, menu3, lock_button]
    )

demo.launch()
