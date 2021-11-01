import json
import os
from math import floor
from time import sleep
from urllib.parse import urlencode
from webscraper import process_tournaments_data


def update_elos(elos, rounds):
    """
    Updates a hasmhmap of elos with a list of rounds.
    """
    for round in rounds:
        aff = round.get("AFF")
        neg = round.get("NEG")
        winners = round.get("WINNERS")

        # Doesn't calculate the elo of rounds with no winner
        if aff and neg and winners:
            # 1000 is the baseline ELO
            aff_elo = elos.get(aff, 1000)
            neg_elo = elos.get(neg, 1000)
            aff_win_prob = prob_win(aff_elo, neg_elo)
            neg_win_prob = prob_win(neg_elo, aff_elo)
            for win in winners:
                if win == "AFF":
                    aff_elo = calc_elo(aff_elo, 1, aff_win_prob)
                    neg_elo = calc_elo(neg_elo, 0, neg_win_prob)
                elif win == "NEG":
                    aff_elo = calc_elo(aff_elo, 0, aff_win_prob)
                    neg_elo = calc_elo(neg_elo, 1, neg_win_prob)
            elos.update({aff: aff_elo, neg: neg_elo})
    return elos


def sort_elos(elos):
    """
    Sorts the hashmap of ELOs in ascending order.
    """
    return dict(sorted(elos.items(), key=lambda item: item[1], reverse=True))


def prob_win(a, b):
    """
    Calculates the chance player A will beat player B,
    given their respective ELOs.
    """
    return 1 / (1 + (10 ** ((b - a) / 400)))


def calc_elo(elo, true, expected):
    """
    Calculates the increase/decrease in ELO,
    with a K value of 32.
    """
    return elo + 32 * (true - expected)


def calc_winrates(rounds):
    winrates = {}

    for round in rounds:
        aff = round.get("AFF")
        neg = round.get("NEG")
        winners = round.get("WINNERS")
        if aff and neg and winners:
            aff_wins = winners.count("AFF")
            neg_wins = winners.count("NEG")
            aff_wr = winrates.get(aff, [0, 0])
            neg_wr = winrates.get(neg, [0, 0])
            aff_wr[0] += aff_wins
            neg_wr[0] += neg_wins
            aff_wr[1] += aff_wins + neg_wins
            neg_wr[1] += aff_wins + neg_wins
            winrates.update({aff: aff_wr, neg: neg_wr})
    return winrates


def sort_and_eval_winrates(winrates):
    items = [(name, wins / rounds)
             for name, (wins, rounds) in winrates.items() if rounds > 0]
    return dict(sorted(items, key=lambda item: item[1], reverse=True))


def save_round_data(path_to_tournament_data, path_to_save):
    # Extracts URLs from file
    with open(path_to_tournament_data, "r") as f:
        tournaments_data = json.loads(f.read())

    # Process all tournaments into a list of hashmaps,
    # and print updates after every tournament is processed.

    new_tournaments_data = process_tournaments_data(tournaments_data)

    with open(path_to_save, "w") as f:
        f.write(json.dumps(new_tournaments_data))


def main():
    """
    Processes a list of tournaments.
    """

    # Relevant file of URLs
    DATASET = "new_ld_2020.json"

    # Extracts URLs from file
    save_round_data(os.path.join("datasets", DATASET))

    # # Calculate and sort the ELOs
    # print("Calculting ELOs...")
    # elos = update_elos({}, rounds)

    # print("Sorting ELOS...")
    # elos = sort_elos(elos)

    # # Calculate and sort the Winrates
    # print("Calculating winrates...")
    # winrates = calc_winrates(rounds)

    # print("Sorting winrates...")
    # winrates = sort_and_eval_winrates(winrates)

    # # Save all the data
    # if not os.path.exists(DATASET):
    #     os.mkdir(DATASET)

    # print("Saving Rounds...")
    # rounds_json = json.dumps(rounds)
    # with open(os.path.join(DATASET, "rounds.txt"), "w") as f:
    #     f.write(rounds_json)

    # print("Saving ELOs...")
    # elos_json = json.dumps(elos)
    # with open(os.path.join(DATASET, "elos.txt"), "w") as f:
    #     f.write(elos_json)

    # print("Saving winrates...")
    # winrates_json = json.dumps(winrates)
    # with open(os.path.join(DATASET, "winrates.txt"), "w") as f:
    #     f.write(winrates_json)

    # print("Saving Rankings...")
    # elo_rankings = "\n".join(f"{n}. {name}: {floor(elo)}" for n,
    #                          (name, elo) in enumerate(elos.items(), 1))
    # with open(os.path.join(DATASET, "elo_rankings.txt"), "w") as f:
    #     f.write(elo_rankings)

    # wr_rankings = "\n".join(f"{n}. {name}: {winrate * 100}" for n,
    #                         (name, winrate) in enumerate(winrates.items(), 1))
    # with open(os.path.join(DATASET, "winrate_rankings.txt"), "w") as f:
    #     f.write(wr_rankings)


if __name__ == "__main__":
    main()
