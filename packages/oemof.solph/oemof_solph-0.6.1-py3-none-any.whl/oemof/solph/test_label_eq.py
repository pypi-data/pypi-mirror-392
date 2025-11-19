import pandas as pd

class MyClass:
    def __init__(self, label):
        self._label = label

    def __eq__(self, other):
        if isinstance(other, MyClass):
            return self._label == other._label
        else:
            return self._label == other

    def __hash__(self):
        return hash(self._label)

    def __str__(self):
        return str(self._label)


foo = MyClass(("foo",))
bar = MyClass(("bar",))
my_dict1 = {(foo, bar): [1,2,3,4]}

my_key = (("foo",), ("bar",))
print(my_dict1[my_key])

df1 = pd.DataFrame(my_dict1)

print(df1[(foo, bar)])

# problem with multi-level pandas
try:
    print(df1[(("foo",), ("bar",))])
except KeyError as ke:
    print(f"Key not found: {ke}")
    print(f"Working key:   {my_key}")

# possible workaround
my_dict1b = df1.to_dict()
print(my_dict1b[my_key].values())

# another workaround
print(df1[MyClass(("foo",)), MyClass(("bar",))])

# plain labels work
foo_plain = MyClass("foo")
bar_plain = MyClass("bar")
my_dict2 = {(foo_plain, bar_plain): [1,2,3,4]}

df2 = pd.DataFrame(my_dict2)
my_key_plain = ("foo", "bar")
print(my_dict2[my_key_plain])
print(df2[my_key_plain])
