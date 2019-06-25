import random
from copy import deepcopy

#Base class
class Mining:
    def __init__(self, dataset):
        self._dataset = dataset
        self._users = set()
        self._permissions = set()
        self._upa = {}  # dictionary (user, set of permissions)
        self._pua = {}  # dictionary (permission, set of users)
        self._ua = {}   # dictionary (user, set of roles)
        self._pa = {}   # dictionary (role, set of permissions)
        self._k = 0     # mined roles so far
        self._n = 0     # total number of granted access to resources (i.e., number of pairs in dataset)
        self._load_upa()
        self._unc_upa = deepcopy(self._upa)
        self._unc_pua = deepcopy(self._pua)
        self._unc_users = deepcopy(self._users)
        self._unc_permissions = deepcopy(self._permissions)

    #initialize UPA matrix according to the dataset 'self._dataset'
    def _load_upa(self):
        with open(self._dataset) as f:
            for u_p in f:
                (user, permission) = u_p.split()
                user = int(user.strip())
                permission = int(permission.strip())

                if user in self._users:
                    if permission not in self._upa[user]:
                        self._upa[user].add(permission)
                        self._n = self._n + 1
                else:
                    self._users.add(user)
                    self._upa[user] = {permission}
                    self._n = self._n + 1

                if permission in self._permissions:
                    self._pua[permission].add(user)
                else:
                    self._permissions.add(permission)
                    self._pua[permission] = {user}
            f.closed

    #used by the mining algorithms, update ua and pa matrices assinging permissions 'prms' to users 'usrs'
    def _update_ua_pa(self, usrs, prms):
        idx_f = 0
        found = False
        for (idx, r) in self._pa.items():
            if r == prms:
                idx_f = idx
                found = True
                break

        if found == False:
            self._k = self._k + 1
            self._pa[self._k] = prms
            idx_f = self._k

        for u in usrs:
            if u in self._ua:
                self._ua[u].add(idx_f)
            else:
                self._ua[u] = {idx_f}

    #after a role has been assigned, look for users and permissions not coverd yet
    def _update_unc(self, usrs, prms):
        for u in usrs:
            self._unc_upa[u] = self._unc_upa[u] - prms
            if len(self._unc_upa[u]) == 0:
                self._unc_users.remove(u)
        for p in prms:
            self._unc_pua[p] = self._unc_pua[p] - usrs
            if len(self._unc_pua[p]) == 0:
                self._unc_permissions.remove(p)


    # return weighed structural complexity of the mined roles and |Roles|, |UA|, and |PA|
    def get_wsc(self):
        nroles = len(self._pa.keys())
        ua_size = 0
        for roles in self._ua.values():
            ua_size += len(roles)
        pa_size = 0
        for prms in self._pa.values():
            pa_size += len(prms)
        return nroles + ua_size + pa_size, nroles, ua_size, pa_size


    def _check_solution(self):
        for u in self._users:
            if u not in self._ua.keys():
                return False
            perms = set()
            for r in self._ua[u]:
                perms.update(self._pa[r])
            if perms != self._upa[u]:
                return False
        return True


    def print_roles(self):
        sr = sorted(self._pa.items(), key = lambda role : len(role[1]))
        for r in sr:
            print(r)


# Permission-Role Usage Cardinality Constraint - Base class
class PRUCC(Mining):
    def __init__(self, dataset, mpr = 0, mru = 0, access_matrix = 'upa', criterion = 'first'):
        # dataset = real-world dataset's filename
        # mpr = maximum # of permissions per role, mru = maximum roles per user
        # mpr/mru = 0 => no mpr/mru constraint
        # access_matrix = 'upa' => use original user-permission association matrix
        # access_matrix != 'upa' => use the matrix of the original UPA's entries left uncovered
        # criterion = 'first' => select the first mpr permissions from the picked UPA's row
        # criterion != 'first' => select mpr random permissions from the picked UPA's row

        super().__init__(dataset)
        self._mpr = len(self._permissions) if mpr == 0 else mpr
        self._mru = len(self._permissions) if mru == 0 else mru

        # use the original UPA or the entries left uncovered in UPA
        self._matrix = self._upa if access_matrix == 'upa' else self._unc_upa

        # select the first mpr (i.e., mpr) permissions or mpr random ones
        self._selection = self._first if criterion == 'first' else self._random

        if self._incompatible():
            exit('ERROR: UPA is incompatible with contraints mpr: {0} mru: {1}'.format(self._mpr, self._mru))

    def _first(self, prms):
        return prms if len(prms) <= self._mpr else set(list(prms)[0:self._mpr])

    def _random(self, prms):
        return prms if len(prms) <= self._mpr else set(random.sample(prms, self._mpr))

    #check whether the constraints mpr and mru are compatible with the UPA matrix
    def _incompatible(self):
        for u in self._upa.keys():
            if self._mpr * self._mru < len(self._upa[u]):
                print(self._mpr, self._mru, len(self._upa[u]))
                return True
        return False

    def mine(self):
        prms = {'dummy'}
        while len(self._unc_users) > 0 and prms:
            usrs, prms = self._pick_role()
            if usrs:
                self._update_ua_pa(usrs, prms)
                self._update_unc(usrs, prms)

        self._fix()

    def _fix(self):
        for u in self._users:
            if len(self._ua[u]) > self._mru or len(self._unc_upa[u]):
                self._ua[u] = set()
                tmp_u = deepcopy(self._upa[u])
                for r in self._pa.keys():
                    if len(self._pa[r]) == self._mpr and self._pa[r].issubset(tmp_u):
                        self._ua[u].add(r)
                        tmp_u = tmp_u.difference(self._pa[r])
                while len(tmp_u) > self._mpr:
                    prms = self._selection(tmp_u)
                    self._update_ua_pa({u}, prms)
                    tmp_u = tmp_u.difference(prms)

                if len(tmp_u):
                    self._update_ua_pa({u}, tmp_u)

        #we need to remove all roles in _pa that are not assigned to any user
        id_roles = set(self._pa.keys())
        assigned_roles = set()
        for u in self._users:
            assigned_roles.update(self._ua[u])
        if len(id_roles) != len(assigned_roles):  # one or more roles are not needed (they are not assigned to any user)
            to_delete = id_roles.difference(assigned_roles)
            for r in to_delete:
                del self._pa[r]

    #used for debug
    def _check_constraints(self):
        mru_v = mpr_v = False
        for u in self._ua.keys():
            if len(self._ua[u]) > self._mru:
                mru_v = True
        for r in self._pa.keys():
            if len(self._pa[r]) > self._mpr:
                mpr_v = True
        if mru_v:
            print('mru violation', end=' ')
        if mru_v:
            print('mpr violation')

    def _pick_role(self):
        pass


# First heuristic
class PRUCC_1(PRUCC):
    def _pick_role(self):
        u = self._min_uncovered()
        usrs = {u}
        prms = self._selection(self._unc_upa[u])
        # look for other users having permissions prms
        for u in self._unc_users:
            if prms.issubset(self._upa[u]):
                usrs.add(u)
        return usrs, prms

    def _min_uncovered(self):
        m = float('inf')
        min_usrs = {}  # users with minimum uncovered permissions
        last = []
        for u in self._unc_users:
            if 0 < len(self._matrix[u]) < m:
                m = len(self._matrix[u])
                min_usrs = {u}
                last = [u]
            if len(self._matrix[u]) == m:
                min_usrs.add(u)
                last = [u]

        u = random.sample(min_usrs, 1) # u is a list, we need the user, hence u[0]
        return u[0]  #min_usrs[-1], last user found, non-deterministic choice


# Second heuristic
class PRUCC_2(PRUCC):
    def _pick_role(self):
        u = self._min_uncovered()
        if u:
            usrs = {u}
            prms = self._selection(self._unc_upa[u])
            # look for other users having permissions prms
            for u in self._unc_users:
                if prms <= self._upa[u] and (u not in self._ua or len(self._ua[u]) < self._mru):
                    usrs.add(u)
        else:
            usrs = prms = {}

        return usrs, prms

    def _min_uncovered(self):
        m = float('inf')
        min_usrs = {}  # users with minimum uncovered permissions
        last = []
        for u in self._unc_users:
            if (u not in self._ua) or (u in self._ua and len(self._ua[u]) < self._mru):
                if 0 < len(self._matrix[u]) < m:
                    m = len(self._matrix[u])
                    min_usrs = {u}
                    last = [u]
                if len(self._matrix[u]) == m:
                    min_usrs.add(u)
                    last = [u]
        if min_usrs:
            u = random.sample(min_usrs, 1)  # u is a list, we need the user, hence u[0]
            return u[0]  #min_usrs[-1], last user found, non-deterministic choice
        else:
            return 0

