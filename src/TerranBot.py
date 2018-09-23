from absl import app
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import features, actions, units

import SC2Util as Util
from Orders import Orders
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
_DEFEND = "Defend"
_NO_OP = "NoOp"


class TerranBot(base_agent.BaseAgent):

    # ---------- PySC2 Methods ----------

    def __init__(self):
        super(TerranBot, self).__init__()
        self.base_top_left = False
        self.order_handler = Orders()
        self.order = ""
        self.init_order_list = [_NO_OP,
                                _BUILD_SVC, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT,
                                _BUILD_BUILDING, _BUILD_BUILDING, _BUILD_BUILDING, _BUILD_BUILDING]

        # Need to add building of extractor.
        self.building_queue = SCQueue(['TechLab', 'Refinery', 'Barracks', 'SupplyDepot'],
                                      {'Barracks': actions.FUNCTIONS.Build_Barracks_screen.id,
                                       'SupplyDepot': actions.FUNCTIONS.Build_SupplyDepot_screen.id,
                                       'Refinery': actions.FUNCTIONS.Build_Refinery_screen.id,
                                       'TechLab': actions.FUNCTIONS.Build_TechLab_screen.id})
        self.unit_queue = SCQueue(['TrainMarauder', 'TrainMarine', 'TrainMarine', 'TrainMarine', 'TrainMarine'],
                                  {'TrainMarine': actions.FUNCTIONS.Train_Marine_quick.id,
                                   'TrainMarauder': actions.FUNCTIONS.Train_Marauder_quick.id})
        self.research_queue = SCQueue([], {})

    def step(self, obs):
        super(TerranBot, self).step(obs)
        if self.order_handler.order_done:
            self.update_order(obs)
        return self.do_order(obs)

    # ------------ Order Methods ---------

    def update_order(self, obs):
        if obs.first():
            cmd = Util.get_one_unit_by_type(obs, units.Terran.CommandCenter)
            player_x, player_y = (obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
            if player_y.mean() <= 31:
                print(cmd.y)
                self.base_top_left = True
                self.order_handler.base = True

        if len(self.init_order_list) > 0:
            self.order = self.init_order_list.pop()
            self.order_handler.order_done = False
            self.order_handler.order_step = 0
        else:
            # self.order = random.choice([_BUILD_BUILDING, _BUILD_UNIT, _BUILD_SVC, _NO_OP, _NO_OP, _NO_OP])
            self.order = _NO_OP
            # self.order_done = True
            # self.order_step = 0

    def do_order(self, obs):
        """Each order function will have to deal with updating order_step & order_done"""
        if self.order == _BUILD_BUILDING:
            action = self.order_handler.order_build_building(obs, self.building_queue.get_last_action(), self.building_queue.last_in_obs())
            if self.order_handler.order_done:
                self.building_queue.pop_action()
            return action

        elif self.order == _BUILD_UNIT:
            action = self.order_handler.order_build_unit(obs, self.unit_queue.get_last_action(), self.unit_queue.last_in_obs())
            if self.order_handler.order_done:
                self.unit_queue.pop_action()
            return action

        elif self.order == _BUILD_SVC:
            return self.order_handler.order_build_svc(obs)

        elif self.order == _RESEARCH:
            pass
        elif self.order == _DEFEND:
            pass
        else:  # noop is implicit
            return actions.FUNCTIONS.no_op()

    # ---------- Utility Methods ----------


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
