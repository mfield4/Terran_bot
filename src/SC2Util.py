import random

from pysc2.lib import features, actions


def select_one_unit_by_type(obs, unit_type):
    """This method wil return an action that sects a unit of the given type. This method will not step orders"""
    my_units = [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]
    if len(my_units):
        unit = random.choice(my_units)
        return [True, actions.FUNCTIONS.select_point("select", (unit[features.FeatureUnit.x], unit[features.FeatureUnit.y]))]

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
