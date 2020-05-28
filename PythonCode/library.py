import random
import math


# real world datasets characteristics
def get_data(h=6):
    # dataset number [dataset name, #users, #permissions, max#perm-per-user, max#users-have-perm]
    datasets = {1: ['datasets/fire1.txt', 365, 709, 617, 251],
                2: ['datasets/fire2.txt', 325, 590, 590, 298],
                3: ['datasets/domino.txt', 79, 231, 209, 52],
                4: ['datasets/apj.txt', 2044, 1164, 58, 291],
                5: ['datasets/emea.txt', 35, 3046, 554, 32],
                6: ['datasets/hc.txt', 46, 46, 46, 45],
                7: ['datasets/customer.txt', 10021, 277, 25, 4184],
                8: ['datasets/americas_small.txt', 3477, 1587, 310, 2866],
                9: ['datasets/americas_large.txt', 3485, 101127, 733, 2812]}

    return datasets[h]


# return characteristics of the optimal solution [dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
def get_data_opt(h=6):
    if h == 7:
        print('WARNING: the optimal cover for customer dataset is missing - using UPA\'s values')

    # dataset number [dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
    datasets = {1: ['datasets/fire1.txt', 64, 1, 9, 1, 395],
                2: ['datasets/fire2.txt', 10, 1, 3, 2, 307],
                3: ['datasets/domino.txt',20, 1, 9, 1, 201],
                4: ['datasets/apj.txt',  453, 1, 8, 1,  52],
                5: ['datasets/emea.txt',  34, 1, 1, 9, 554],
                6: ['datasets/hc.txt',    14, 1, 6, 1,  32],
                7: ['datasets/customer.txt', 0, 1, 25, 1, 25], # not optimal solution
                8: ['datasets/americas_small.txt', 178, 1, 12, 1, 263],
                9: ['datasets/americas_large.txt', 398, 1,  4, 1, 733]}

    return datasets[h]


# generate mpr/mru values to test heuristics PRUCC1 and PRUCC2, see the paper for details
def get_test_sets(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='opt'):
    #n_mpr number of values for the mpr parameter
    #n_pru number of values for the mru parameter

    dataset = get_data(h)
    print(dataset)

    #[dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
    dataset_opt = get_data_opt(h)
    print(dataset_opt)

    to_test = dict()
    if u_l == 'opt':
        upper_limit = dataset_opt[5] if fix == 'mpr' else dataset_opt[3]
    else:
        upper_limit = dataset[3]

    upper_limit = upper_limit - 1
    if fix == 'mpr':
        fixed_constraint = n_mpr - 2
        derived_constraint = n_pru - 2
        opt_val = dataset_opt[5]
        der_ul_val = dataset_opt[3] - 1
    else:
        fixed_constraint   = n_pru - 2
        derived_constraint = n_mpr - 2
        opt_val = dataset_opt[3]
        der_ul_val = dataset_opt[5] - 1

    fixed_list = [2]
    if upper_limit > 2:
        for _ in range(fixed_constraint):
            v = fixed_list[-1] + upper_limit // (fixed_constraint + 1)
            if v not in fixed_list:
                fixed_list.append(v)
        if upper_limit not in fixed_list:
            fixed_list.append(upper_limit)

    print(fixed_list, opt_val)

    for t in fixed_list:
        derived_list = [math.ceil(dataset[3] / t)]  # max#P/mpr or max#P/mru
        if t != 1:
            delta = (dataset[3] - derived_list[0]) // (derived_constraint + 1)
            limit = dataset[3] - 1
            for _ in range(derived_constraint):
                tmp_val = derived_list[-1] + delta
                if tmp_val not in derived_list:
                    derived_list.append(tmp_val)
            if limit not in derived_list:
                derived_list.append(limit)
        #print(t, derived_list)

        to_test[t] = derived_list

    return dataset[0], fixed_list, to_test

# another way to generate mpr/mru values to test PRUCC1 and PRUCC2
def compute_test_sets(h=6, n_mpr=3, n_pru=3, fix='mpr'):
    dataset = get_data(h)
    to_test = dict()

    fixed_constraint = n_mpr if fix == 'mpr' else n_pru
    derived_constraint = n_pru if fix == 'mpr' else n_mpr

    fixed_list = [1]
    for _ in range(fixed_constraint):
        fixed_list.append(fixed_list[-1] + dataset[3] // (fixed_constraint + 1))
    fixed_list.append(dataset[3])

    for t in fixed_list:
        derived_list = [math.ceil(dataset[3] / t)]
        if dataset[3] // t != dataset[3]:
            for _ in range(derived_constraint):
                tmp_val = derived_list[-1] + dataset[3] // (derived_constraint + 1)
                if tmp_val not in derived_list:
                    derived_list.append(tmp_val)
            derived_list.append(dataset[3])

        to_test[t] = derived_list

    return dataset[0], fixed_list, to_test


# synthetic roleset
# To specify each role the dataset generator randomly selects up to
# mpr integers in the interval [1, mpr] that are mapped to permissions
# see the paper for details
def generate_roleset(nr, np, mpr):
    permissions = list(range(1, np+1))
    r = 1
    role_set = []
    while r <= nr:
        role_size = random.randint(1,mpr)                   # random size
        role = sorted(set(random.sample(permissions, role_size)))
        if role not in role_set:
            role_set.append(role)
            r += 1

    mapping = dict()
    i = 1 #new permission id
    for role in role_set:
        for p in role:
            if p not in mapping:
                mapping[p] = i
                i += 1

    new_role_set = []
    for role in role_set:
        new_role_set.append(set(map(lambda x: mapping[x], role)))

    return role_set, mapping, new_role_set, list(range(1,i))

# generate synthetic datasets (represented by UA and PA), see the paper for details
def generate_dataset(nr, nu, np, mru, mpr):
    ua = {}  # dictionary (user, set of roles)
    pa = {}  # dictionary (role, set of permissions)
    permissions = list(range(1, np+1))
    roles = list(range(1, nr+1))
    used_roles = set()
    used_permissions = set()
    role_set = []


    # generate random roles
    # print('generate random roles')
    g_role_set, mapping, role_set, used_permissions = generate_roleset(nr, np, mpr)

    r = 1
    for role in role_set:
        pa[r] = role
        r += 1

    # assign roles to users
    # print('assign roles to users')
    for u in range(1, nu+1):
        n_r_u = random.randint(1, mru)
        ua[u] = set(random.sample(roles, n_r_u))
        used_roles.update(ua[u])
        # print(u, ua[u], ' ', len(ua[u]))

    # remove from pa un-used roles
    unused_roles = set(roles).difference(used_roles)
    for u_r in unused_roles:
        del pa[u_r]

    #print('u_r', used_roles, len(used_roles), 'expected:', nr)
    #print('un_r', unused_roles)
    #print('u_p', len(used_permissions), 'expected:', np)
    return ua, pa, used_roles, used_permissions

# save the generated synthetic dataset (save the UPA matrix represented by UA and PA)
def save_dataset(ua, pa, nr, nu, np, mru, mpr, base='synthetic_datasets/'):
    ds_name = str(nr) + '_' + str(nu) + '_' + str(np) + '_' + str(mru) + '_' + str(mpr) + '.txt'
    # print(ds_name)
    upa = open(base + 'upa_' + ds_name, 'w')
    for (u, roles) in ua.items():
        permissions = set()
        for r in roles:
            permissions.update(pa[r])
        for p in sorted(permissions):
            upa.write("{:>6} {:>6}\n".format(u, p))

    roles = open(base + 'roles_' + ds_name, 'w')
    for (r, permissions) in pa.items():
        for p in sorted(permissions):
            roles.write("{:>6} {:>6}\n".format(r, p))

    return ds_name


# compute role-sets similarity
def compute_sim(roles_a, roles_b):
    sim = 0
    for r_a in roles_a.values():
        s = 0
        for r_b in roles_b.values():
            if len(r_a.intersection(r_b)) / (len(r_a.union(r_b))) > s:
                s = len(r_a.intersection(r_b)) / (len(r_a.union(r_b)))

        sim += s
    return sim / len(roles_a)


def compare_solutions(ua_orig, pa_orig, ua_mined, pa_mined):
    if len(ua_orig) != len(ua_mined):
        print('ERROR')
        exit(1)

    for u in ua_orig.keys():
        original_roles = []
        mined_roles = []
        for r in ua_orig[u]:
            original_roles.append(pa_orig[r])
        for r in ua_mined[u]:
            mined_roles.append(pa_mined[r])

        nr = 0
        for r in original_roles:
            if r in mined_roles:
                nr += 1
        print('or:', len(original_roles), 'mr:', len(mined_roles), 'found:', nr)


# compute role-set  accuracy
def disc_roles(orig_roles, mined_roles):
    found_roles = 0
    for r in orig_roles.values():
        if r in mined_roles.values():
            found_roles = found_roles + 1
    return found_roles