a = ["a", "b", "c", "d", "e", "f", "g", "h"]

print("#", a[:])
print("#", a[:5])
print("#", a[:-1])
print("#", a[4:])
print("#", a[-3:])
print("#", a[2:5])
print("#", a[2:-1])
print("#", a[-3:-1])


b = a[3:]
print("Before:   ", b)
b[1] = 99
print("After:    ", b)
print("No change:", a) 