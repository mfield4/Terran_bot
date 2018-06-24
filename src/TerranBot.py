import random

from absl import app
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import features, actions, units

from SCQueue import SCQueue

_SCREEN_SIZE = 84
_MINIMAP_SIZE = 64

#         num_actions = len(self.action_list)
#         if num_actions > 0:
#             if self.action_list[num_actions - 1] in obs.observation.available_actions:
#                 return self.action_list.pop()

# Orders. Many abstraction justifications I am taking from the 170 project. May want to work on that.
_BUILD_BUILDING = "build_building"
_BUILD_UNIT = "build_unit"
_BUILD_SVC = "build_svc"
_RESEARCH = "research"
_NO_OP = "NoOp"


class TerranBot(base_agent.BaseAgent):

    # ---------- PySC2 Methods ----------

    def __init__(self):
        super(TerranBot, self).__init__()
        self.base_top_left = False
        self.init_order_list = [_NO_OP,
                                _BUILD_SVC, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT,
                                _BUILD_BUILDING, _BUILD_BUILDING, _BUILD_BUILDING]
        self.order = ""
        self.order_step = 0
        self.order_done = True

        # Need to add building of extractor.
        self.building_queue = SCQueue(['TechLab_Barracks', 'Barracks', 'SupplyDepot'],
                                      {'Barracks': actions.FUNCTIONS.Build_Barracks_screen.id,
                                       'SupplyDepot': actions.FUNCTIONS.Build_SupplyDepot_screen.id,
                                       'TechLab_Barracks': actions.FUNCTIONS.Build_TechLab_Barracks_quick.id})
        self.unit_queue = SCQueue(['TrainMarauder', 'TrainMarine', 'TrainMarine', 'TrainMarine', 'TrainMarine'],
                                  {'TrainMarine': actions.FUNCTIONS.Train_Marine_quick.id})
        self.research_queue = SCQueue([], {})

    def step(self, obs):
        super(TerranBot, self).step(obs)
        if self.order_done:
            self.update_order(obs)
        return self.do_order(obs)

    # ------------ Order Methods ---------

    def update_order(self, obs):
        if obs.first():
            cmd = random.choice(self.get_units_by_type(obs, units.Terran.CommandCenter))
            player_x, player_y = (
                    obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
            meanx, meany = player_x.mean(), player_y.mean()
            if player_y.mean() <= 31:
                print(cmd[features.FeatureUnit.y])
                self.base_top_left = True

        if len(self.init_order_list) > 0:
            self.order = self.init_order_list.pop()
            self.order_done = False
            self.order_step = 0
        else:
            # self.order = random.choice([_BUILD_BUILDING, _BUILD_UNIT, _BUILD_SVC, _NO_OP, _NO_OP, _NO_OP])
            self.order = _NO_OP
            self.order_done = True
            self.order_step = 0

    def do_order(self, obs):
        """Each order function will have to deal with updating order_step & order_done"""
        if self.order == _BUILD_BUILDING:
            return self.order_build_building(obs)

        elif self.order == _BUILD_UNIT:
            return self.order_build_unit(obs)

        elif self.order == _BUILD_SVC:
            return self.order_build_svc(obs)

        elif self.order == _RESEARCH:
            return self.order_research(obs)

        else:  # noop is implicit
            return actions.FUNCTIONS.no_op()

    def order_build_building(self, obs):
        if self.order_step == 0:
            building = self.building_queue.get_last_action()

            if building in ['SupplyDepot', 'Barracks']:  # Select svcs
                ok, select_svc_action = self.select_unit__by_type(obs, units.Terran.SCV)
                if ok:
                    self.order_step += 1
                    return select_svc_action

            elif building in ['TechLab_Barracks', 'Reactor_Barracks']:  # Select the barracks to upgrade.
                ok, select_bck_action = self.select_unit__by_type(obs, units.Terran.Barracks)
                if ok:
                    self.order_step += 1
                    return select_bck_action

            return actions.FUNCTIONS.no_op()
        # Build SupplyDepot, Barracks, etc.
        if self.order_step == 1 and self.unit_type_is_selected(obs, units.Terran.SCV):
            if self.building_queue.last_in_obs(obs):
                self.order_step = 0
                self.order_done = True
                building = self.building_queue.pop_action()
                command = self.get_units_by_type(obs, units.Terran.CommandCenter)

                if len(command) > 0:
                    cmd = random.choice(command)
                    cmdx, cmdy = cmd[features.FeatureUnit.x], cmd[features.FeatureUnit.y]
                    print(cmdx, cmdy, cmd[0], cmd[1])
                    if building == 'SupplyDepot':
                        x, y = self.transform_offset(cmdx, 10, cmdy, -15)
                        return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))

                    elif building == 'Barracks':
                        x, y = self.transform_offset(cmdx, -15, cmdy, -15)
                        return actions.FUNCTIONS.Build_Barracks_screen("now", (x, y))
        # Build TechLabs, Reactors, etc.
        elif self.order_step == 1 and self.unit_type_is_selected(obs, units.Terran.Barracks):
            if self.building_queue.last_in_obs(obs):
                self.order_step = 0
                self.order_done = True
                return actions.FUNCTIONS.Build_Techlab_Barrack_quick("now")

        return actions.FUNCTIONS.no_op()

    def order_build_unit(self, obs):
        if self.order_step == 0:
            # To find out what building to select.
            unit_order = self.unit_queue.get_last_action()

            if unit_order in ['TrainMarine', 'TrainMarauder']:  # Select the barracks
                ok, action = self.select_unit__by_type(obs, units.Terran.Barracks)
                if ok:
                    self.order_step += 1
                    return action
        elif self.order_step == 1:
            if self.unit_queue.last_in_obs(obs):
                unit_order = self.unit_queue.pop_action()
                self.order_step = 0
                self.order_done = True

                if unit_order == 'TrainMarine':
                    return actions.FUNCTIONS.Train_Marine_quick("now")
                elif unit_order == 'TrainMarauder':
                    return actions.FUNCTIONS.Train_Marauder_quick("now")

            elif not self.unit_type_is_selected(obs, units.Terran.Barracks):
                self.order_step = 0

        return actions.FUNCTIONS.no_op()

    def order_build_svc(self, obs):
        if self.order_step == 0:
            ok, cmd_select_action = self.select_unit__by_type(obs, units.Terran.CommandCenter)
            if ok:
                self.order_step += 1
                return cmd_select_action

        elif self.order_step == 1:
            if actions.FUNCTIONS.Train_SCV_quick.id in obs.observation.available_actions:
                self.order_step = 0
                self.order_done = True
                return actions.FUNCTIONS.Train_SCV_quick("now")

            self.order_done = True
        return actions.FUNCTIONS.no_op()

    def order_research(self, obs):
        if self.order_step == 0:
            pass
        return actions.FUNCTIONS.no_op()

    # ---------- Utility Methods ----------

    def select_unit__by_type(self, obs, unit_type):
        """This method wil return an action that sects a unit of the given type. This method will not step orders"""
        the_units = self.get_units_by_type(obs, unit_type)
        if len(the_units) > 0:
            unit = random.choice(the_units)
            return [True, actions.FUNCTIONS.select_point("select_all_type",
                                                         (unit[features.FeatureUnit.x], unit[features.FeatureUnit.y]))]

        return [False, actions.FUNCTIONS.no_op()]

    def transform_offset(self, x, x_offset, y, y_offset):
        if self.base_top_left:
            return [x - x_offset, y - y_offset]

        return [x + x_offset, y + y_offset]

    @staticmethod
    def get_units_by_type(obs, unit_type):
        return [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]

    @staticmethod
    def unit_type_is_selected(obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
                obs.observation.single_select[0].unit_type == unit_type):
            return True

        if (len(obs.observation.multi_select) > 0 and
                obs.observation.multi_select[0].unit_type == unit_type):
            return True

        return False


def main(argv):
    agent = TerranBot()

    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="Simple128",
                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Bot(sc2_env.Race.zerg, sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                        feature_dimensions=features.Dimensions(screen=_SCREEN_SIZE, minimap=_MINIMAP_SIZE),
                        use_feature_units=True),
                    step_mul=16,  # 150 apm, default 8 @ 300 apm.
                    game_steps_per_episode=0,  # however long needed.
                    visualize=True) as env:

                agent.setup(env.observation_spec(), env.action_spec())
                steps = env.reset()
                while True:
                    step_actions = [agent.step(steps[0])]

                    if steps[0].last():
                        break
                    steps = env.step(step_actions)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)
