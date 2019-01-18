
def Similarity(ind1, ind2):
    c = 0
    t = len(ind1)
    for i in range(t):
        
        if ind1[i] == ind2[i]:
            c += 1
    return t - c == 0

def retiraRepetido(pop):
    qt = len(pop)
    indicesDesc = []
    indices = []
    for i in range(qt):
        for j in range(qt):
            if i != j:
                boolean = Similarity(pop[i], pop[j])
                if boolean is True:
                    indicesDesc.append(j)
                elif boolean is False and i not in indicesDesc and i not in indices:
                    indices.append(i)

    return sorted(set(indices))