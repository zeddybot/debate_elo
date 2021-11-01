import json
import os
from calc import calc_elo, prob_win
from math import floor
from time import sleep
from urllib.parse import urlencode
from webscraper import process_tournaments_data


def update_elos(elos, round):
    """
    Updates a hasmhmap of elos with a single rounds.
    """
    aff, neg, winners = round["Aff"], round["Neg"], round["Winners"]

    # Doesn't calculate the elo of rounds with no winner
    if not (aff and neg and winners):
        return elos
    # 1000 is the baseline ELO
    aff_elo, neg_elo = elos.get(aff, 1000), elos.get(neg, 1000)
    exp_aff_win_prob = prob_win(aff_elo, neg_elo)
    exp_neg_win_prob = prob_win(neg_elo, aff_elo)
    for winner in winners:
        if winner == "AFF":
            true_aff_win_prob, true_neg_win_prob = 1, 0
        elif winner == "NEG":
            true_aff_win_prob, true_neg_win_prob = 0, 1
        aff_elo = calc_elo(aff_elo, true_aff_win_prob, exp_aff_win_prob)
        neg_elo = calc_elo(neg_elo, true_neg_win_prob, exp_neg_win_prob)
    elos.update({aff: aff_elo, neg: neg_elo})
    return elos


def sort_elos(elos):
    """
    Sorts the hashmap of ELOs in ascending order.
    """
    return dict(sorted(elos.items(), key=lambda item: item[1], reverse=True))


def save_round_data(path_to_tournament_data, path_to_save):
    # Extracts URLs from file
    with open(path_to_tournament_data, "r") as f:
        tournaments_data = json.loads(f.read())

    # Process all tournaments into a list of hashmaps,
    # and print updates after every tournament is processed.

    new_tournaments_data = process_tournaments_data(tournaments_data)

    with open(path_to_save, "w") as f:
        f.write(json.dumps(new_tournaments_data))

    return new_tournaments_data


def save_elos(elos, path_to_save):
    elos_json = json.dumps(elos)
    with open(path_to_save, "w") as f:
        f.write(elos_json)


def update_elos_from_tournaments_data(elos, tournaments_data, log=print):
    tournaments = tournaments_data["Tournaments"]
    total_tournaments = len(tournaments)
    for i, tournament in enumerate(tournaments, start=1):
        log(f"Calculating ELOs from tournament {i} of {total_tournaments}...")
        rounds = tournament["Rounds"]
        for round in rounds:
            update_elos(elos, round)
    return elos


def save_rankings(elos, path_to_save):
    elo_rankings = "\n".join(f"{n}. {name}: {floor(elo)}" for n,
                             (name, elo) in enumerate(elos.items(), start=1))
    with open(path_to_save, "w") as f:
        f.write(elo_rankings)


def main():
    """
    Processes a list of tournaments.
    """

    # Relevant file of URLs
    DATASET = "new_ld_2020.json"

    # Extracts URLs from file
    tournaments_data = save_round_data(os.path.join("datasets", DATASET))

    # Calculate and sort the ELOs
    elos = {}
    update_elos_from_tournaments_data(elos, tournaments_data)
    elos = sort_elos(elos)

    # Save all the data
    if not os.path.exists(DATASET):
        os.mkdir(DATASET)

    print("Saving ELOs...")
    save_elos(elos, "test2.json")

    print("Saving Rankings...")
    save_rankings(elos, "test3.json")


if __name__ == "__main__":
    main()
