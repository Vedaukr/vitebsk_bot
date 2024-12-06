import Levenshtein

def find_closest_word(target_word: str, word_list: list[str]):

    min_distance = float('inf')
    closest_word = None
    
    for word in word_list:
        distance = Levenshtein.distance(target_word, word)
        if distance < min_distance:
            min_distance = distance
            closest_word = word
        
        if distance == 0:
            break
    
    return closest_word, min_distance