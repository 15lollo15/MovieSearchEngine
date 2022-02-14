tmp = [('b',2),('a',2)]
print(sorted(tmp, key=(lambda t : (t[1], t[0]))))