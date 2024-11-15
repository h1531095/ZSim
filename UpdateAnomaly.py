from AnomalyBar import AnomalyBar
from AnomalyBar.CopyAnomalyForOutput import Disorder, NewAnomaly
import numpy as np
import Enemy
import Buff


def spawn_output(anomaly_bar, mode_number):
    """
    该函数用于抛出一个新的属性异常类
    """
    if not isinstance(anomaly_bar, AnomalyBar):
        raise TypeError(f'{anomaly_bar}不是AnomalyBar类！')

    # 先处理快照，使其除以总权值。
    anomaly_bar.current_ndarray = anomaly_bar.current_ndarray / anomaly_bar.current_anomaly
    output = anomaly_bar.element_type, anomaly_bar.current_ndarray
    if mode_number == 0:
        output = NewAnomaly(anomaly_bar)
    elif mode_number == 1:
        output = Disorder(anomaly_bar)
    # return之前将两个current重置。
    anomaly_bar.current_anomaly = np.float64(0)
    anomaly_bar.current_ndarray = np.zeros((1, anomaly_bar.current_ndarray.shape[0]), dtype=np.float64)  # 保持 1 列
    return output


def anomaly_effect_active(bar: AnomalyBar, DYNAMIC_BUFF_DICT: dict, exist_buff_dict: dict, timenow: int, enemy: Enemy.Enemy):
    """
    该函数的作用是创建属性异常附带的debuff和dot，
    debuff与dot的index写在了Anomaly.accompany_debuff和Anomaly.accompany_dot里。
    这里通过Buff的BuffInitialize函数来根据Buff名，直接提取对应的双字典，
    并且直接放进Buff的构造函数内，对新的Buff进行实例化。
    然后，回传给exist_buff_dict中的Buff0。
    """
    if bar.accompany_debuff:
        all_match, config_dict, judge_dict = Buff.BuffInitialize(bar.accompany_debuff, exist_buff_dict)
        anomaly_debuff_new = Buff.Buff(judge_dict, config_dict)
        #   修改一些必要的属性。
        anomaly_debuff_new.simple_start(timenow, exist_buff_dict['enemy'])
        DYNAMIC_BUFF_DICT['enemy'].append(anomaly_debuff_new)
        enemy.dynamic.dynamic_debuff_list.append(anomaly_debuff_new)
    if bar.accompany_dot:
        pass


def update_anomaly(element_type: int, enemy: Enemy.Enemy, time_now: int, event_list: list, DYNAMIC_BUFF_DICT: dict, exist_buff_dict: dict, timenow: int):
    """
    该函数需要在Loading阶段，submission是End的时候运行。
    用于判断该次属性异常触发应该是新建、替换还是触发紊乱。
    第一个参数是属性种类，第二个参数是Enemy类的实例，第三个参数是当前时间
    如果判断通过触发，则会立刻实例化一个对应的属性异常实例（自带复制父类的状态与属性），
    """
    bar = enemy.anomaly_bars_dict[element_type]
    if not isinstance(bar, AnomalyBar):
        raise TypeError(f'{type(bar)}不是Anomaly类！')
    '''
    只要调用了本函数，就要顺便检查一下当前的异常情况。以防意外触发了两种异常状态还不报错搁那儿嘎嘎算。
    '''
    active_anomaly_check = 0
    active_anomaly_list = []
    for element_number, element in enemy.trans_anomaly_effect_to_str.items():
        if getattr(enemy.dynamic, element):
            active_anomaly_check += 1
            active_anomaly_list.append(element_number)
        if active_anomaly_check >= 2:
            raise ValueError(f'当前同时存在两种以上的异常状态！！！')
    bar.max_anomaly = getattr(enemy, f'max_anomaly_{enemy.trans_element_number_to_str[element_type]}')
    if len(active_anomaly_list) != 0:
        last_anomaly_element_type = active_anomaly_list[0]
    else:
        last_anomaly_element_type = None
    if bar.current_anomaly >= bar.max_anomaly:
        bar.is_full = True
        # 积蓄值蓄满了，但是属性异常不一定触发，还需要验证一下内置CD
        bar.ready_judge(time_now)
        if bar.ready:
            # 内置CD检测也通过之后，属性异常正式触发。现将需要更新的信息更新一下。
            enemy.update_anomaly(element_type)
            bar.ready = False
            bar.anomaly_times += 1
            bar.last_anomaly_time = time_now

            '''
            更新完毕，现在正式进入分支判断
            无论是哪个分支，都需要涉及enemy下的两大容器：enemy_debuff_list以及enemy_dot_list的修改，同时，也可能需要修改exist_buff_dict以及DYNAMIC_BUFF_DICT
            '''
            if element_type in active_anomaly_list or active_anomaly_check == 0:
                """
                这个分支意味着：触发了属性异常效果，并且enemy身上已经存在对应的异常，此时应该执行的策略是“更新”，模式编码是0
                该策略下，只需要抛出一个新的属性异常给dot，不需要改变enemy的信息，只需要更新enemy的dot和debuff 两个list即可。
                """
                mode_number = 0
                new_anomaly = spawn_output(bar, mode_number)
                anomaly_effect_active(bar, DYNAMIC_BUFF_DICT, exist_buff_dict['enemy'], timenow, enemy)
                event_list.append(new_anomaly)
                print(f'触发{enemy.trans_element_number_to_str[element_type]}属性异常！')
            elif element_type not in active_anomaly_list and len(active_anomaly_list) > 0:
                '''
                这个分支意味着：要结算紊乱。那么需要复制的就不应该是新的这个属性异常，而应该是老的属性异常的bar实例。
                '''
                mode_number = 1
                last_anomaly_bar = enemy.anomaly_bars_dict[last_anomaly_element_type]
                setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[last_anomaly_element_type], False)
                setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)
                disorder = spawn_output(last_anomaly_bar, mode_number)
                new_anomaly = spawn_output(bar, 1)
                event_list.append(disorder)
                event_list.append(new_anomaly)
                print(f'触发紊乱！')
            setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)       # 同步更新enemy.dynamic下面的属性异常状态。


            # TODO: 实现属性异常触发后，同步向DYNAMIC_BUFF_DICT添加buff，或是添加Dot，
            # TODO：当前问题：新的buff的实例化需要读取CSV，频繁读取可能会影响性能。需要重新定位实例化Buff的位置。








