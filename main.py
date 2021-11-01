import argparse
import json
import os
from urllib import parse
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


def save_round_data(tournaments_data_file, save_file, append=False):
    tournaments_data = json.loads(tournaments_data_file.read())

    if append:
        try:
            old_tournaments_data = json.loads(save_file.read())
        except json.decoder.JSONDecodeError:
            old_tournaments_data = {"Tournaments": []}
    else:
        old_tournaments_data = {"Tournaments": []}

    tournaments_to_remove = [tournament["Tournament"]
                             for tournament in old_tournaments_data["Tournaments"]]
    filtered_tournaments = [tournament for tournament in tournaments_data["Tournaments"]
                            if tournament["Tournament"] not in tournaments_to_remove]
    tournaments_data["Tournaments"] = filtered_tournaments

    new_tournaments_data = process_tournaments_data(tournaments_data)
    combined_tournaments = (new_tournaments_data["Tournaments"]
                            + old_tournaments_data["Tournaments"])
    new_tournaments_data["Tournaments"] = combined_tournaments

    save_file.seek(0)
    save_file.truncate()
    save_file.write(json.dumps(new_tournaments_data))


def save_elos(tournaments_data_file, save_file, append=False):
    tournaments_data = json.loads(tournaments_data_file.read())

    if append:
        try:
            elos = json.loads(save_file.read())
        except json.decoder.JSONDecodeError:
            elos = {}
    else:
        elos = {}

    update_elos_from_tournaments_data(elos, tournaments_data)
    elos = sort_elos(elos)
    elos_json = json.dumps(elos)

    save_file.seek(0)
    save_file.truncate()
    save_file.write(elos_json)


def update_elos_from_tournaments_data(elos, tournaments_data, log=print):
    tournaments = tournaments_data["Tournaments"]
    total_tournaments = len(tournaments)
    for i, tournament in enumerate(tournaments, start=1):
        log(f"Calculating ELOs from tournament {i} of {total_tournaments}...")
        rounds = tournament["Rounds"]
        for round in rounds:
            update_elos(elos, round)
    return elos


def save_rankings(elos_file, save_file, append=False):
    elos = json.loads(elos_file.read())
    elo_rankings = "\n".join(f"{n}. {name}: {floor(elo)}" for n,
                             (name, elo) in enumerate(elos.items(), start=1))
    print("Saving Rankings...")
    save_file.write(elo_rankings)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Download debate round data and calculating ELO rankings.')
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '-d', '--download',
        dest='action',
        action='store_const',
        const=save_round_data,
    )
    action_group.add_argument(
        '-c', '--calculate',
        dest='action',
        action='store_const',
        const=save_elos,
    )
    action_group.add_argument(
        '-r', '--rank',
        dest='action',
        action='store_const',
        const=save_rankings,
    )
    parser.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='Avoids overwriting data.',
    )
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('outfile', type=argparse.FileType('r+'))

    return parser.parse_args()


def main():
    args = parse_args()

    with args.infile as infile, args.outfile as outfile:
        args.action(
            infile,
            outfile,
            append=args.append
        )
    print("Done.")


if __name__ == "__main__":
    main()
