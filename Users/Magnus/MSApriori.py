import itertools
import re
from sys import argv

print('Computing frequent item sets.')
transaction_file = 'transaction.txt'
parameter_file = 'mis.txt'
output_file = 'msa_output.txt'


def fileParser(transaction_file, parameter_file):
    T = []
    with open(transaction_file, 'r') as trans:
        for row in trans:
            transarr = re.findall(r'{.*?}', row)
            T.extend([map(str, list(eval(innerrow))) for innerrow in transarr])

    with open(parameter_file, 'r') as param:
        data = [row for row in param]

    MS = dict()
    cannot_be_together = list()
    must_have = list()
    for index, d in enumerate(data):
        if d[0] == 'M':
            match = re.match(r'^.*\((.*)\).*= (\d*\.\d*)', d)
            MS[match.group(1)] = float(match.group(2))
        elif d[0] == 'S':
            max_sup_diff = float(re.match(r'.*= (.*)', d).group(1))
        elif d[0] == 'm':
            must_have = [x.strip() for x in d.split(':')[1].split('or')]
        elif d[0] == 'c':
            cannot_be_together = [map(str, list(eval(x))) for x in re.findall(r'{.*?}', d)]

    return T, MS, max_sup_diff, cannot_be_together, must_have



def init_pass(M, T):
    L = list()
    for t in T:
        for i in t:
            sup_count[i] = sup_count.get(i, 0) + 1
    smallest_sup = None
    for m in M:
        if smallest_sup:
            if m in sup_count and sup_count[m] / n >= smallest_sup:
                L.append(m)
        elif m in sup_count and sup_count[m] / n >= MS[m]:
            L.append(m)
            smallest_sup = MS[m]
    return L


def level2_candidate_gen(L):
    c = list()
    for i, l in enumerate(L):
        if sup_count[l] / n >= MS[l]:
            for j in range(i + 1, len(L)):
                if sup_count[L[j]] / n > MS[l] and abs(sup_count[L[j]] / n - sup_count[l] / n) <= max_sup_diff:
                    c.append({'c': [l, L[j]], 'count': 0})
    return c


def MScandidate_gen(F, k):
    c = list()
    for index, f1 in enumerate(F):
        for j, f2 in enumerate(F[index + 1:]):
            if set(f1[:-1]) == set(f2[:-1]) and abs(sup_count[f2[k - 2]] / n - sup_count[
                f1[k - 2]] / n) <= max_sup_diff:  # MS[f2[k-2]] > MS[f1[k-2]]) required?
                candidate = list(f1)
                candidate.append(f2[k - 2])
                delete = False
                for s in list(itertools.combinations(candidate, k - 1)):
                    if candidate[0] in s or MS[candidate[0]] == MS[candidate[1]]:
                        if list(s) not in F:
                            delete = True
                if not delete:
                    c.append({'c': candidate, 'count': 0})
    return c


def apply_constraints(F, must_have, cannot_be_together):
    F1 = dict()
    for k in F:
        F1[k] = list()
        for f in F[k]:
            delete = False
            if set(f).intersection(set(must_have)):
                for c in cannot_be_together:
                    if set(c).issubset(set(f)):
                        delete = True
                        break
                if not delete:
                    F1[k].append(f)
    return F1


def print_in_format(F):
    out_file = open(output_file, 'w')
    for k in F:
        out_file.write('Frequent ' + str(k) + '-itemsets\n')
        for f in F[k]:
            if k == 1:
                out_file.write('\n    ' + str(sup_count[f[0]]) + ' : {' + ','.join(set(f)) + '}')
            else:
                tail_count = 0
                for c in C[k]:
                    if set(c['c']) == set(f):
                        count = c['count']
                if k == 2:
                    tail_count = sup_count[f[k - 1]]
                else:
                    for c in C[k - 1]:
                        if set(c['c']) == set(f[1:]):
                            tail_count = c['count']
                out_file.write("\n    " + str(count) + " : " + '{' + ', '.join(f) + '}')
                out_file.write("\nTailcount = " + str(tail_count))
        out_file.write("\n\n    Total number of frequent " + str(k) + "-itemsets = " + str(len(F[k])) + "\n\n\n")


T, MS, max_sup_diff, cannot_be_together, must_have = fileParser(transaction_file, parameter_file)
n = float(len(T))
F = {}
sup_count = {}
C = {}
M = []

for item, mis in sorted(MS.items(), key=lambda x: (x[1], int(x[0]))):
    M.append(item)

L = init_pass(M, T)
if L:
    F[1] = [[L[0]]]
else:
    out_file = open(output_file, 'w')
    out_file.write("No frequent items found")
    print("Please find output in " + output_file)
    exit()

for l in L[1:]:
    if sup_count[l] / n >= MS[l]:
        F[1].append([l])

for k in range(2, 15):
    if k == 2:
        C[k] = level2_candidate_gen(L)
    else:
        C[k] = MScandidate_gen(F[k - 1], k)

    for c in C[k]:
        sub_found = False
        sub_count = True
        if k > 2:
            for c1 in C[k - 1]:
                if set(c['c'][1:]) == set(c1['c']):
                    sub_found == True
                    if c1['count'] != 0:
                        sub_count = False
            if sub_count and not sub_found:
                C[k - 1].append({'c': c['c'][1:], 'count': 0})
        for t in T:
            if set(c['c']).issubset(t):
                c['count'] += 1
            if k > 2 and sub_count:
                if set(c['c'][1:]).issubset(t):
                    C[k - 1][-1]['count'] += 1
    if not C[k]:
        break

    F[k] = []
    for c in C[k]:
        if c['count'] / n >= MS[c['c'][0]]:
            F[k].append(c['c'])

    if len(F[k]) < 2:
        break

F1 = apply_constraints(F, must_have, cannot_be_together)
print_in_format(F1)
print("Please find output in " + output_file)
