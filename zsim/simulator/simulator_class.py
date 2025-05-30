from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from simulator.dataclasses import SimCfg

import gc

from define import APL_MODE, APL_PATH, ENEMY_ADJUST_ID, ENEMY_DIFFICULTY, ENEMY_INDEX_ID
from sim_progress import Buff, Load
from sim_progress.Character.skill_class import Skill
from sim_progress.data_struct import ActionStack, Decibelmanager, ListenerManger
from sim_progress.Enemy import Enemy
from sim_progress.Preload import PreloadClass
from sim_progress.Report import start_report_threads
from sim_progress.ScheduledEvent import ScheduledEvent as ScE
from sim_progress.Update.Update_Buff import update_dynamic_bufflist
from sim_progress.RandomNumberGenerator import RNG
from simulator.dataclasses import (
    CharacterData,
    GlobalStats,
    InitData,
    LoadData,
    ScheduleData,
)


class Simulator:
    tick: int
    crit_seed: int
    init_data: InitData
    char_data: CharacterData
    load_data: LoadData
    schedule_data: ScheduleData
    global_stats: GlobalStats
    skills: list[Skill]
    preload: PreloadClass
    game_state: dict[str, Any]
    decibel_manager: Decibelmanager
    listener_manager: ListenerManger
    rng_instance: RNG
    in_parallel_mode: bool
    sim_cfg: "SimCfg" | None

    def reset_simulator(self, sim_cfg: "SimCfg" | None):
        """重置模拟器实例为初始状态。"""
        self.reset_sim_data(sim_cfg)  # 重置所有全局变量
        start_report_threads(sim_cfg)  # 启动线程以处理日志和结果写入

    def reset_sim_data(self, sim_cfg: "SimCfg" | None):
        """重置所有全局变量为初始状态。"""
        if sim_cfg is not None:
            self.in_parallel_mode = True
            self.sim_cfg = sim_cfg
        else:
            self.in_parallel_mode = False
            self.sim_cfg = None
        self.tick = 0
        self.crit_seed = 0
        self.init_data = InitData(sim_cfg)

        self.char_data = CharacterData(self.init_data, sim_cfg, sim_instance=self)
        self.load_data = LoadData(
            name_box=self.init_data.name_box,
            Judge_list_set=self.init_data.Judge_list_set,
            weapon_dict=self.init_data.weapon_dict,
            cinema_dict=self.init_data.cinema_dict,
            action_stack=ActionStack(),
            char_obj_dict=self.char_data.char_obj_dict,
            sim_instance=self,
        )
        self.schedule_data = ScheduleData(
            enemy=Enemy(
                index_ID=ENEMY_INDEX_ID,
                adjust_ID=ENEMY_ADJUST_ID,
                difficulty=ENEMY_DIFFICULTY,
                sim_instance=self,
            ),
            char_obj_list=self.char_data.char_obj_list,
            sim_instance=self,
        )
        if self.schedule_data.enemy.sim_instance is None:
            self.schedule_data.enemy.sim_instance = self

        self.global_stats = GlobalStats(
            name_box=self.init_data.name_box, sim_instance=self
        )
        skills = [char.skill_object for char in self.char_data.char_obj_list]
        self.preload = PreloadClass(
            skills, load_data=self.load_data, apl_path=APL_PATH, sim_instance=self
        )

        self.game_state = {  # noqa: F841
            "tick": self.tick,
            "init_data": self.init_data,
            "char_data": self.char_data,
            "load_data": self.load_data,
            "schedule_data": self.schedule_data,
            "global_stats": self.global_stats,
            "preload": self.preload,
        }
        self.decibel_manager = Decibelmanager(self)
        self.listener_manager = ListenerManger(self)
        self.rng_instance = RNG(sim_instance=self)

    def main_loop(self, stop_tick: int = 1000, *, sim_cfg: "SimCfg" | None = None):
        self.reset_simulator(sim_cfg)
        while True:
            # Tick Update
            # report_to_log(f"[Update] Tick step to {tick}")
            update_dynamic_bufflist(
                self.global_stats.DYNAMIC_BUFF_DICT,
                self.tick,
                self.load_data.exist_buff_dict,
                self.schedule_data.enemy,
            )  # type: ignore

            # Preload
            self.preload.do_preload(
                self.tick,
                self.schedule_data.enemy,
                self.init_data.name_box,
                self.char_data,
            )  # type: ignore
            preload_list = self.preload.preload_data.preload_action  # type: ignore

            if stop_tick is None:
                if not APL_MODE and self.preload.preload_data.skills_queue.head is None:  # type: ignore
                    stop_tick = self.tick + 120
            elif self.tick >= stop_tick:
                break

            # Load
            if preload_list:
                Load.SkillEventSplit(
                    preload_list,
                    self.load_data.load_mission_dict,
                    self.load_data.name_dict,
                    self.tick,
                    self.load_data.action_stack,
                )
            Load.DamageEventJudge(
                self.tick,
                self.load_data.load_mission_dict,
                self.schedule_data.enemy,
                self.schedule_data.event_list,
                self.char_data.char_obj_list,
                dynamic_buff_dict=self.global_stats.DYNAMIC_BUFF_DICT,
            )
            Buff.BuffLoadLoop(
                self.tick,
                self.load_data.load_mission_dict,
                self.load_data.exist_buff_dict,
                self.init_data.name_box,
                self.load_data.LOADING_BUFF_DICT,
                self.load_data.all_name_order_box,
                sim_instance=self,
            )
            Buff.buff_add(
                self.tick,
                self.load_data.LOADING_BUFF_DICT,
                self.global_stats.DYNAMIC_BUFF_DICT,
                self.schedule_data.enemy,
            )
            # Load.DamageEventJudge(tick, load_data.load_mission_dict, schedule_data.enemy, schedule_data.event_list, char_data.char_obj_list)
            # ScheduledEvent
            sce = ScE(
                self.global_stats.DYNAMIC_BUFF_DICT,
                self.schedule_data,
                self.tick,
                self.load_data.exist_buff_dict,
                self.load_data.action_stack,
                sim_instance=self,
            )
            sce.event_start()
            self.tick += 1
            print(f"\r{self.tick} ", end="")

            if self.tick % 500 == 0 and self.tick != 0:
                gc.collect()

    def __deepcopy__(self, memo):
        return self

    # FIXME: 这里存在一些问题。在将Simulator对象传入各个模块后，
    #  若这些模块进行deepcopy操作，这会导致Simulator 也被复制一次，
    #  连带着部分对象的__new__方法被重新执行，可能会让一些对象被重复初始化。
    #  这个问题并未导致模拟器出现严重的问题——原因是deepcopy只会调用一次__new__来新建，以及__dict__来进行复制，而不会调用__init__。
    #  而sim_instance中大部分的对象都只自定义了__init__方法，并不涉及__nwe__，只有那些重写了__new__方法的对象才会出现这个问题。
    #  为了解决这个问题，我重写了Simulator的__deepcopy__方法，使其直接返回自身。
    #  但是，在与Ai交流的过程中，它指出sim_instance 的体积庞大，就算是解决了deep_copy导致初始化的问题，
    #  内存问题依旧存在，并且亟待解决，这让我回想起了两个现象，似乎都指向这个问题：
    #  1、昨日跑属性收益时出现了电脑爆炸卡的情况，
    #  2、在对象化重构以后，10800ticks的模拟耗时从原来的6~7秒上升到了8~9秒，不知是不是我的错觉，总感觉变慢了。
