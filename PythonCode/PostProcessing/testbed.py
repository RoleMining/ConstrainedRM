from postpucc import POST_PUCC
from postrucc import POST_RUCC, FRUC, RPA, CPA
from library import load_ua_pa

datasets = ['americas_large',
            'americas_small',
            'apj',
            'customer',
            'domino',
            'emea',
            'fire1',
            'fire2',
            'hc']

dataset_name = dict(map(lambda d: (d, ' '.join(d.split('_')).title()), datasets))
dataset_name['hc'] = 'Healthcare'
dataset_name['fire1'] = 'Firewall 1'
dataset_name['fire2'] = 'Firewall 2'


base_dir = 'decompositions/'

decompositions = ['_optimal_cover.txt',
                  '_org_row.txt',
                  '_unc_row.txt',
                  '_org_col.txt',
                  '_unc_col.txt',
                  '_fastMin.txt',
                  '_obmd.txt',
                  '_biclique.txt']

decomp_no_lr = ['_optimal_cover.txt',
                  '_org_row.txt',
                  '_unc_row.txt',
                  '_org_col.txt',
                  '_unc_col.txt',
                  '_fastMin.txt',
                  '_obmd.txt',
                  '_biclique.txt']

dec_name = {'_optimal_cover.txt':'Optimal',
                  '_org_row.txt':'RM1',
                  '_unc_row.txt':'RM2',
                  '_org_col.txt':'RM3',
                  '_unc_col.txt':'RM4',
                  '_fastMin.txt':'FastMiner',
                  '_obmd.txt':'OBMD',
                  '_biclique.txt':'Biclique'}


dec_name_no_lr = {n:dec_name[n] for n in decomp_no_lr}

# consder mpr = 10%, 30%, 50%, 80%, 100% of max permissions per role of the optimal solution
post_pucc_opt_parm = \
    {'americas_large':(73, 220, 367, 586, 733),
     'americas_small':(26, 79, 132, 210, 263),
     'apj':(5, 16, 26, 42, 52),
     'customer':(3, 8, 13, 20, 25),
     'domino':(20, 60, 101, 161, 201),
     'emea':(55, 166, 277, 443, 554),
     'fire1':(40, 119, 198, 316, 395),
     'fire2':(31, 92, 154, 246, 307),
     'hc':(3, 10, 16, 26, 32)
     }

# For each dataset, considering the optimal solution for the uncostrained case,
# the first value is the minimum number of roles (excluding 1) assigned to a user
# the last but one value is the maximum number of roles assigned to a user
# the last value is 20% bigger than the last but one
# For each dataset we consider at most five (equally spaced) values
post_rucc_opt_parm = \
    {'americas_large':(2, 3, 4, 5),
     'americas_small':(2, 6, 10, 12, 14),
     'apj':(2, 4, 6, 8, 10),
     'customer':(2, 4, 6, 8, 10),
     'domino':(2, 4, 7, 9, 11),
     'emea':(1, 2, 3, 4, 5),   # the optimal unconstrained solution distributes one role to each user
     'fire1':(2, 4, 7, 9, 11),
     'fire2':(2, 3, 4),
     'hc':(2, 4, 6, 7)
     }


scenarios = ('postpucc', 'postrucc', 'postpdcc')

heuristics = {'postpucc':(POST_PUCC,),
               'postrucc':(POST_RUCC, FRUC, CPA, RPA),
              }

parameters = {'postpucc':post_pucc_opt_parm,
              'postrucc':post_rucc_opt_parm,
              }

heuristics_name = {'FIXPDC':'FixPDC',
                   'POST_PDCC':'postPDCC',
                   'POST_PUCC':'postPUCC',
                   'POST_RUCC': 'postRUCC',
                   'FRUC': 'FixRUC',
                   'CPA':'CPA',
                   'RPA':'RPA'}


def decompostition_measures():
    for dataset in datasets:
        print(f'{dataset_name[dataset]:>16} & ', end=' ')
        r = ''
        w = ' '*16
        for decomposition in decomp_no_lr:
            filename = base_dir + dataset + decomposition
            if 'customer' in dataset and 'optimal' in decomposition:
                continue
            ua, pa = load_ua_pa(filename)
            nroles = len(pa.keys())
            ua_size = 0
            for roles in ua.values():
                ua_size += len(roles)
            pa_size = 0
            for prms in pa.values():
                pa_size += len(prms)
            r += f'{nroles:>10} & '
            w += f'{nroles + ua_size + pa_size:>10} & '

        print(r)
        print(w)

if __name__ == '__main__':
    decompostition_measures()