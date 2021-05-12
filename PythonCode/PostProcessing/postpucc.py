from copy import deepcopy
from postprocessing import POST


class POST_PUCC(POST):
    def __init__(self, state, mpr):
        super().__init__(state)
        self._cr = dict()
        self._mpr = mpr

        for r_i, prms_i in self._orig_pa.items():
            for r_j, prms_j in self._orig_pa.items():
                if len(prms_j) <= self._mpr < len(prms_i) and prms_j < prms_j:
                    if r_i in self._cr:
                        self._cr[r_i].add(r_j)
                    else:
                        self._cr[r_i] = {r_j}


    def mine(self):
        for u in self._orig_ua.keys():
            for r in self._orig_ua[u]:
                role = self._orig_pa[r]
                if len(role) <= self._mpr:
                    self._update_ua_pa({u}, role)
                else:
                    tmp_role = deepcopy(role)
                    if r in self._cr:
                        for contained in self._cr[r]:
                            if tmp_role:
                                self._update_ua_pa({u}, contained)
                                tmp_role = tmp_role - contained
                    new_role = set()
                    for p in tmp_role:
                        new_role.add(p)
                        tmp_role = tmp_role - {p}
                        if not tmp_role or len(new_role) == self._mpr:
                            self._update_ua_pa({u}, new_role)
                            new_role = set()
