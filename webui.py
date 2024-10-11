from CharSet_new import Character
import gradio as gr

def create_character(char_name, weapon, weapon_level, sp_limit, ds4, ds2a, ds2b, ds2c, d4, d5, d6, a,b,c,d,e,f,g,h,i):
    character = Character(
        char_name=char_name,
        weapon=weapon,
        weapon_level=weapon_level,
        sp_limit=sp_limit,
        equip_set4=ds4, equip_set2_a=ds2a, equip_set2_b=ds2b, equip_set2_c=ds2c,
        drive4=d4, drive5=d5, drive6=d6,
        scATK_percent=a, scATK=b, scHP_percent=c, scHP=d, scDEF_percent=e, scDEF=f, scAnomalyProficiency=g, scPEN=h, scCRIT=i,
    )
    statement = Character.Statement(character)
    return statement.statement

# 定义 Gradio 接口
def web_ui(char_name, weapon, weapon_level, sp_limit, ds4, ds2a, ds2b, ds2c, d4, d5, d6, a,b,c,d,e,f,g,h,i):
    statement = create_character(char_name, weapon, weapon_level, sp_limit, ds4, ds2a, ds2b, ds2c, d4, d5 , d6, a,b,c,d,e,f,g,h,i)
    return statement

# 创建 Gradio 应用
iface = gr.Interface(
    fn=web_ui,
    inputs=[
        gr.Textbox(value='艾莲', label="角色名字"),
        gr.Textbox(value='深海访客', label="武器名字"),
        gr.Slider(minimum=1, maximum=10, step=1, label="武器精炼等级"),
        gr.Slider(minimum=0, maximum=120, step=1, value=120,label="能量上限"),
        gr.Textbox(label="驱动盘套装4"),
        gr.Textbox(value='极地重金属', label="驱动盘套装2A"),
        gr.Textbox(label="驱动盘套装2B"),
        gr.Textbox(label="驱动盘套装2C"),
        gr.Textbox(label="四号位"),
        gr.Textbox(label="五号位"),
        gr.Textbox(label="六号位"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 ATK%"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 ATK"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 HP%"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 HP"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 DEF%"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 DEF"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 异常精通"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 PEN"),
        gr.Slider(minimum=0, maximum=100, step=1, label="副词条 CRIT")
    ],
    outputs=gr.JSON(label="角色面板"),
    title="角色面板计算器",
    description="输入角色信息，计算角色面板。",
    allow_flagging="never"
)

# 启动 Gradio 应用
if __name__ == "__main__":
    iface.launch()