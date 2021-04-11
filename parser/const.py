parser_errors = {
    'eop': ('NCSParser ERROR:\n\tНеочікуваний кінець програми - в таблиці символів немає запису з номером %s.', 1001),
    'after_eop': ('NCSParser ERROR:\n\tНеочікуваіні лексеми за межами головної програми.', 1002),
    'tokens': ('NCSParser ERROR:\n\tВ рядку %s неочікуваний елемент (%s, %s). '
               '\n\tОчікувався - (%s, %s).', 1),
    'not_expected': (f'\n\tВ рядку %s неочікуваний елемент (%s, %s).\n\tОчікувався - %s.', 2)
}

parser_warnings = {
    'no_effect': 'NCSParser Warning: \n\tВираз на рядку %s не має ефекту.'
}