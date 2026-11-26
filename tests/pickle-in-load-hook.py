import pickle


class M:
    def set_extra_state(self, state):
        # ruleid: pickle-in-load-hook
        s = pickle.loads(state.numpy().tobytes())

    def _load_from_state_dict(self, sd, *a):
        # ruleid: pickle-in-load-hook
        s = pickle.loads(sd["x"])

    def save(self, obj):
        # ok: pickle-in-load-hook
        return pickle.dumps(obj)

    def helper(self, raw):
        # ok: pickle-in-load-hook
        return pickle.loads(raw)
