from absl import app
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import features, actions, units

import Orders as Order
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
                                # _BUILD_SVC, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT, _BUILD_UNIT,
                                _BUILD_BUILDING, _BUILD_BUILDING, _BUILD_BUILDING]
        self.order = ""
        self.order_step = 0
        self.order_done = True

        # Need to add building of extractor.
        self.building_queue = SCQueue(['TechLab_Barracks', 'Refinery', 'Barracks', 'SupplyDepot'],
                                      {'Barracks': actions.FUNCTIONS.Build_Barracks_screen.id,
                                       'SupplyDepot': actions.FUNCTIONS.Build_SupplyDepot_screen.id,
                                       'Refinery': actions.FUNCTIONS.Build_Refinery_screen.id,
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
            cmd = Order.get_one_unit_by_type(obs, units.Terran.CommandCenter)
            player_x, player_y = (obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
            if player_y.mean() <= 31:
                print(cmd.y)
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
            step, action = Order.order_build_building(obs, self.base_top_left, self.building_queue.last_in_obs(), self.building_queue.get_last_action(), self.order_step)
            return self.update_order_step(action, step)

        elif self.order == _BUILD_UNIT:
            step, action = Order.order_build_unit(obs, self.order_step, self.unit_queue.get_last_action(), self.unit_queue.last_in_obs())
            return self.update_order_step(action, step)

        elif self.order == _BUILD_SVC:
            step, action = Order.order_build_svc(obs, self.order_step)
            return self.update_order_step(action, step)

        elif self.order == _RESEARCH:
            step, action = Order.order_research()
            return self.update_order_step(action, step)

        else:  # noop is implicit
            return actions.FUNCTIONS.no_op()

    # ---------- Utility Methods ----------

    def update_order_step(self, action, step):
        if step == -1:
            self.order_done = True
            self.order_step = 0
            self.building_queue.pop_action()
        else:
            self.order_step = int(step)
        return action


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
