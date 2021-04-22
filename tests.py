import pickle
a = {'a':0}
a['a'] +=1
with open('file.txt', 'wb') as handle:
    pickle.dump(a, handle)
with open('file.txt', 'rb') as handle:
    b = pickle.loads(handle.read())
