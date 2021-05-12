from postprocessing import POST
from copy import deepcopy

class POST_RUCC(POST):
    def __init__(self, state, mru): # state: file containing a UPA decoposition (UA and PA)
        super().__init__(state)
        self._mru = mru

    def _approx_cover(self, permissions, roles):
        working_prms = deepcopy(permissions)
        covering_roles = list()
        while working_prms:
            max_role = -1
            max_role_sz = 0
            for r, role in roles.items():
                if role <= permissions and len(working_prms.intersection(role)) > max_role_sz:
                    max_role_sz = len(working_prms.intersection(role))
                    max_role = r

            covering_roles.append(max_role)
            working_prms = working_prms - roles[max_role]

        return covering_roles

    def mine(self):
        roles = deepcopy(self._orig_pa)
        for u in sorted(self._orig_ua): # for each user
            permissions = deepcopy(self._upa[u])
            cover = self._approx_cover(permissions, roles)

            nr_to_use = len(cover) if len(cover) <= self._mru else self._mru - 1
            roles_to_use = cover[:nr_to_use]

            for r in roles_to_use:
                    self._update_ua_pa({u}, roles[r])
                    permissions = permissions - roles[r]

            if permissions:
                self._update_ua_pa({u}, permissions)
                if permissions not in roles.values():
                    roles[max(roles)+1] = deepcopy(permissions)


class FRUC(POST):
    def __init__(self, state, mru): # state: file containing a decomposition (UA and PA)
        super().__init__(state)
        self._mru = mru
        self._ua = deepcopy(self._orig_ua)
        self._pa = deepcopy(self._orig_pa)
        self._nr = max(self._pa)  # we use max instead of len as there could be "holes" in the role numbering
                                  # this happens when using obmd-based decomposition
        self._ru = dict() # _ru[r] = set of users having role r
        self._violating_usrs = list()  # list of users such that len(self._ua[u]) > self._mru
        self._update_ru()

    def _update_ru(self):
        for r in self._pa:
            self._ru[r] = set()
        for u, roles in self._ua.items():
            for r in roles:
                self._ru[r].add(u)

        self._violating_usrs = [u for u, roles in self._ua.items() if len(roles) > self._mru]

    def _update_ua_pa(self, user, role, used_roles):
        if role not in self._pa.values():
            self._nr += 1
            self._pa[self._nr] = deepcopy(role)
            found = self._nr
        else:
            found = [r for (r, prms) in self._pa.items() if prms == role][0]

        for u in self._ua.keys():
            if used_roles <= self._ua[u]:
                self._ua[u] = self._ua[u] - used_roles
                self._ua[u].add(found)


    def mine(self):
        flag = True
        while len(self._violating_usrs):
            # choose a user in violating_usrs
            u = max(self._violating_usrs, key=lambda x: len(self._ua[x]))
            sorted_roles = sorted([ (r, self._pa[r]) for r in self._ua[u] ], key=lambda t: len(self._ru[ t[0] ]), reverse=True)
            if self._mru > 1:
                roles_to_use = sorted_roles[:-(self._mru - 1)]
            else:
                roles_to_use = sorted_roles

            new_role = set()
            used_roles = set()
            for r, role in roles_to_use:
                new_role = new_role.union(role)
                used_roles.add(r)

            #print('  checking decomposition soundness before update ...', self._cs())
            self._update_ua_pa(u, new_role, used_roles)

            #print('  checking decomposition soundness  after update ...', self._cs(), '\n')

            # if flag and not self._cs():
            #     flag = False
            #     print('            user', u)
            #     print('            role', new_role)
            #     print('    merged roles', dict(roles_to_use).keys())

            self._update_ru()


class RPA(POST):
    def __init__(self, state, mru):
        super().__init__(state)
        self._mru = mru


    def mine(self):
        roles = list(self._orig_pa.values())
        for u in self._orig_ua:
            prms_to_cover = deepcopy(self._upa[u])
            covered_prms = set()
            assigned_roles = 0
            for role in sorted(roles, key=lambda r: len(r), reverse=True):
                if role <= self._upa[u] and not (role <= covered_prms):
                    assigned_roles += 1
                    covered_prms.update(role)
                    prms_to_cover = prms_to_cover - role

                    # assign role to u
                    self._update_ua_pa({u}, role)
                    if assigned_roles == self._mru -1:
                        break
            if prms_to_cover:
                self._update_ua_pa({u}, prms_to_cover)
                if prms_to_cover not in roles:
                    roles.append(prms_to_cover)


class CPA(POST):
    def __init__(self, state, mru):
        super().__init__(state)
        self._mru = mru

    def mine(self):
        roles = list(self._orig_pa.values())
        for u, prms in self._upa.items():
            prms_to_cover = deepcopy(prms)
            covered_prms = set()
            assigned_roles = 0
            while prms_to_cover and assigned_roles < self._mru -1:
                u_roles = list(filter(lambda r:r <= self._upa[u], roles)) # all roles contained in u's permissions
                role = max(u_roles, key=lambda r: len(r.intersection(prms_to_cover)))
                assigned_roles += 1
                covered_prms.update(role)
                prms_to_cover = prms_to_cover - role

                # assign role to u
                self._update_ua_pa({u}, role)

            if prms_to_cover:
                self._update_ua_pa({u}, prms_to_cover)
                if prms_to_cover not in roles:
                    roles.append(prms_to_cover)


if __name__ == '__main__':
    pass
    # starting_state = 'decompositions/apj_obmd.txt'
    #
    # starting_state = 'decompositions/hc_obmd.txt'
    # starting_state = 'decompositions/domino_obmd.txt'
    # state = RPA(starting_state, 12)
    # state.mine()
    # print('RPA', state.get_wsc(), state._cs())
    #
    # starting_state = 'decompositions/hc_fastMin.txt'
    # starting_state = 'decompositions/domino_fastMin.txt'
    # state = CPA(starting_state, 12)
    # state.mine()
    # print('CPA', state.get_wsc(), state._cs())

    # starting_state = 'decompositions/hc_obmd.txt'
    # for i in range(1, 10):
    #     print(f'{i:*^20}')
    #     state = FRUC(starting_state, i)
    #     state.mine()
    #     print('FRUC', state.get_wsc(), state._cs())

