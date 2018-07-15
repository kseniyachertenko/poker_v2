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
    groups = get_suit_groups(hand)
    return bool([suit for suit, group in groups.items() if len(group) >= hand_length])


def straight(ranks):
    """Возвращает list рангов, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    result = [ranks[0]]
    for idx, rank in enumerate(ranks):
        if ranks[idx - 1] - rank == 1:
            result.append(rank)
            if len(result) == hand_length:
                return result
        else:
            result = [rank]
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
    suits = {'C': [], 'S': [], 'H': [], 'D': []}
    for idx, card in enumerate(hand):
        suits[card[1]].append(hand[idx])
    return suits


def get_rank(rank):
    return ranks_list[rank - 2] if isinstance(rank, int) else ranks_list.index(rank) + 2


def sort_hand(hand):
    return sorted(hand, key=lambda card: ranks_list.index(card[0]), reverse=True)


def find_last_rank(ranks):
    """Лучший ранг"""
    max_rank, min_rank = ranks[0], ranks[-1]
    return max_rank + 1 if max_rank < get_rank('A') else min_rank - 1


def jokers_suit(jokers):
    equal_suits = {
        'B': 'CS',
        'R': 'HD'
    }
    return ''.join([equal_suits[suit] for rank, suit in jokers])


def get_card(rank, suit):
    if isinstance(rank, int):
        rank = get_rank(rank)
    return rank + suit


def get_remain_suits(rank, from_suits, hand):
    return [suit for suit in from_suits if get_card(rank, suit) not in hand]


def get_card_straight(hand, count, is_same_suit=False):
    cards = [hand[0]]
    for idx, [rank, suit] in enumerate(hand[1:], 1):
        prev_rank, prev_suit = cards[-1]
        if get_rank(prev_rank) - get_rank(rank) == 1:

            if is_same_suit and prev_suit != suit:
                cards.pop()

            cards.append(hand[idx])
            if len(cards) == count:
                return cards
        else:
            cards = [hand[idx]]


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    hand_rank_number, *options = hand_rank(hand)
    hand = sort_hand(hand)

    if hand_rank_number in [4, 8]:
        is_same_suit = hand_rank_number == 8
        return get_card_straight(hand, hand_length, is_same_suit)

    elif hand_rank_number == 5:
        cards = max([group for suit, group in get_suit_groups(hand)], key=len)
        return sort_hand(cards)[:hand_length]
    else:
        if hand_rank_number in [6, 7]:
            ranks = options
        elif hand_rank_number in [1, 2, 3]:
            found_rank, all_ranks = options

            if hand_rank_number != 2:
                found_rank = [found_rank]

            remain_ranks = list(set(all_ranks) - set(found_rank))[:3]
            ranks = found_rank + remain_ranks
        else:
            ranks = options[0][:hand_length]

        symbol_ranks = [get_rank(rank) for rank in ranks]
        return list(filter(lambda curr_card: curr_card[0] in symbol_ranks, hand))[:hand_length]


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    jokers = [card for card in hand if '?' in card]
    if not jokers:
        return best_hand(hand)

    hand = sort_hand(list(set(hand) - set(jokers)))
    jokers_suits, ranks, suits = jokers_suit(jokers), card_ranks(hand), ('H', 'C', 'D', 'S')

    suits = get_suit_groups(hand)
    max_group_suit = max(suits, key=len)

    # 4 одной масти => 8,5
    if len(suits[max_group_suit]) > 3:
        if max_group_suit in jokers_suits:
            straight_cards = get_card_straight(suits[max_group_suit], 4)

            cards = straight_cards or suits[max_group_suit][:4]
            last_rank_number = find_last_rank(card_ranks(cards))
            cards.append(get_card(last_rank_number, max_group_suit))
            return cards
    # Пара и 2 джокера или 3 одинакового ранга => 7
    rank_list = []
    if kind(2, ranks) and len(jokers) == 2:
        rank_list.append(kind(2, ranks))
    if kind(3, ranks):
        rank_list.append(kind(3, ranks))
    if rank_list:
        for rank in sorted(rank_list, reverse=True):
            remain_suits = get_remain_suits(get_rank(rank), suits, hand)
            if all(suit in jokers_suits for suit in remain_suits):
                cards = [get_card(rank, suit) for suit in suits]

                remain_card = sort_hand(list(set(hand) - set(cards)))[0]
                cards.append(remain_card)
                return cards
    # Две пары => 6
    if two_pair(ranks):
        pair_ranks = sorted(two_pair(ranks), reverse=True)
        cards = [card for card in hand if get_rank(card[0]) in pair_ranks]

        for pair_rank in pair_ranks:
            remain_suits = get_remain_suits(get_rank(pair_rank), jokers_suits, cards)
            if remain_suits:
                cards.append(get_card(pair_rank, remain_suits[0]))
                return cards
    # 3 подряд и 2 джокера или 4 подряд => 4
    straight_cards = get_card_straight(hand, hand_length - len(jokers))
    if straight_cards:
        while len(straight_cards) != hand_length:
            straight_ranks = card_ranks(sort_hand(straight_cards))
            new_rank = find_last_rank(straight_ranks)
            straight_cards.append(get_card(new_rank, jokers_suits[0]))
        return straight_cards
    # Пара или ничего => 3
    cards = []
    pair_rank = kind(2, ranks)
    if pair_rank:
        pair_suits = [suit for rank, suit in hand if rank == get_rank(pair_rank)]

        remain_suits = list(set(jokers_suits) - set(pair_suits))
        if remain_suits:
            pair_suits.append(remain_suits[0])
            cards = [get_card(pair_rank, suit) for suit in pair_suits]
    else:
        max_card_rank, max_card_suit = hand[0]
        cards = [get_card(max_card_rank, suit) for suit in jokers_suits if suit != max_card_suit][:len(jokers)]
        cards.append(hand[0])
    return (cards + sort_hand(list(set(hand) - set(cards))))[:hand_length]


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
