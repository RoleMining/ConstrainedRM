from testbed import *
import time

rank_dir = 'rankings/'


def test_heuristic(scenario, dataset, limit):
    nr_all = []
    wsc_all = []
    for decomposition in decomp_no_lr:
        for heuristic in heuristics[scenario]:
            starting_state = base_dir + dataset + decomposition
            if dataset == 'customer' and 'optimal' in decomposition:
                nr, wsc = 1, 1
            else:
                nr, wsc = run(heuristic, starting_state, limit)
            nr_all.append(nr)
            wsc_all.append(wsc)

    return  nr_all, wsc_all


def run(heuristic, starting_state, limit):
    state = heuristic(starting_state, limit)
    name = heuristics_name[state.__class__.__name__]
    state.mine()
    wsc, nr, _, _ = state.get_wsc()
    # print(f'{name:>8} {limit:>3} {wsc:>5} {nr:>4} {state._cs()}', starting_state)
    # print(name, limit, state.get_wsc(), state._cs())
    return nr, wsc


# input: list of (integer) values
# output: list of ranks of the elements in the input list
def rank(values):
    pairs = list(enumerate(values))
    pairs.sort(key=lambda x: x[1])
    # print(values)
    # print(pairs)

    num_elem = len(values)
    pos1 = 0
    pos2 = 0
    r = 0
    to_return = list()
    while pos1 < num_elem:
        r += 1
        pos2 = pos1 + 1
        t_r = r
        while pos2 < num_elem and pairs[pos1][1] == pairs[pos2][1]:
            r += 1
            t_r += r
            pos2 += 1

        num_eq = pos2 - pos1

        for i in range(pos1, pos2):
            to_return.append((pairs[i][0], round(t_r / num_eq, 2)))
        pos1 = pos2

    # print(to_return)
    to_return.sort(key=lambda x: x[0])
    # print(to_return)

    return [p[1] for p in to_return]


def compute_rank(dataset, scenario):
    r_num_roles = dict()
    r_wsc = dict()

    all_r = dict()
    all_w = dict()
    for limit in parameters[scenario][dataset]:
        for decomposition in decomp_no_lr:
            starting_state = base_dir + dataset + decomposition
            r = list()
            w = list()
            l, d = limit, decomp_no_lr.index(decomposition)
            for heuristic in heuristics[scenario]:
                nr, wsc = run(heuristic, starting_state, limit)
                r.append(nr)
                w.append(wsc)
            # print(rank(r), rank(w))
            all_r[(l, d)] = r
            all_w[(l, d)] = w
            r_num_roles[(l, d)] = rank(r)
            r_wsc[(l, d)] = rank(w)

    return r_num_roles, r_wsc, all_r, all_w


def average(r_r, r_w):
    a_r_r_l = dict()  # average #roles rank considering the constraint values
    a_r_r_d = dict()  # average #roles rank considering the decompositions
    a_r_w_l = dict()  # average wsc rank considering the constraint values
    a_r_w_d = dict()  # average wsc rank considering the decompositions

    constraints = set()
    decompositions = set()
    for c, d in r_r.keys():
        num_heuristics = len(r_r[(c, d)])
        constraints.add(c)
        decompositions.add(d)

    for c in constraints:
        a_r_r_l[c] = [0] * num_heuristics
        a_r_w_l[c] = [0] * num_heuristics
        for t in r_r.keys():
            if c == t[0]:
                for h in range(num_heuristics):
                    a_r_r_l[c][h] += r_r[t][h]
                    a_r_w_l[c][h] += r_w[t][h]

    for d in decompositions:
        a_r_r_d[d] = [0] * num_heuristics
        a_r_w_d[d] = [0] * num_heuristics
        for t in r_r.keys():
            if d == t[1]:
                for h in range(num_heuristics):
                    a_r_r_d[d][h] += r_r[t][h]
                    a_r_w_d[d][h] += r_w[t][h]

    # print(constraints)
    # print(decompositions)
    # print(a_r_r_l)
    # print(a_r_w_l)
    # print(a_r_r_d)
    # print(a_r_w_d)

    for l in a_r_r_l.keys():
        a_r_r_l[l] = list(map(lambda x: round(x / len((decompositions)), 2), a_r_r_l[l]))
        a_r_w_l[l] = list(map(lambda x: round(x / len((decompositions)), 2), a_r_w_l[l]))

    for d in a_r_r_d.keys():
        a_r_r_d[d] = list(map(lambda x: round(x / len((constraints)), 2), a_r_r_d[d]))
        a_r_w_d[d] = list(map(lambda x: round(x / len((constraints)), 2), a_r_w_d[d]))

    # print(a_r_r_l)
    # print(a_r_w_l)
    # print(a_r_r_d)
    # print(a_r_w_d)

    return a_r_r_l, a_r_w_l, a_r_r_d, a_r_w_d


def compute_time(scenario, dataset):
    for limit in parameters[scenario][dataset]:
        for decomposition in decomp_no_lr:
            if 'customer' in dataset and 'optimal' in decomposition:
                continue
            starting_state = base_dir + dataset + decomposition
            print(dataset_name[dataset], dec_name_no_lr[decomposition], limit)
            for heuristic in heuristics[scenario]:
                start = time.perf_counter()
                nr, wsc = run(heuristic, starting_state, limit)
                end = time.perf_counter()
                name = heuristics_name[heuristic.__name__]
                t = int((end - start) * 1000)
                print(f'   {name:>10}  {t:>5}')

                # print(dec_name[decomposition], nr, wsc)


if __name__ == '__main__':
    dataset = 'hc'
    scenario = 'postpucc'
    limit = 2

    # compute_time(scenario, dataset)
    # for dataset in datasets:
    #     growing_factor(scenario, dataset, limit)

    # print_table(dataset, scenario)

    #display_all_rankings(dataset, scenario)
    # save_experiment_results(scenario)

    # print( [round(sum(x) / len(a_r_r_d), 2) for x in list(zip(*(list(a_r_r_d.values()))))] )
    # print( [round(sum(x) / len(a_r_w_d), 2) for x in list(zip(*(list(a_r_w_d.values()))))] )
