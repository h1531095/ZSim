
# **ZSim APL设计书**

## 0、前言

​ 本文档介绍了ZSim中APL模块（APL）的脚本规则和语法，以帮助每一位想要自己定制队伍手法、寻找更优解的ZSim使用者。

> APL是什么：
>
> ​ APL（Action Priority List） 是《魔兽世界》的一款战斗模拟器（ SimulationCraft） 中一个核心功能，用于定义角色在模拟战斗中执行技能的优先级顺序。通过APL，可以对游戏角色的输出流程进行定制化管理，并且，由程序以100%的完成度进行执行。
>
> <details>
>   <summary style="color: gray">点击查看详细内容</summary>
>   <p style="text-indent: 2em;color: gray">通常，针对同一个角色或是队伍的手法讨论，只能基于玩家的感觉来进行，对于“怎么打比较合适”的手法细节讨论，往往得不出一个最终的结论。即使我们能够借助第三方的游戏计算器，让局部总伤计算更加精确，但也最多只能做到局部精确。某个手法或是某种输出策略对于全局战斗的影响，依旧是难以计算和模拟的。</p>
>   <p style="text-indent: 2em;color: gray">所以，模拟仿真计算器以及APL脚本应运而生。二者结合，就可以真正实现不同策略之间的公平比较，比如：某角色有能量和豆子两种资源，那么到底是优先打能量资源，还是优先打豆子资源呢？通过APL的控制，我们可以设计两套手法，一套永远先打能量，一套永远先打豆子。APL就好像一个水平超高的玩家，它会清晰、稳定地执行我们设计好的既定手法。</p>
>   <p style="text-indent: 2em;color: gray">最终，我们从模拟结果上，可以看到两套手法方案被百分百执行时的输出水平，从而找出其中最优的输出策略。这样的仿真思路，在很多游戏中都能见到，比如Simc、Gscim（原神的模拟仿真软件）等。</p>
>   <p style="text-indent: 2em;color: gray">本模拟器（ZZZSim） 的APL功能正是仿照Simc的APL运行逻辑写的。但是在具体的运行上有一些不同。语法上也针对游戏特色进行了一些优化和改动。</p>
> </details>

---------------

## 1、ZSim中APL模块的运作原理

​ ZSim的APL模块每次运行时，都会从APL脚本的第一行开始，逐行检验其条件部分，直到找到某一行的所有条件全部通过，就将这一行所指向的技能ID输出给下一步程序。每一行APL代码都只能指向一个动作，但是限制条件可以是多个，同一个动作的限制条件之间用“|”分隔符进行隔离，这些条件之间都是“与”关系。

​ 当前版本，如果激活某动作的条件之间存在“或”关系，则应写多行APL代码。

> <details>
>   <summary style="color: gray">后续开发方向</summary>
>   <p style="text-indent: 2em;color: gray">目前，程序只支持“非门”和“与门”，暂不具备解析“或门”的能力。不过，该功能将会是APL功能拓展的首个目标，因为当APL脚本代码涉及到多条件中的多个“或”逻辑时，现有的脚本语法会让APL代码变得非常臃肿冗杂，所以，解析“或”逻辑的功能可以说是迫在眉睫。</p>
> </details>

---

## 2、基本构成

```APL
动作ID|条件1|条件2|条件3|条件4……
```

1. **动作ID**：APL 脚本从上到下逐行解析动作，并执行第一个满足条件的动作。
2. **条件判断**：条件是APL脚本的核心，通常是对角色和敌人的状态（如资源、冷却时间、敌人状态等）的判断。
3. **注释**：使用 `#` 开头的行作为注释，不会被解析器执行，写APL时，应对每一行的代码都进行标注，写明该动作的条件以及逻辑层次。对于比较复杂或是反常的优先级结构，则更应通过#进行说明。

---

## 3、 结构介绍

​ 结下来，我将对Zsim中的APL代码的每个部分进行解释。

​ 首先，让我们来看看一行APL代码，这行代码的意思是：雅将在6个豆子、且身上有丽娜穿透率Buff时，使用满蓄力普攻。

```APL
#满豆自动放满蓄力普攻
1091|action+=|1091_SNA_3|attribute.1091:special_resource==6|buff.1091:exist→Buff-角色-丽娜-核心被动-穿透率==True
```

​ **参数解释：**

|   参数（从左到右）    | <span style="display:inline-block;width: 80px;nowrap">类型</span> | 备注                                                         |
| :-------------------: | :----------------------------------------------------------: | ------------------------------------------------------------ |
|        `1091`         |                           角色CID                            | 在ZSim内部，雅的数字ID为1091                                 |
|      `action+=`       |                           APL类型                            | 意为“常规动作类APL”，这个暂时可以视作无用参数，但是该参数会影响APL解析，无论是缺少参数，还是内容不对，均会引起程序报错，所以还是需要按照格式填写 |
|     `1091_SNA_3`      |                            动作ID                            | 在ZSim内部，雅的蓄力普攻的ID就是“1091_SNA_3”                 |
|   `attribute.1091:`   |                           条件抬头                           | APL代码中的每一个条件模块，都由“条件抬头”和“条件主体”构成，二者之间用“：”进行分隔。条件抬头中，第一个字段的含义是：“何种类型的条件”，而第二个字段的含义是：“去哪儿查该条件”，所以，这里“attribute.1091”的含义就是：雅的属性。注意，“条件抬头”通常都具有完整的两个字段，并且用“.”进行分隔 |
| `special_resource==6` |                           条件主体                           | 这一部分就是“条件主体”了，一个标准的条件主体应该含有条件内容、比较符、结果三个部分。条件内容具体指向某个属性或是某个参数，比较符和数值则构成了“条件”本身，比如“大于XXX点”，“小于等于XXXX点”等 |
|          `|`          |                            分隔符                            | 这是分隔符，两条互为“与”关系的条件之间，应该用“\|”符号进行分隔，其含义基本等价于“且”。相应的，如果不同的条件之间的语义不能用“且”进行连接，那么就意味着它们无法在同一行APL内共存。 |

---

## 4、通用特殊字符

| 符号 | 含义                                                         | <span style="display:inline-block;width: 120px;nowrap">示例</span> | <span style="display:inline-block;width: 300px;nowrap">实例解释</span> |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| \|   | “与”，用于分隔不同的条件单元                                 | 条件1\|条件2                                                 | 需要同时满足条件1**和**条件2                                 |
| !    | “非”，即表达条件的反义。                                     | !action.after: index==1091_SNA_3                             | 上一个技能的ID**不是**1091_SNA_3                             |
| →    | “嵌套结构的下一层索引”，比如某结构下存在较多属性（或是键值），而条件本身又要求精确访问某个内容，此时就可以用“→”标记。注意，这个标记不是->两个字符，而是特殊字符→。正常输入法中输入“You”就可以打出这个字符。 | attribute.1300:special_state→醉花月云转可用次数>=0           | 青衣的特殊状态里，**“醉花月云转可用次数”键值对应的值**大于等于0。 |

----------------------------

### 5、书写规范

- 每行仅定义一个动作，条件可以是多个，但是条件之间必须是“与”关系；
- 同行的不同条件之间，严格使用“`|`”符号分隔。整行代码应不含无意义空格；
- 在输入文本类信息（比如技能ID、Buff的ID等）时，不需要双引号！
- 优先级高的APL应总是处于上方；
- 反义符号`!`应使用英文字体，嵌套结构索引`→`则应使用完整字符，而不要使用`->`，否则程序解析会出错。

---

## 6、全参数详解

> #### 6.1 条件抬头
>
> ​ 注意，目前的条件抬头和条件主体是1对1关系，但是以后随着APL功能的不断拓展，条件主体会逐渐变多。
>
> > <details>
> >     <summary>日后开发方向</summary>
> >     1、action类条件，以后可能会支持查询队伍的上两个动作，或是某动作是否被执行过；</br>
> >     2、status类条件，以后会支持查询角色的某些特别状态（具体看游戏的发展方向）</br>
> >     3、attribute、buff、special类条件，目前暂无升级方向。
> > </details>
>
> <table>
> <tr>
>   <td style="text-align: center;">条件抬头</td>
>   <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">分隔符</td>
>   <td style="text-align: center;">条件主体</td>
>   <td>含义</td>
> </tr>
> <tr>
>   <td rowspan="1"; style="text-align: center;"><code>action</code></td>
>   <td rowspan="6"; style="text-align: center; vertical-align: middle"><code>.</code></td>
>   <td style="text-align: center;"><code>after</code></td>
>   <td>检查整支队伍的上一个动作</td>
> </tr>
> <tr>
>   <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>status</code></td>
>   <td style="text-align: center;"><code>enemy</code></td>
>   <td>检查敌人的状态</td>
> </tr>
> <tr>
>   <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>attribute</code></td>
>   <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>CID</code></td>
>   <td>检查ID为<code>CID</code>的角色的属性，包括属性面板上显示的属性 以及一些其他的特殊状态</td>
> </tr>
> <tr>
>   <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>buff</code></td>
>   <td style="text-align: center;"><code>CID/enemy</code></td>
>   <td>检查ID为<code>CID</code>的角色 / 敌人 身上的buff情况</td>
> </tr>
> <tr>
>   <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>special</code></td>
>   <td style="text-align: center; position: relative;
> background: linear-gradient(to bottom left, transparent 49%, #999 50%, transparent 51%);"></td>
>   <td>特殊类的APL类型，属于暂未开发的功能，会导致报错</td>
> </tr>
> </table>
>
> ----------------------------------
>
> #### 6.2 各条件主体及其子集
>
> <table>
>  <tr>
>    <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">条件抬头+主体</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">分隔符</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">一阶子参</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">分隔符</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">二阶子参</td>
>      <td>含义</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>模板</code></td>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>.</code></td>
>      <td rowspan="1"; style="text-align: center;"><code>占位符</code></td>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>→</code></td>
>      <td rowspan="1"; style="text-align: center;"><code>占位符</code></td>
>      <td>占位符</td>
>  </tr>
>  <tr>
>      <td rowspan="9"; style="text-align: center; vertical-align: middle"><code>status.enemy</code></td>
>      <td rowspan="18"; style="text-align: center; vertical-align: middle"><code>:</code></td>
>      <td rowspan="1"; style="text-align: center;"><code>stun</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人失衡状态</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>QTE_triggerable_times</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人在单轮失衡内可被连携的次数</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>QTE_triggered_times</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人在单轮失衡内已经被连携的次数</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>anomaly_pct_0</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人目前的<span style="color: orange;">物理</span>积蓄百分比</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>anomaly_pct_1</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人目前的<span style="color: red;">火</span>积蓄百分比</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>anomaly_pct_2</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人目前的<span style="color: skyblue;">冰</span>积蓄百分比</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>anomaly_pct_3</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人目前的<span style="color: blue;">电</span>积蓄百分比</td>
>  </tr>  
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>anomaly_pct_4</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人目前的<span style="color: purple;">以太</span>积蓄百分比</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>anomaly_pct_5</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>敌人目前的<span style="color: skyblue;">烈霜</span>积蓄百分比</td>
>  </tr>
>  <tr>
>      <td rowspan="6"; style="text-align: center; vertical-align: middle"><code>attribute.CID</code></td>
>      <td rowspan="1"; style="text-align: center;"><code>energy</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>被查询角色的当前能量</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>decibel</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>被查询角色的当前喧响值</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>special_resource</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>被查询角色的当前特殊资源数量</td>
>  </tr>
>  <tr>
>      <td rowspan="3"; style="text-align: center; vertical-align: middle"><code>special_state</code></td>
>      <td rowspan="3"; style="text-align: center; vertical-align: middle"><code>→</code></td>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>闪络电压</code></td>
>      <td>独属青衣，<code>CID</code>必须为1300。返回的是闪络电压的积攒比例</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>闪络状态</code></td>
>      <td>独属青衣，<code>CID</code>必须为1300。返回的是闪络状态。（即青衣的闪络电压比例是否在75%以上）</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>醉花月云转可用次数</code></td>
>   <td>独属青衣，<code>CID</code>必须为1300。返回的是青衣强化普攻「醉花月云转」的突进打击的剩余可用次数（最多4次）</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center; vertical-align: middle"><code>action.after</code></td>
>      <td rowspan="1"; style="text-align: center;"><code>skill_tag</code></td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: gray">\</td>
>      <td>查询技能的标签</td>
>  </tr>
>  <tr>
>      <td rowspan="2"; style="text-align: center; vertical-align: middle"><code>buff.CID</code></td>
>      <td rowspan="1"; style="text-align: center;"><code>exist</code></td>
>      <td rowspan="2"; style="text-align: center; vertical-align: middle"><code>→</code></td>
>      <td rowspan="2"; style="text-align: center; vertical-align: middle"><code>Buff_Index</code></td>
>      <td>ID为<code>CID</code>的角色身上，名为<code>Buff_Index</code>的Buff的存在情况</td>
>  </tr>
>  <tr>
>      <td rowspan="1"; style="text-align: center;"><code>count</code></td>
>      <td>ID为<code>CID</code>的角色身上，名为<code>Buff_Index</code>的Buff的层数情况</td>
>  </tr>
> </table>

---

## 7、示例及讲解

​ 接下来是APL代码的展示与讲解环节。我选择了一段 青衣、丽娜、雅队伍的爆发期APL来进行展示。注意，为了方便大家理解APL的运行逻辑以及优化流程，这套展示给大家看的APL代码并非是最优解。

​ 在逐行讲解的过程中，我将为大家详细讲解APL的具体作用和逻辑，以及多条APL相互组合时的效果。

> ```APL
> #失衡期间丽娜要满覆盖buff
> 1211|action+=|1211_NA_1|status.enemy:stun==True|!buff.1091:exist→Buff-角色-丽娜-核心被动-穿透率==True
> ```
>
> ​ 在失衡期，如果发现丽娜Buff断了（注意上面的`!`符号表示了反义），那么就要切出丽娜来A一下，续上穿透率Buff。这里不用E的原因是为了省时间。（当然，在合轴模式下，或许E技能更优）

> ```APL
> #满豆自动放满蓄力普攻
> 1091|action+=|1091_SNA_3|attribute.1091:special_resource==6|buff.1091:exist→Buff-角色-丽娜-核心被动-穿透率==True|status.enemy:stun==True
> ```
>
> ​ 在失衡期，雅在拥有6个豆子时，只会在身上有丽娜穿透率Buff的时候释放满蓄力普攻。换言之，如果雅的豆子满了，但是身上没有Buff，那么本行APL的判定就不通过，是不会释放满蓄力普攻的。

> ```APL
> #能量不够时应优先大招
> 1091|action+=|1091_Q|attribute.1091:special_resource>3|attribute.1091:decibel==3000|status.enemy:stun==True|attribute.1091:energy<40
> ```
>
> ​ 在失衡期，雅大招就绪但能量不够时，就会释放大招，无论身上有没有丽娜穿透率Buff。但是请注意，单独来看这是一条有问题的APL。因为该条APL会导致雅在满豆、满喧响的情况下优先开大。想要修复这一手法逻辑，只需要在这一行APL的末尾加上一个条件即可：
>
> ```APL
> ……|attribute.1091:special_resource<6
> ```
>
> ​ 只要将豆子的数量锁定住，那么这一条APL就能正常发挥作用。
>
> ​ 但是有趣的是，如果将以上3条APL同时激活，并且按照文中展示的顺序进行排列，那么即使是有缺陷的本行APL，也不会导致出错。
>
> > <details>
> >     <summary style="color: gray">展开说明</summary>
> >     <p style="text-indent: 2em; color: gray">由于APL的执行顺序是从上到下，所以，在执行到这一行之前，前两行是一定没有通过的。前面我们介绍过，导致本行APL出错的条件集为：满豆且满喧响。那么这种场景，会在第二行APL被拦下来。上面展示的第二行APL，就是让雅在有穿透率Buff的时候，优先泄豆。</br></p>
> >     <p style="text-indent: 2em; color: gray">有的读者可能又注意到了新的问题。“那如果身上恰好没有Buff，且满豆，那APL的执行不就漏到第三行了吗？”</br></p>
> >     <p style="text-indent: 2em; color: gray">放心，这个情况也是不会出现的。因为在失衡期，身上没有Buff的情况会被第一行APL拦下来。</br></p>
> >     <p style="text-indent: 2em; color: gray">总之，如果APL的运行来到了第三行，那么就说明当前起码是：有穿透率Buff且不满豆的状态，也就是说，我们补写的那个条件判定，在第三行的位置上，是永远不会起到作用的。</br></p>
> >     <p style="text-indent: 2em; color: gray">可见，APL的优先级思维要求大家以全新的视角来拆分、看待自己的游戏逻辑，在稍后的章节中，我会给出一些书写APL的小方法，来帮助大家梳理优先级。</p>
> > </details>

> ```APL
> #豆子相差很远时，也优先开大
> 1091|action+=|1091_Q|attribute.1091:special_resource<4|attribute.1091:decibel==3000|status.enemy:stun==True
> 
> ```
>
> ​ 这一句APL就更有意思了。和上一句的大招APL相比，这一句改变了豆子的判定，并且取消了能量的判定。只有满足以下条件（可以简单概括为：要么豆子数量不对，要么能量值不对），APL才的执行才会来到第四行（不满足的条件为<span style="color: orange">橙色</span>）：
>
> ​ **情况1：**满喧响（默认） | 豆子∈(3, 6) | <span style="color: orange">能量足够</span>
>
> ​ **情况2：**满喧响（默认） | <span style="color: orange">豆子∈[0, 3]</span> | 能量不够
>
> ​ **情况3：**满喧响（默认） | <span style="color: orange">豆子∈[0, 3]</span> | <span style="color: orange">能量足够</span>
>
> ​ 而本条APL针对的恰好就是**情况2**，即在有没能量，且大招不会导致豆子溢出时开大。

> ```APL
> #泄能逻辑
> 1091|action+=|1091_E_EX_A_1|status.enemy:stun==True|attribute.1091:energy>=40|attribute.1091:special_resource<6
> ```
>
> ​ 这里展示的APL是雅在失衡期的泄能逻辑。如果你全局检查目前已经展示的5行APL，你就不难发现本行APL中藏着一个无效条件，对，就是能量判定。从上面的三种情况的列举可以看出，能够进入到这一行的APL，均是能量足够的情况。所以能量判定在这一行是无效的。
>
> ​ 这也意味着，这一行APL的作用，就是“无脑泄蓝”，哪怕此时喧响值足够，也是优先打强化E。<span style="color: gray">（很明显，这个逻辑是不对的，在实战中我们面对豆子不满、且有能量、有大的情况，往往会先进行豆子判断。如果开大豆子不溢出，那就优先开大，如果开大豆子溢出，那就优先打E。）</span>
>
> ​ 根据上述推理，这一行的APL实际上可以优化为以下两行来执行。
>
> ```APL
> 1091|action+=|1091_E_EX_A_1|status.enemy:stun==True|attribute.1091:special_resource<6|attribute.1091:special_resource>4
> 1091|action+=|1091_Q|status.enemy:stun==True|attribute.1091:special_resource<3
> ```
>
> ​ 顺便，诸位读者可能已经发现了，这两行APL如果调换先后顺序，实际上起到的效果是完全相同的。这也是APL的一个核心特点：当情况的分类讨论抵达最后一层时，最后一层的APL先后顺序不影响实际效果。因为它们本质上是同优先级的APL。
