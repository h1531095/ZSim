from AnomalyBar import AnomalyBar
from AnomalyBar.CopyAnomalyForOutput import Disorder, NewAnomaly
import numpy as np
import Enemy
import importlib
from Buff.BuffAddStrategy import BuffAddStrategy
from Dot.BaseDot import Dot


anomlay_dot_dict = {
    1: 'Ignite',
    2: 'Freez',
    3: 'Shock',
    4: 'Corruption',
    5: 'Freez'
}


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


def anomaly_effect_active(bar: AnomalyBar, timenow: int, enemy: Enemy.Enemy, new_anomaly, element_type):
    """
    该函数的作用是创建属性异常附带的debuff和dot，
    debuff与dot的index写在了Anomaly.accompany_debuff和Anomaly.accompany_dot里。
    这里通过Buff的BuffInitialize函数来根据Buff名，直接提取对应的双字典，
    并且直接放进Buff的构造函数内，对新的Buff进行实例化。
    然后，回传给exist_buff_dict中的Buff0。
    """
    if bar.accompany_debuff:
        for debuff in bar.accompany_debuff:
            BuffAddStrategy(debuff)
    if bar.accompany_dot:
        new_dot = spawn_anomaly_dot(element_type, timenow, new_anomaly)
        if new_dot:
            for dots in enemy.dynamic.dynamic_dot_list[:]:
                if dots.ft.index == new_dot.ft.index:
                    dots.end(timenow)
                    enemy.dynamic.dynamic_dot_list.remove(dots)
            enemy.dynamic.dynamic_dot_list.append(new_dot)
            # event_list.append(new_dot)


def update_anomaly(element_type: int, enemy: Enemy.Enemy, time_now: int, event_list: list):
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
    anomaly_name_list = []
    for element_number, element_anomaly_effect in enemy.trans_anomaly_effect_to_str.items():
        if getattr(enemy.dynamic, element_anomaly_effect):
            anomaly_name_list.append(element_anomaly_effect)
            anomaly_name_list_unique = list(set(anomaly_name_list))
            active_anomaly_check = len(anomaly_name_list_unique)
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
            bar.last_active = time_now
            bar.active = True

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
                anomaly_effect_active(bar, time_now, enemy, new_anomaly, element_type)
                if not element_type in [2,5]:
                    """
                    如果是新触发的冰异常，那么在触发当场不应该碎冰。碎冰应该由碎冰DOT抛出。
                    当前分支是非冰异常分支，所以修改完anomaly状态之后直接向eventlist里面添加事件。
                    """
                    setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)
                    event_list.append(new_anomaly)
                else:
                    """
                    当前分支是冰异常和烈霜异常分支，所以触发异常后，不向eventlist里面添加事件。
                    同时，frozen的状态参数被打开。
                    """
                    setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)
                    enemy.dynamic.frozen = True
            elif element_type not in active_anomaly_list and len(active_anomaly_list) > 0:
                '''
                这个分支意味着：要结算紊乱。那么需要复制的就不应该是新的这个属性异常，而应该是老的属性异常的bar实例。
                '''
                mode_number = 1
                last_anomaly_bar = enemy.anomaly_bars_dict[last_anomaly_element_type]
                setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[last_anomaly_element_type], False)
                setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)
                if element_type in [2, 5]:
                    enemy.dynamic.frozen = True
                disorder = spawn_output(last_anomaly_bar, mode_number)
                new_anomaly = spawn_output(bar, 1)
                for dots in enemy.dynamic.dynamic_dot_list[:]:
                    if not isinstance(dots, Dot):
                        raise TypeError(f'{dots}不是DOT类！')
                    if dots.ft.index == 'Freez':
                        if dots.dy.effect_times > dots.ft.max_effect_times:
                            raise ValueError('该Dot任务已经完成，应当被删除！')
                        event_list.append(dots.anomaly_data)
                        dots.dy.ready = False
                        dots.dy.last_effect_ticks = time_now
                        dots.dy.effect_times += 1
                        enemy.dynamic.dynamic_dot_list.remove(dots)
                        enemy.dynamic.frozen = False
                        print('因紊乱而强行移除碎冰')
                event_list.append(disorder)
                if not element_type in [2,5]:
                    event_list.append(new_anomaly)
                # else:
                #     return element_type, time_now
                print(f'触发紊乱！')
            setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)       # 同步更新enemy.dynamic下面的属性异常状态。
    #     else:
    #         return element_type, time_now
    # else:
    #     return element_type, time_now


def spawn_anomaly_dot(element_type, timenow, bar=None):
    if element_type in anomlay_dot_dict:
        class_name = anomlay_dot_dict[element_type]
        new_dot = create_dot_instance(class_name, bar)
        if isinstance(new_dot, Dot):
            new_dot.start(timenow)
        return new_dot
    else:
        return False


def create_dot_instance(class_name, bar=None):
    # 动态导入相应模块
    module_name = f"Dot.Dots.{class_name}"  # 假设你的类都在dot.DOTS模块中
    try:
        module = importlib.import_module(module_name)  # 导入模块
        class_obj = getattr(module, class_name)  # 获取类对象
        if bar:
            return class_obj(bar)
        else:
            return class_obj()  # 创建并返回类实例
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Error loading class {class_name}: {e}")











