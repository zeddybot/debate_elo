def prob_win(a, b):
    """
    Calculates the chance player A will beat player B, given their respective ELOs.
    A differential in ELOs of 400 corresponds to a 10x differential in expected
    win probabilities.
    """
    magnitude_score_differential = 400
    return 1 / (1 + (10 ** ((b - a) / magnitude_score_differential)))


def calc_elo(elo, true, expected):
    """
    Calculates the increase/decrease in ELO,
    with a K value of 32.
    """
    k = 32
    return elo + k * (true - expected)
