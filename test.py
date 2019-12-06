fresh_fruit = {
    "apple": 10,
    "banana": 8,
    "lemon": 5,
}


class OutOfBananas(Exception):
    pass


def make_lemonade(count):
    pass


def make_cider(count):
    pass

def slice_bananas(count):
    pass


def make_smoothies(count):
    pass


def out_of_stock():
    pass


if count := fresh_fruit.get("lemon", 0):
    make_lemonade(count)
else:
    out_of_stock()


if (count := fresh_fruit.get("apple", 0)) >= 4:
    make_cider(count)
else:
    out_of_stock()


if (count := fresh_fruit.get("banana", 0) >= 2):
    pieces = slice_bananas(count)
else:
    pieces = 0


try:
    smoothies = make_smoothies(pieces)
except OutOfBananas:
    out_of_stock()


#~~~~~~~~~~~~~~~~~~~~~


if (count := fresh_fruit.get("banana", 0)) >= 2:
    pieces = slice_bananas(count)
    to_enjoy = make_smoothies(count)
elif (count := fresh_fruit.get("apple", 0)) >= 4:
    to_enjoy = make_cider(count)
elif count := fresh_fruit.get("lemon", 0):
    to_enjoy = make_lemonade(count)
else:
    to_enjoy = "Nothing"

#~~~~~~~~~~~~~~~~~~~~~~

def pick_fruit():
    pass


def make_juice(fruit, count):
    pass

bottles = []
while fresh_fruit := pick_fruit():
    for fruit, count in fresh_fruit.items():
        batch = make_juice(fruit, count)
        bottles.extend(batch)
    