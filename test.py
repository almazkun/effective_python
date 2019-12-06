fresh_fruit = {
    "apple": 10,
    "banana": 8,
    "lemon": 5,
}
counter = 0

class OutOfBananas(Exception):
    pass


def make_lemonade(count):
    print("lemonade made")


def make_cider(count):
    print("cider made")

def slice_bananas(count):
    print("banana made")


def make_smoothies(count):
    print("smoothie made")


def out_of_stock():
    print("Made nothing")


def lemon():
    if count := fresh_fruit.get("lemon", 0):
        make_lemonade(count)
        print(counter)
        counter += 1
    else:
        out_of_stock()


def apple():    
    if (count := fresh_fruit.get("apple", 0)) >= 4:
        make_cider(count)
        print(counter)
        counter += 1
    else:
        out_of_stock()


def banana():
    if (count := fresh_fruit.get("banana", 0) >= 2):
        pieces = slice_bananas(count)
        print(counter)
        counter += 1
    else:
        pieces = 0



    try:
        smoothies = make_smoothies(pieces)
        print(counter)
        counter += 1
    except OutOfBananas:
        print(counter)
        counter += 1
        out_of_stock()


#~~~~~~~~~~~~~~~~~~~~~

def all():
    if (count := fresh_fruit.get("banana", 0)) >= 2:
        print(counter)
        counter += 1
        pieces = slice_bananas(count)
        to_enjoy = make_smoothies(count)
        
    elif (count := fresh_fruit.get("apple", 0)) >= 4:
        print(counter)
        counter += 1
        to_enjoy = make_cider(count)
    elif count := fresh_fruit.get("lemon", 0):
        print(counter)
        counter += 1
        to_enjoy = make_lemonade(count)
    else:
        print(counter)
        counter += 1
        to_enjoy = "Nothing"

#~~~~~~~~~~~~~~~~~~~~~~

def pick_fruit():
    print("Pick_fruit picked")


def make_juice(fruit, count):
    print(counter, "juice made")
    


bottles = []

while fresh_fruit := pick_fruit():
    for fruit, count in fresh_fruit.items():
        print(counter)
        counter += 1
        batch = make_juice(fruit, count)
        bottles.extend(batch)
    

lemon()
apple()
banana()
all()
make_juice("banana", 2)