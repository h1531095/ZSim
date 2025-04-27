# APL 编辑器实现路线

本文档概述了基于 `APL template.toml` 的 WebUI APL 编辑器的实现计划。

## 核心功能

### 1. APL 文件管理

- [ ] **加载 APL:**

  - 从 `DEFAULT_APL_DIR` 和 `COSTOM_APL_DIR` 加载 TOML 文件。
  - 提供下拉列表或其他方式选择要编辑的 APL (基于 `title`)。 (部分已实现于 `listed_alp_options`)
  - 加载后显示 APL 的内容，并提供修改框
- [ ] **修改 APL：**

  - 允许用户在界面上直接编辑 APL 的内容。
  - 提供保存/取消功能。
  - 角色配置项（角色名称、武器、星魂、主词条等）使用下拉选择框
  - 区分必选角色和可选角色。
  - 区分 `required` 和 `optional` 角色。
  - 区分 `cinema`, `weapon`, `equip_set4` 等配置项。
  - logic 部分的编辑 (核心难点)，现阶段由一个大文本框实现
- [ ] **删除 APL:**

  - 提供删除已加载 APL 的功能。
  - 提供删除确认提示。
- [ ] **保存 APL:**

  - 将编辑后的内容保存回对应的 TOML 文件。
  - 区分默认 APL 和自定义 APL 的保存逻辑（例如，修改默认 APL 时可能需要另存为自定义 APL）。
  - 自动更新 `latest_change_time`。
- [X] **新建 APL:**

  - 提供基于 `APL template.toml` 创建新 APL 文件的功能。
  - 新文件默认保存在 `COSTOM_APL_DIR`。
  - 需要用户输入新的 `title` 和 `author` (可选)。
- [ ] **重命名:** (部分已实现于 `rename_apl` 对话框)

  - 修改 APL 的 `title` 和 `comment`。
  - 考虑是否允许修改 `author`。

### 2. General 部分编辑

- [ ] **显示:** 在界面上显示当前加载 APL 的 `title`, `comment`, `author`, `create_time`, `latest_change_time`。
- [ ] **编辑:**
  - 提供输入框编辑 `title` (需检查重名)。 (已实现)
  - 提供文本区域编辑 `comment`。 (已实现)
  - 提供输入框编辑 `author`。
  - 考虑 `create_time` 和 `latest_change_time` 的处理方式（只读显示或允许修改）。

### 3. Characters 部分编辑

- [ ] **显示:**
  - 清晰展示 `required` 和 `optional` 角色列表。
  - 展示每个已配置角色的详细设置 (`cinema`, `weapon`, `equip_set4` 等)。
- [ ] **编辑 `required` / `optional` 列表:**
  - 提供多选框或类似控件，允许用户从可用角色列表中选择/取消选择角色，添加到 `required` 或 `optional`。
  - 需要一个角色列表来源 (可能来自 `CHAR_CID_MAPPING` 或其他配置)。
- [ ] **编辑角色具体配置:**
  - 允许添加新的角色配置段 (e.g., `[characters."新角色"]`)。
  - 允许删除已有的角色配置段。
  - 为每个角色的配置项 (`cinema`, `weapon`, `equip_set4` 等) 提供合适的编辑控件：
    - `cinema`: 可能需要多选框或数字输入 (根据是列表还是单个数字)。
    - `weapon`: 文本输入或下拉选择 (如果武器列表已知)。
    - `equip_set4`: 文本输入或下拉选择 (如果套装列表已知)。
  - 需要动态处理不同角色的不同配置项。

### 4. APL Logic 部分编辑

- [ ] **显示:** 使用文本区域 (Text Area) 显示 `logic` 字符串。
- [ ] **编辑:** 允许用户直接在文本区域中编辑 `logic` 内容。
- [ ] **(可选) 增强功能:**
  - 语法高亮 (如果 APL 逻辑有固定语法)。
  - 格式校验或错误提示。
  - 提供常用逻辑片段的插入功能。

## UI/UX 考虑

- 使用 Streamlit 组件构建界面。
- 布局清晰，分区明确（General, Characters, Logic）。
- 提供清晰的保存/取消操作。
- 错误处理和用户反馈 (例如，保存成功/失败，输入校验错误)。

## 后续步骤

1. 实现文件管理功能 (新建)。
2. 完善 General 部分的编辑功能。
3. 实现 Characters 部分的编辑功能 (核心难点)。
4. 实现 APL Logic 部分的编辑功能。
5. 添加可选的增强功能和 UI/UX 优化。
