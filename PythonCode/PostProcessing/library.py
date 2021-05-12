import sys


def get_data(h=9):
    # dataset number [dataset name, #users, #permissions, max#perm-per-user, max#users-have-perm]
    datasets = {1: ['datasets/americas_large.txt', 3485, 101127, 733, 2812],
                2: ['datasets/americas_small.txt', 3477, 1587, 310, 2866],
                3: ['datasets/apj.txt', 2044, 1164, 58, 291],
                4: ['datasets/customer.txt', 10021, 277, 25, 4184],
                5: ['datasets/domino.txt', 79, 231, 209, 52],
                6: ['datasets/emea.txt', 35, 3046, 554, 32],
                7: ['datasets/fire1.txt', 365, 709, 617, 251],
                8: ['datasets/fire2.txt', 325, 590, 590, 298],
                9: ['datasets/hc.txt', 46, 46, 46, 45]
                }

    return datasets[h]


def get_data_opt(h=9):
    if h == 4:
        print('WARNING: the optimal cover for customer dataset is missing - using UPA\'s values')

    # dataset number [dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
    datasets = {1: ['datasets/americas_large.txt', 398, 1, 4, 1, 733],
                2: ['datasets/americas_small.txt', 178, 1, 12, 1, 263],
                3: ['datasets/apj.txt', 453, 1, 8, 1, 52],
                4: ['datasets/customer.txt', 0, 1, 25, 1, 25],  # not optimal solution
                5: ['datasets/domino.txt', 20, 1, 9, 1, 201],
                6: ['datasets/emea.txt', 34, 1, 1, 9, 554],
                7: ['datasets/fire1.txt', 64, 1, 9, 1, 395],
                8: ['datasets/fire2.txt', 10, 1, 3, 2, 307],
                9: ['datasets/hc.txt', 14, 1, 6, 1, 32]
                }

    return datasets[h]


def optimal_solution_structure(h=9):
    if h == 4:
        print('WARNING: the optimal cover for customer dataset is missing')
        return None

    ua = {}  # dictionary (user, set of roles)
    pa = {}  # dictionary (role, set of permissions)
    users = set()
    permissions = set()

    opt_sol = {1: 'converted_exact_covers/americas-large_exact_cover.txt',
               2: 'converted_exact_covers/americas-small_exact_cover.txt',
               3: 'converted_exact_covers/apj_exact_cover.txt',
               4: 'MISSING',
               5: 'converted_exact_covers/domino_exact_cover.txt',
               6: 'converted_exact_covers/emea_exact_cover.txt',
               7: 'converted_exact_covers/fire1_exact_cover.txt',
               8: 'converted_exact_covers/fire2_exact_cover.txt',
               9: 'converted_exact_covers/hc_exact_cover.txt',
               }

    dataset_name = opt_sol[h].strip().split('/')[1].strip().split('_')[0]

    with open(opt_sol[h]) as f:
        line = f.readline()
        if 'Number' in line:
            str, nr = line.split('=')
            nr = int(nr.strip())
            # print('Number of roles:', nr)

        # construct UA and PA
        num_urs_sz_rl = dict()
        rs_u_freq = dict()  # rs_u_freq[i] = j means that there are j users having roles with i permissions
        for line in f:
            if 'Role' in line:
                record = line.strip().split(' ')
                role = int(record[1])
                prms = list(map(int, record[3:]))  # permissions associated to a role
                permissions = permissions | set(prms)
            elif 'Users' in line:
                record = line.strip().split(' ')
                usrs = list(map(int, record[1:]))  # users having role described by prms
                users = users | set(usrs)
            else:
                # rs_u_freq[i] = j means that there are j users having roles with i permissions
                rs_u_freq[len(prms)] = rs_u_freq.get(len(prms), 0) + len(usrs)
                pa[role] = set(prms)
                for u in usrs:
                    if u not in ua:
                        ua[u] = {role}
                    else:
                        ua[u].add(role)
                # print(role, prms, usrs)

    rup_freq = dict()  # rup_freq[i] = j means that there are j users having i roles
    for (uu, rr) in ua.items():
        rup_freq[len(rr)] = rup_freq.get(len(rr), 0) + 1

    rsz_freq = dict()  # rsz_freq[i] = j means that there are j roles having i permissions
    perm_dist = dict()  # perm_dist[p] = j means that permission p belongs to j roles
    for (rr, pp) in pa.items():
        rsz_freq[len(pp)] = rsz_freq.get(len(pp), 0) + 1
        for p in pp:
            perm_dist[p] = perm_dist.get(p, 0) + 1

    pd_freq = dict()  # pd_freq[i] = j means that there are j permissions assigned to i roles
    for p, pd in perm_dist.items():
        pd_freq[pd] = pd_freq.get(pd, 0) + 1

    return dataset_name, rup_freq, rsz_freq, rs_u_freq, pd_freq


decompositions_dir = 'decompositions/'


def save_solution(state, version='rm', output='terminal'):  # output='file' send output to a file
    dataset = state._dataset
    filename = dataset.split('/')[1].split('.')[0] + '_' + version + '.txt'
    # print(dataset)
    print(filename)
    ra = dict()
    for u, roles in state._ua.items():
        for r in roles:
            if r in ra:
                ra[r].add(u)
            else:
                ra[r] = {u}
    if output == 'file':
        stdout = sys.stdout
        sys.stdout = open(decompositions_dir + filename, 'w')  # hard coded!!!

    for r in state._pa.keys():
        print(f'role: {r}')
        permissions = str(sorted(state._pa[r]))[1:-1]
        users = str(sorted(ra[r]))[1:-1]
        print(f'permissions: {permissions}')
        print(f'users: {users}')
        print()

    if output == 'file':
        sys.stdout.close()
        sys.stdout = stdout


def convert_optimal_solution(h=9, output='terminal'):
    if h == 4:
        print('WARNING: the optimal cover for customer dataset is missing')
        return False

    opt_sol = {1: 'converted_exact_covers/americas-large_exact_cover.txt',
               2: 'converted_exact_covers/americas-small_exact_cover.txt',
               3: 'converted_exact_covers/apj_exact_cover.txt',
               4: 'MISSING',
               5: 'converted_exact_covers/domino_exact_cover.txt',
               6: 'converted_exact_covers/emea_exact_cover.txt',
               7: 'converted_exact_covers/fire1_exact_cover.txt',
               8: 'converted_exact_covers/fire2_exact_cover.txt',
               9: 'converted_exact_covers/hc_exact_cover.txt',
               }

    dataset_name = opt_sol[h].strip().split('/')[1].strip().split('_')[0]
    print(dataset_name)
    filename = 'decompositions/' + dataset_name + '_optimal_cover.txt'

    if output == 'file':
        stdout = sys.stdout
        sys.stdout = open(filename, 'w')

    f = open(opt_sol[h], 'r')
    for line in f:
        if 'Role' in line:
            record = line.strip().split(' ')
            role = record[1]
            prms = record[3:]  # permissions associated to a role
            print('role:', role)
            print('permissions:', ', '.join(prms))
        elif 'Users' in line:
            record = line.strip().split(' ')
            usrs = record[1:]  # users having role described by prms
            print('users:', ', '.join(usrs), '\n')
    f.close()

    if output == 'file':
        sys.stdout.close()
        sys.stdout = stdout

    return True


def load_ua_pa(state):  # find where it is used!
    ua = dict()
    pa = dict()
    f = open(state, 'r')
    for line in f:
        if 'role' in line:
            r = int(line.split(':')[1])
            # print('role: ', r)
        elif 'permissions' in line:
            permissions = line.split(':')[1]
            pa[r] = set(map(int, permissions.split(',')))
            # print('permissions: ', pa[r])
        elif 'users' in line:
            users = line.split(':')[1]
            users = set(map(int, users.split(',')))
            # print('users: ', users)

            for u in users:
                if u in ua.keys():
                    ua[u].add(r)
                else:
                    ua[u] = {r}
    f.close()

    return ua, pa


def load_upa(dataset):
    users = set()
    permissions = set()
    upa = {}  # dictionary (user, set of permissions)
    pua = {}  # dictionary (permission, set of users)

    with open(dataset) as f:
        for line in f:
            (user, permission) = line.split()
            user = int(user.strip())
            permission = int(permission.strip())

            if user in users:
                if permission not in upa[user]:
                    upa[user].add(permission)
            else:
                users.add(user)
                upa[user] = {permission}

            if permission in permissions:
                pua[permission].add(user)
            else:
                permissions.add(permission)
                pua[permission] = {user}
        f.closed

    return upa, pua, users, permissions


def check_permissions(upa, pa):
    permissions_upa = set()
    for u, perms in upa.items():
        permissions_upa.update(perms)

    permissions_pa = set()
    for r, perms in pa.items():
        permissions_pa.update(perms)

    return permissions_upa == permissions_pa


def check_users(upa, ua):
    return upa.keys() == ua.keys()


def check_covering(upa, ua, pa):
    for u in upa:
        u_permissions = set()
        for r in ua[u]:
            u_permissions.update(pa[r])

        if u_permissions != upa[u]:
            return False

    return True
