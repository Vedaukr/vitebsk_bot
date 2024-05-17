def filter_unique(base_list, getter_func):
    helper_dict = {}
    for el in base_list:
        comparing_element = getter_func(el)
        if comparing_element in helper_dict:
            continue
        helper_dict[comparing_element] = el

    return list(helper_dict.values())