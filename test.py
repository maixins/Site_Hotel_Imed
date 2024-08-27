from ortools.linear_solver import pywraplp
import itertools
import sqlite3
import sys
from multiprocessing import Pool
import csv

def get_lines(depart):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    D = {}
    c.execute("SELECT code_aeroport_depart, code_aeroport_arrivee FROM lignes")
    for row in c.fetchall():
        if depart == 'Algérie':
            if row[0] in D:
                if row[1] not in D[row[0]]:
                    D[row[0]].append(row[1])
            else:
                D[row[0]] = [row[1]]
        elif depart == 'France':
            if row[1] in D:
                if row[0] not in D[row[1]]:
                    D[row[1]].append(row[0])
            else:
                D[row[1]] = [row[0]]
    conn.close()  # Fermer la connexion après l'utilisation
    return D

lines_fr = get_lines('France')

aeroport_fr = [_ for _ in lines_fr]
aeroport_dz = []
for fr in aeroport_fr:
    for dz in lines_fr[fr]:
        if lines_fr[fr] not in aeroport_dz:
            aeroport_dz.append(dz)

def compute_combinations(i):
    for j in aeroport_fr:
        if j == i:
            continue
        for k in aeroport_fr:
            if k == i or k == j:
                continue
            for l in aeroport_dz:
                for m in aeroport_dz:
                    if l == m:
                        continue
                    for n in aeroport_dz:
                        if n == l or n == m:
                            continue
                        if (l not in lines_fr[i]) and (l not in lines_fr[j]) and (l not in lines_fr[k]):
                            if (m not in lines_fr[i]) and (m not in lines_fr[j]) and (m not in lines_fr[k]):
                                if (n not in lines_fr[i]) and (n not in lines_fr[j]) and (n not in lines_fr[k]):
                                    continue
                        res = ((i,j,k),(l,m,n))
                        with open('combinations.csv', 'a', newline='') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow([str(res)])


def all_combin():
    with Pool() as pool:
        results = pool.map(compute_combinations, aeroport_fr)
    # Aplatir la liste des listes
    return [item for sublist in results for item in sublist]

if __name__ == '__main__':
# Écrire les résultats dans un fichier CSV

    y = all_combin()
    print(len(y))
