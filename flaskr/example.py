#l1- variable declaration,inputs
#l2- if else, loops, functions
#l3-practice

def cons_spliter(c):
    m=[]
    k=[]
    l=len(c)
    if c[1][0]-c[0][0]==1:
        k.append(c[0])
    else:
        m.append([c[0]])
    for i in range(1,l):
        if c[i][0]-c[i-1][0]!=1:
            m.append(k)
            k=[]
        k.append(c[i])
    m.append(k)
    return m
print(cons_spliter([(1,2),(2,3),(3,4),(6,4),(7,3),(9,2),(11,3)]))










