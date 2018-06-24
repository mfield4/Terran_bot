class SCQueue:

    def __init__(self, queue, id_dict):
        self.build_queue = queue
        self.build_ids = id_dict

    def pop_action(self):
        return self.build_queue.pop()

    def get_last_action(self):
        queue_len = len(self.build_queue)

        if queue_len > 0:
            return self.build_queue[queue_len - 1]

        return "NoOp"

    def last_in_obs(self, obs):
        queue_len = len(self.build_queue)

        if queue_len > 0:
            return self.build_ids[self.build_queue[queue_len - 1]] in obs.observation.available_actions
        return False
