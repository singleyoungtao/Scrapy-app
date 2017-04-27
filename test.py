def a():
    print("abc")
    return True

b = a()
c = 1
if b:
    c = c + 1
    print(c)
else:
    print("error")