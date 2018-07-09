import itertools

ranks_list = list(map(lambda x: str(x), range(2, 10))) + ['T', 'J', 'Q', 'K', 'A']


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


def flush(hand, count=5):
    """Возвращает True, если все карты одной масти"""
    groups = get_suit_groups(hand)
    return bool([suit for suit, group in groups if len(list(group)) >= count])


def straight(ranks, count=5):
    """Возвращает list рангов, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    result = [ranks[0]]
    for idx in range(0, len(ranks)):
        if ranks[idx - 1] - ranks[idx] == 1:
            result.append(ranks[idx])
            if len(result) == count:
                return result
        else:
            result = [ranks[idx]]
    return False


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    groups = [rank for rank, group in itertools.groupby(ranks) if len(list(group)) == n]
    return groups[0] if groups else None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    pair = [rank for rank, group in itertools.groupby(ranks) if len(list(group)) == 2]
    return pair[:2] if len(pair) > 1 else None


def get_suit_groups(hand):
    """Группы по масти"""
    def key_func(card):
        return card[1]
    return itertools.groupby(sorted(hand, key=key_func), key_func)


def get_rank(rank):
    return ranks_list[rank - 2] if isinstance(rank, int) else ranks_list.index(rank) + 2


def sort_hand(hand):
    return sorted(hand, key=lambda card: ranks_list.index(card[0]), reverse=True)


def find_last_rank(ranks):
    """Лучший ранг"""
    return ranks[0] + 1 if ranks[0] < 14 else ranks[-1] - 1


def jokers_suit(jokers):
    equal_suits = {
        'B': 'CS',
        'R': 'HD'
    }
    return ''.join([equal_suits[card[1]] for card in jokers])


def get_remain_suits(rank, from_suits, hand):
    return [suit for suit in from_suits if rank + suit not in hand]


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    rank, *options = hand_rank(hand)

    if rank in [4, 8]:
        suit = ''
        if rank == 8:
            suit = max([idx for idx, group in get_suit_groups(hand)], key=len)
        result = []
        options_rank = options[0]
        for idx in range(options_rank, 1, -1):
            current_rank = get_rank(idx)
            if rank == 8:
                card = [current_rank + suit]
            else:
                card = list(filter(lambda curr_card: current_rank in curr_card, hand))

            if card and card[0] in hand:
                result.append(card[0])
                if len(result) == 5:
                    return result
            else:
                result.clear()
    elif rank == 5:
        cards = max([list(group) for idx, group in get_suit_groups(hand)], key=len)
        return sort_hand(cards)[:5]
    else:
        if rank in [6, 7]:
            ranks = options
        elif rank in [1, 2, 3]:
            found_rank, ranks = options
            if rank != 2:
                found_rank = [found_rank]
            remain_ranks = [rank for rank in ranks if rank not in found_rank][:3]
            ranks = found_rank + remain_ranks
        else:
            ranks = options[0][:5]

        symbol_ranks = [get_rank(rank) for rank in ranks]
        return list(filter(lambda curr_rank: curr_rank[0] in symbol_ranks, hand))[:5]


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    jokers = [card for card in hand if '?' in card]
    if not jokers:
        return best_hand(hand)

    hand = sort_hand(list(set(hand) - set(jokers)))
    jokers_suits, ranks, suits = jokers_suit(jokers), card_ranks(hand), ('H', 'C', 'D', 'S')

    # 4 одной масти => 8,5
    if flush(hand, 4):
        max_group = max([list(group) for idx, group in get_suit_groups(hand)], key=len)
        suit = max_group[0][1]

        if suit in jokers_suits:
            cards = straight(card_ranks(max_group), 4) or card_ranks(max_group)[:4]
            cards.append(find_last_rank(cards))
            return [get_rank(rank) + suit for rank in cards]
    # Пара и 2 джокера или 3 одинакового ранга => 7
    if kind(2, ranks) and len(jokers) == 2 or kind(3, ranks):
        rank_list = []
        if kind(3, ranks):
            rank_list.append(kind(3, ranks))
        if len(jokers) == 2:
            rank_list.append(kind(2, ranks))

        for rank in sorted(rank_list, reverse=True):
            allow_suits = get_remain_suits(get_rank(rank), suits, hand)
            if all(suit in jokers_suits for suit in allow_suits):
                cards = [get_rank(rank) + suit for suit in suits]
                cards.append(sort_hand(list(set(hand) - set(cards)))[0])
                return cards
    # Две пары => 6
    if two_pair(ranks):
        ranks = two_pair(ranks)
        cards = list(filter(lambda card: get_rank(card[0]) in ranks, hand))

        for rank, pair_suits in itertools.groupby(cards, lambda card: card[0]):
            allow_suits = get_remain_suits(rank, jokers_suits, hand)
            if allow_suits:
                cards.append(rank + allow_suits[0])
                return cards
    # 3 подряд и 2 джокера или 4 подряд => 4
    if straight(ranks, 3) and len(jokers) == 2 or straight(ranks, 4):
        hand_ranks = card_ranks(hand)
        ranks = straight(hand_ranks, 3) if len(jokers) == 2 else straight(hand_ranks, 4)
        cards = [card for card in hand if get_rank(card[0]) in ranks]

        while len(cards) != 5:
            new_rank = find_last_rank(sorted(ranks, reverse=True))
            ranks.append(new_rank)
            cards.append(get_rank(new_rank) + jokers_suits[0])
        return cards
    # Пара или ничего => 3
    cards = []
    if kind(2, ranks):
        rank = get_rank(kind(2, ranks))
        kind_suits = [card[1] for card in hand if card[0] == rank]
        last_suit = list(set(jokers_suits) - set(kind_suits))

        if last_suit:
            kind_suits.append(last_suit[0])
            cards = [rank + suit for suit in kind_suits]
    else:
        card = hand[0]
        cards = [card[0] + suit for suit in jokers_suits if suit != card[1]][:len(jokers)]
        cards.append(card)
    return (cards + sort_hand(list(set(hand) - set(cards))))[:5]


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
