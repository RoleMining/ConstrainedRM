from prucc import *
from library import *

def compare_prucc(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='#P'):
    #h: chosen dataset
    '''
                    1: firewall 1       6: healthcare
                    2: firewall 2       7: customer
                    3: domino           8: americas small
                    4: apj              9: americas large
                    5: emea
    '''
    #n_mpr: number of mpr values on which to test heuristics PRUCC1 and PRUCC2
    #n_pru: number of mru values on which to test heuristics PRUCC1 and PRUCC2
    #fix:   'mpr' fix the maximum number of permissions per role and compute mru
    #       'mru' fix the maximum number of roles per user and compute mpr
    #u_l:   '#P'  maximum number of permissions per user in UPA
    #       'opt' use the values in the optimal solution dependign on 'fix'
    #SEE THE PAPER FOR DETAILS

    dataset_name, fixed_list, to_test = get_test_sets(h, n_mpr, n_pru, fix, u_l)
    test_bed = [['of', 'upa', 'first'],
                ['or', 'upa', 'random'],
                ['uf', 'uncovered', 'first'],
                ['ur', 'uncovered', 'random']]

    print(dataset_name)
    for v1 in fixed_list:
        for v2 in to_test[v1]:
            if fix == 'mpr':
                mpr = v1
                mru = v2
            else:
                mpr = v2
                mru = v1

            for test in test_bed:
                print('mpr:', mpr, 'mru:', mru)
                istance = PRUCC_1(dataset_name, mpr, mru, test[1], test[2])
                istance.mine()
                wsc, nroles, ua_size, pa_size = istance.get_wsc()
                print('PRUCC1: {:>3} {:6d} {:6d}'.format(test[0], nroles, wsc))

                istance = PRUCC_2(dataset_name, mpr, mru, test[1], test[2])
                istance.mine()
                wsc, nroles, ua_size, pa_size = istance.get_wsc()
                print('PRUCC2: {:>3} {:6d} {:6d}'.format(test[0], nroles, wsc))


def compare_synthetic(nr, nu, np, mru, mpr, runs=5):
    # nr: number of roles to generate
    # nu: number of users
    # np: number of permissions
    # mru: maximum number of roles per user
    # mrp: maximum number of permissions per role
    # runs: number of time heuristics are tested for the given parameters

    base = 'synthetic_datasets/'
    test_bed = [['of', 'upa', 'first'],
                ['or', 'upa', 'random'],
                ['uf', 'uncovered', 'first'],
                ['ur', 'uncovered', 'random']]

    to_return = [runs, nr]

    for test in test_bed:
        tot_roles_1 = tot_wsc_1 = tot_found_1 = tot_sim_1 = 0
        tot_roles_2 = tot_wsc_2 = tot_found_2 = tot_sim_2 = 0

        #print('+'*20)
        for _ in range(runs):
            ua, pa, used_roles, used_permissions = generate_dataset(nr, nu, np, mru, mpr)
            while len(used_roles) != nr:
                print('upa generation failed')
                ua, pa, used_roles, used_permissions = generate_dataset(nr, nu, np, mru, mpr)

            dataset_name = save_dataset(ua, pa, nr, nu, np, mru, mpr)

            istance = PRUCC_1(base + 'upa_' + dataset_name, mpr, mru, test[1], test[2])
            istance.mine()
            wsc = istance.get_wsc()
            found_roles = disc_roles(pa, istance._pa)
            similarity = (compute_sim(pa, istance._pa) + compute_sim(istance._pa, pa))/2
            #print('pr1', test[0], '#roles:', wsc[1], ' wsc:', wsc[0], ' - found roles: ', found_roles)
            tot_roles_1 += wsc[1]
            tot_wsc_1 += wsc[0]
            tot_found_1 += found_roles
            tot_sim_1 += similarity

            istance = PRUCC_2(base + 'upa_' + dataset_name, mpr, mru, test[1], test[2])
            istance.mine()
            istance.mine()
            wsc = istance.get_wsc()
            found_roles = disc_roles(pa, istance._pa)
            similarity = (compute_sim(pa, istance._pa) + compute_sim(istance._pa, pa))/2
            #print('pr2', test[0], '#roles:', wsc[1], ' wsc:', wsc[0], ' - found roles: ', found_roles)
            tot_roles_2 += wsc[1]
            tot_wsc_2 += wsc[0]
            tot_found_2 += found_roles
            tot_sim_2 += similarity


        #print('-'*20)
        to_return.append((test[0], tot_roles_1, tot_wsc_1, tot_found_1, tot_sim_1, tot_roles_2, tot_wsc_2, tot_found_2, tot_sim_2))
        print('pr1', test[0], '#roles:', tot_roles_1//runs, ' wsc:', tot_wsc_1//runs, ' - found roles: ', tot_found_1//runs, '- similariy: ', tot_sim_1/runs)
        print('pr2', test[0], '#roles:', tot_roles_2//runs, ' wsc:', tot_wsc_2//runs, ' - found roles: ', tot_found_2//runs, '- similariy: ', tot_sim_2/runs)


    #return test[0], tot_roles_1, tot_wsc_1, tot_found_1, tot_roles_2, tot_wsc_2, tot_found_2, runs, nr
    #print(to_return)
    return to_return


if __name__ == '__main__':

    # fix nr, nu = 10 * nr, nu/np =  5, mru = nr/10, mru * mpr = 25% np
    # mpr fixed
    test_3_0_0 = [(20, 200, 40, 2, 5),
                  (40, 400, 80, 4, 5),
                  (80, 800, 160, 8, 5),
                  (100, 1000, 200, 10, 5)]

    # fix nr, nu = 10 * nr, nu/np =  5, mru * mpr = 25% np,  mpr = np/10
    # mru fixed
    test_4_0_0 = [(20, 200, 40, 5, 2),
                  (40, 400, 80, 5, 4),
                  (80, 800, 160, 5, 8),
                  (100, 1000, 200, 5, 10)]

compare_prucc()
compare_synthetic(*test_3_0_0[0])