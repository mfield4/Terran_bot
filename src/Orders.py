from pysc2.lib import actions, units

import SC2Util as Util


# --------- Orders ---------

class Orders:
    def __init__(self):
        self.base = False
        self.order_step = 0
        self.order_done = True

    def update_order_step(self, action, step):
        if step == -1:
            self.order_done = True
            self.order_step = 0
        else:
            self.order_step = int(step)
        return action

    def order_build_building(self, obs, building, action_id):
        """Input: The name of the building to be built, and where to build it.
            select_helper will select the appropriate unit and inc the step.
            build_helper will return the build function. Offsets are hardcoded here"""
        step, action = 0, actions.FUNCTIONS.no_op()
        if self.order_step == 0:
            step, action = build_building_select_helper(obs, building)

        elif self.order_step == 1:
            # print(obs.observation.available_actions)
            if action_id in obs.observation.available_actions:
                step, action = build_building_build_helper(obs, self.base, building)

        return self.update_order_step(action, step)

    def order_build_unit(self, obs, unit, action_id):
        step, action = 0, actions.FUNCTIONS.no_op()
        if self.order_step == 0:
            # To find out what building to select.
            if unit in ['TrainMarine', 'TrainMarauder']:  # Select the barracks
                step, action = Util.select_one_unit_by_type(obs, units.Terran.Barracks)

        elif self.order_step == 1:
            if action_id in obs.observation.available_actions:

                if unit == 'TrainMarine':
                    step, action = [-1, actions.FUNCTIONS.Train_Marine_quick("now")]
                elif unit == 'TrainMarauder':
                    step, action = [-1, actions.FUNCTIONS.Train_Marauder_quick("now")]

        return self.update_order_step(action, step)

    def order_build_svc(self, obs):
        step, action = 0, actions.FUNCTIONS.no_op()
        if self.order_step == 0:
            step, action = Util.select_one_unit_by_type(obs, units.Terran.CommandCenter)

        elif self.order_step == 1:
            if actions.FUNCTIONS.Train_SCV_quick.id in obs.observation.available_actions:
                step, action = [-1, actions.FUNCTIONS.Train_SCV_quick("now")]
        return self.update_order_step(action, step)


# ---------- Order Helpers --------- Likely for some to be refactored to a utility file later on.

def build_building_select_helper(obs, building):
    if building in ['SupplyDepot', 'Barracks', 'Refinery']:  # Select svcs
        return Util.select_one_unit_by_type(obs, units.Terran.SCV)

    elif building in ['TechLab', 'Reactor']:  # Select the barracks to upgrade.
        return Util.select_one_unit_by_type(obs, units.Terran.Barracks)

    return [0, actions.FUNCTIONS.no_op()]


def build_building_build_helper(obs, base, building):
    if building == 'SupplyDepot':
        cmd = Util.get_one_unit_by_type(obs, units.Terran.CommandCenter)
        x, y = Util.transform_offset(base, cmd.x, 10, cmd.y, -15)
        return [-1, actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))]
    elif building == 'Barracks':
        cmd = Util.get_one_unit_by_type(obs, units.Terran.CommandCenter)
        x, y = Util.transform_offset(base, cmd.x, -17, cmd.y, -17)
        return [-1, actions.FUNCTIONS.Build_Barracks_screen("now", (x, y))]
    elif building == 'Refinery':
        geyser = Util.get_one_unit_by_type(obs, units.Neutral.VespeneGeyser)
        return [-1, actions.FUNCTIONS.Build_Refinery_screen("now", (geyser.x, geyser.y))]
    elif building == 'TechLab':
        bcks = Util.get_one_unit_by_type(obs, units.Terran.Barracks)
        return [-1, actions.FUNCTIONS.Build_TechLab_screen("now", (bcks.x, bcks.y))]
    elif building == 'Reactor':
        return [-1, actions.FUNCTIONS.Build_Reactor_screen("now")]

    return [0, actions.FUNCTIONS.no_op()]

# ----------- Utility Functions ---------
