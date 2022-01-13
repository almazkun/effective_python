import json

UNDEFINED = object()


def divide_json(path):
    print(" * Open file")
    handle = open(path, "r+")  # OSError may happen
    try:
        print(" * Read file")
        data = handle.read()  # UnicodeDecodeError may happen
        print(" * Parse JSON")
        op = json.loads(data)  # ValueError may happen
        print(" * Divide")
        value = op["numerator"] / op["denominator"]  # ZeroDivisionError may happen
    except ZeroDivisionError as e:
        print(" * Handling ZeroDivisionError")
        return UNDEFINED
    else:
        print(" * Update file")
        op["result"] = value
        result = json.dumps(op)
        handle.seek(0)  # OSError may happen
        handle.write(result)  # OSError may happen
        return value
    finally:
        print(" * Close file")
        handle.close()  # Always executed


temp_path = "random_data.json"

divide_json(temp_path)
