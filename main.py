import itertools

ranks_list = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
hand_length = 5


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return 8, max(ranks)
    elif kind(4, ranks):
        return 7, kind(4, ranks), kind(1, ranks)
    elif kind(3, ranks) and kind(2, ranks):
        return 6, kind(3, ranks), kind(2, ranks)
    elif flush(hand):
        return 5, ranks
    elif straight(ranks):
        return 4, max(ranks)
    elif kind(3, ranks):
        return 3, kind(3, ranks), ranks
    elif two_pair(ranks):
        return 2, two_pair(ranks), ranks
    elif kind(2, ranks):
        return 1, kind(2, ranks), ranks
    else:
        return 0, ranks


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    return sorted([get_rank(rank) for rank, suit in hand], reverse=True)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    return len(set([suit for rank, suit in hand])) == 1


def straight(ranks):
    """Возвращает list рангов, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    for idx, rank in enumerate(ranks[1:], 1):
        if ranks[idx - 1] - rank != 1:
            return False
    return True


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    groups = [rank for rank, group in itertools.groupby(ranks) if len(list(group)) == n]
    return groups[0] if groups else None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    pair = [rank for rank, group in itertools.groupby(ranks) if len(list(group)) == 2]
    return pair if len(pair) == 2 else None


def get_rank(rank):
    return ranks_list.index(rank) + 2


def create_card(rank, suit):
    return ''.join([rank, suit])


def check_hand(cur_rank, cur_options, cur_cards, max_rank, max_options, max_cards):
    need_update = False

    if cur_rank > max_rank:
        need_update = True
    elif cur_rank == max_rank:
        if cur_rank in [8, 4]:
            need_update = max_options[0] < cur_options[0]
        elif cur_rank in [7, 6]:
            max_main_kind, cur_main_kind = max_options[1], cur_options[1]
            need_update = max_main_kind <= cur_main_kind and sum(max_options) < sum(cur_options)
        elif cur_rank == 5:
            need_update = max_options < cur_options
        else:
            ranks_idx = 1 if cur_rank in [3, 2, 1] else 0
            max_ranks, cur_ranks = max_options[ranks_idx], cur_options[ranks_idx]
            need_update = not max_ranks or sum(max_ranks) < sum(cur_ranks)

    if need_update:
        max_rank, max_options, max_cards = cur_rank, cur_options, cur_cards
    return max_rank, max_options, max_cards


def best_options_from_hand(hand):
    groups = itertools.combinations(hand, hand_length)

    # max_rank, max_hand_rank_options, max_cards
    max_options = (0, [0, 0], [])

    for group in groups:
        cur_rank, *cur_options = hand_rank(group)
        max_options = check_hand(cur_rank, cur_options, group, *max_options)
    return max_options


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    max_options = best_options_from_hand(hand)
    return max_options[2]


def jokers_suit(jokers):
    equal_suits = {
        'B': 'CS',
        'R': 'HD'
    }
    return ''.join([equal_suits[suit] for rank, suit in jokers])


def cards_from_joker_suit(suit, hand):
    return [create_card(rank, suit) for rank in ranks_list if create_card(rank, suit) not in hand]


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    jokers = [card for card in hand if '?' in card]

    if not jokers:
        return best_hand(hand)

    hand = list(set(hand) - set(jokers))

    # max_rank, max_hand_rank_options, max_cards
    max_options = (0, [0, 0], [])

    new_cards_pairs = []

    for joker in jokers:
        suits = jokers_suit([joker])
        new_pair = [create_card(rank, suit) for suit in suits for rank in ranks_list
                    if create_card(rank, suit) not in hand]

        new_cards_pairs.append(new_pair)

    new_cards_combinations = itertools.product(*new_cards_pairs)

    for new_pair in new_cards_combinations:
        cur_options = best_options_from_hand(hand + list(new_pair))
        max_options = check_hand(*cur_options, *max_options)
    return max_options[2]


def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
