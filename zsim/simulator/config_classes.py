from typing import Literal
from pydantic import BaseModel, Field, model_validator


class SimulationConfig(BaseModel):
    """模拟配置参数"""

    # all mode common:
    stop_tick: int | None = Field(None, description="指定模拟的tick数量")
    mode: Literal["normal", "parallel"] | None = Field(None, description="运行模式")
    func: Literal["attr_curve", "weapon"] | None = Field(None, description="功能选择")
    adjust_char: Literal[1, 2, 3] | None = Field(None, description="调整的角色相对位置")
    run_turn_uuid: str | None = Field(None, description="本轮次并行运行的uuid")

    # only for attr_curve:
    sc_name: str | None = Field(None, description="要调整的副词条名称")
    sc_value: int | None = Field(None, description="要调整的副词条数量")
    remove_equip: bool | None = Field(None, description="移除装备")

    # only for weapon:
    weapon_name: str | None = Field(None, description="要调整的武器名称")
    weapon_level: Literal[1, 2, 3, 4, 5] | None = Field(
        None, description="要调整的武器精炼等级"
    )

    # optinal:
    # apl_path: str | None = Field(None, description="APL代码相对路径")

    @model_validator(mode="after")
    def validate_conditional_fields(self):
        if self.func == "attr_curve":
            if self.sc_name is None or self.sc_value is None:
                raise ValueError("当func为attr_curve时，必须提供sc_name和sc_value")
        elif self.func == "weapon":
            if self.weapon_name is None or self.weapon_level is None:
                raise ValueError("当func为weapon时，必须提供weapon_name和weapon_level")
        return self
