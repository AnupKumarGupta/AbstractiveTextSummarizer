inp = raw_input()
stopmarks = []
def find_marks(listcheck,ch,lst):
    return [i for i,ltr in enumerate(listcheck) if ch == ltr and i not in lst]

singlewords = [' '+chr(i) for i in range(97,123)]
doublequotes = find_marks(inp,'"',[])
cnt1 = inp.count(" '")
cnt2 = inp.count("' ")
cn1 = 0
cn2 = 0
cnn1 = []
cnn2 = []

for i in range(cnt1):
    cn1 = inp.index(" '",cn1)
    cnn1.append(cn1)

for i in range(cnt2):
    cn2 = inp.index("' ",cn2)
    cnn2.append(cn2)

for i in zip(cnn1,cnn2):
    x,y = i
    doublequotes = doublequotes + [x,y]

    
rem_full = []
rem_ques = []
rem_excla = []

for i in xrange(0,len(doublequotes),2):
    rem_full = rem_full + [j+doublequotes[i] for j in find_marks(inp[doublequotes[i]:doublequotes[i+1]],'.',[])]
    rem_ques = rem_ques + [j+doublequotes[i] for j in find_marks(inp[doublequotes[i]:doublequotes[i+1]],'?',[])]
    rem_excla = rem_excla + [j+doublequotes[i] for j in find_marks(inp[doublequotes[i]:doublequotes[i+1]],'!',[])]
fullstop = find_marks(inp,'.',rem_full)
tbrem = []
for i in fullstop:
    if(i==1 or i==2):
        tbrem.append(i)
    if(ord(inp[i-2])==32 and (ord(inp[i-1]) in range(65,91) or ord(inp[i-1]) in range(97,123))):
        tbrem.append(i)
    if(ord(inp[i-3])==32 and ord(inp[i-2]) in range(65,91) and ord(inp[i-1]) in range(97,123)):
        tbrem.append(i)
    if(ord(inp[i-3])==32 and ord(inp[i-2]) == 111 and ord(inp[i-1]) == 110):
        tbrem.append(i)


if('etc.' in inp):
    cnt = inp.count('etc.')
    ind = 0
    print 'etc. found'
    for i in range(cnt):
        new_ind = inp.index('etc.',ind) + 3
        tbrem.append(new_ind)
        ind = new_ind + 1

for i in tbrem:
    fullstop.remove(i)
        
questionmark = find_marks(inp,'?',rem_ques)
exclamation = find_marks(inp,'!',rem_excla)

a = fullstop + questionmark + exclamation
a = [0] + [i+1 for i in sorted(a)]

for i in xrange(len(a)-1):
    prnt = inp[a[i]:a[i+1]].split()
    print ' '.join(prnt)
