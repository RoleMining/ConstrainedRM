from copy import deepcopy

class POST:
    def __init__(self, state):
        self._upa = {}  # dictionary (user, set of permissions)
        self._permissions = set()
        self._orig_ua = dict()    # original ua
        self._orig_pa = dict()    # original pa
        self._ua = dict()         # post-processed ua
        self._pa = dict()         # post-processed pa
        self._nr = 0              # number of roles
        self._state = state       # starting RBAC state (file containing a representation of UA and PA)
        self._load_ua_pa()
        self._users = set(self._orig_ua.keys())
        self._original_users = deepcopy(self._users)

    def _load_ua_pa(self):
        f = open(self._state, 'r')
        for line in f:
            if 'role' in line:
                r = int(line.split(':')[1])
                # print('role: ', r)
            elif 'permissions' in line:
                permissions = line.split(':')[1]
                permissions = set(map(int, permissions.split(',')))
                self._orig_pa[r] = permissions
                # print('permissions: ', pa[r])
            elif 'users' in line:
                users = line.split(':')[1]
                users = set(map(int, users.split(',')))
                # print('users: ', users)

                for u in users:
                    if u in self._orig_ua.keys():
                        self._orig_ua[u].add(r)
                    else:
                        self._orig_ua[u] = {r}

                    if u in self._upa:
                        self._upa[u].update(permissions)
                    else:
                        self._upa[u] = deepcopy(permissions)
        f.close()

    def _update_ua_pa(self, usrs, role):

        if role not in self._pa.values():
            self._nr += 1
            self._pa[self._nr] = role
            found = self._nr
        else:
            found = [r for (r, prms) in self._pa.items() if prms == role][0]

        '''
        found = 0
        for (r, prms) in self._pa.items():
            if prms == role:
                found = r
                break
        else:
            self._nr += 1
            self._pa[self._nr] = role
            found = self._nr
        '''

        for u in usrs:
            if u in self._ua:
                self._ua[u].add(found)
            else:
                self._ua[u] = {found}

    def _cs(self):
        if len(self._ua) != len(self._original_users):
            #print('Failed #users', '*mined users', len(self._ua), '#orig users', len(self._original_users))
            return False

        flag = True
        for u in self._ua:
            perms = set()
            for r in self._ua[u]:
                perms.update(self._pa[r])
            if perms != self._upa[u]:
                # print('user', u)
                # print('original', self._upa[u])
                # print('assigned', perms)
                # print()
                flag = False, u
                break
                #return False
        return flag

    def check_solution(self):
        if set(self._ua.keys()) != set(self._orig_ua.keys()):
            return False

        for u in self._ua.keys():
            s1 = set()
            s2 = set()
            for r in self._orig_ua[u]:
                s1.update(self._orig_pa[r])
            for r in self._ua[u]:
                s2.update(self._pa[r])

            if s1 != s2:
                return False

        return True

    def _check_soundness_starting_state(self):
        if set(self._orig_ua.keys()) != set(self._upa.keys()):
            return False

        for u in self._orig_ua.keys():
            s = set()
            for r in self._orig_ua[u]:
                s.update(self._orig_pa[r])

            if s != self._upa[u]:
                return False

        return True

    def get_wsc(self):
        nroles = len(self._pa.keys())
        ua_size = 0
        for roles in self._ua.values():
            ua_size += len(roles)
        pa_size = 0
        for prms in self._pa.values():
            pa_size += len(prms)
        return nroles + ua_size + pa_size, nroles, ua_size, pa_size
