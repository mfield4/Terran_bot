import random

from pysc2.lib import features, actions, units


# --------- Orders ---------

def order_build_building(obs, base, action_id, building: str, step: int):
    """Input: The name of the building to be built, and where to build it.
        select_helper will select the appropriate unit and inc the step.
        build_helper will return the build function. Offsets are hardcoded here"""
    if step == 0:
        return build_building_select_helper(obs, building)

    elif step == 1:
        if action_id in obs.observation.available_actions:
            return build_building_build_helper(obs, building, base)

    return [0, actions.FUNCTIONS.no_op()]


def order_build_unit(obs, step, unit, action_id):
    if step == 0:
        # To find out what building to select.
        if unit in ['TrainMarine', 'TrainMarauder']:  # Select the barracks
            return select_unit_by_type(obs, units.Terran.Barracks)
    elif step == 1:
        if action_id in obs.observation.available_actions:

            if unit == 'TrainMarine':
                return [-1, actions.FUNCTIONS.Train_Marine_quick("now")]
            elif unit == 'TrainMarauder':
                return [-1, actions.FUNCTIONS.Train_Marauder_quick("now")]

    return [0, actions.FUNCTIONS.no_op()]


def order_build_svc(obs, step):
    if step == 0:
        return select_unit_by_type(obs, units.Terran.CommandCenter)

    elif step == 1:
        if actions.FUNCTIONS.Train_SCV_quick.id in obs.observation.available_actions:
            return [-1, actions.FUNCTIONS.Train_SCV_quick("now")]

    return [0, actions.FUNCTIONS.no_op()]


# ---------- Order Helpers --------- Likely for some to be refactored to a utility file later on.


def build_building_build_helper(obs, building, base):
    if building == 'SupplyDepot':
        cmd = get_one_unit_by_type(obs, units.Terran.CommandCenter)
        x, y = transform_offset(base, cmd.x, 10, cmd.y, -15)
        return [-1, actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))]

    elif building == 'Barracks':
        cmd = get_one_unit_by_type(obs, units.Terran.CommandCenter)
        x, y = transform_offset(base, cmd.x, -17, cmd.y, -17)
        return [-1, actions.FUNCTIONS.Build_Barracks_screen("now", (x, y))]

    elif building == 'Refinery':
        geyser = get_one_unit_by_type(obs, units.Neutral.VespeneGeyser)
        return [-1, actions.FUNCTIONS.Build_Refinery_screen("now", (geyser.x, geyser.y))]

    return [1, actions.FUNCTIONS.no_op()]


def build_building_select_helper(obs, building):
    if building in ['SupplyDepot', 'Barracks', 'Refinery']:  # Select svcs
        return select_unit_by_type(obs, units.Terran.SCV)

    elif building in ['TechLab_Barracks', 'Reactor_Barracks']:  # Select the barracks to upgrade.
        return select_unit_by_type(obs, units.Terran.Barracks)

    return [0, actions.FUNCTIONS.no_op()]


def select_unit_by_type(obs, unit_type):
    """This method wil return an action that sects a unit of the given type. This method will not step orders"""
    my_units = [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]
    if len(my_units):
        unit = random.choice(my_units)
        return [True, actions.FUNCTIONS.select_point("select",
                                                     (unit[features.FeatureUnit.x], unit[features.FeatureUnit.y]))]

    return [False, actions.FUNCTIONS.no_op()]


def get_one_unit_by_type(obs, unit_type):
    my_units = [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]
    if len(my_units):
        return random.choice(my_units)
    return None


def get_units_by_type(obs, unit_type):
    return [unit for unit in obs.observation.feature_units
            if unit.unit_type == unit_type]


def unit_type_is_selected(obs, unit_type):
    if (len(obs.observation.single_select) > 0 and
            obs.observation.single_select[0].unit_type == unit_type):
        return True

    if (len(obs.observation.multi_select) > 0 and
            obs.observation.multi_select[0].unit_type == unit_type):
        return True

    return False


def transform_offset(base_top_left, x, x_offset, y, y_offset):
    if base_top_left:
        return [x - x_offset, y - y_offset]

    return [x + x_offset, y + y_offset]
