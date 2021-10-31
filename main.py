import json
import os
from math import floor
from time import sleep
from urllib.parse import urlencode
from utils import get_html


def info_to_url(nums):
    """
    Convert a pair of tournament ID and round ID to
    a url that can be accessed through the requests library.
    """
    params = {"tourn_id": nums[0], "round_id": nums[1]}
    return "https://www.tabroom.com/index/tourn/results/round_results.mhtml?" + urlencode(params)


def get_round_urls(url):
    """
    Extracts a list of rounds urls from the url of a single round.
    """
    html = get_html(url)
    sidebar = [h4 for h4 in html.find_all(
        "h4") if "Results" in h4.string and "Event Results" not in h4.string][0].parent
    results = [result for result in sidebar.find_all("a") if "round results" in [
        child.string.strip().lower() for child in result.descendants if child.string is not None]]
    result_urls = ["https://www.tabroom.com" + result["href"]
                   for result in results]
    # Puts the rounds in the correct order
    return reversed(result_urls)


def get_rounds(url):
    """
    Extracts every row of the table of rounds.
    """
    html = get_html(url)
    rounds = html.find("tbody").find_all("tr")
    return rounds


def process_round(round):
    """
    Converts the BS4 Tree of a round into a
    dictionary of relevant information.
    """
    info = [item for item in round.find_all(
        "td") if item["class"] == ["smallish"]]
    aff_name = info[0]["title"]
    aff_words = info[0].a.string.split()
    # Some tournaments put the full name, and some only put the initials
    if aff_words[-2:] == aff_name.split():
        aff = ' '.join(aff_words)
    else:
        aff = ' '.join(aff_words[:-1]) + ' ' + aff_name

    neg_name = info[1]["title"]
    neg_words = info[1].a.string.split()
    if neg_words[-2:] == neg_name.split():
        neg = ' '.join(neg_words)
    else:
        neg = ' '.join(neg_words[:-1]) + ' ' + neg_name

    # Filters out byes and forfeits, and makes elim rounds count more
    if len(info) >= 3:
        winners = [div.string.strip().upper()
                   for div in info[2].find_all("div")]
    else:
        winners = []

    return {"AFF": aff, "NEG": neg, "WINNERS": winners}


def all_rounds_from_tourney(url):
    """
    Processes all the rounds from a tournament.
    """
    return [process_round(round) for round_url in get_round_urls(url) for round in get_rounds(round_url)]


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


def main():
    """
    Processes a list of tournaments.
    """

    # Relevant file of URLs
    DATASET = "ld_2020"

    # Extracts URLs from file
    with open(os.path.join("datasets", DATASET + ".txt"), "r") as f:
        urls = [info_to_url(nums) for nums in json.loads(f.read())]

    # Process all tournaments into a list of hashmaps,
    # and print updates after every tournament is processed.
    total_tournaments = len(urls)
    rounds = []
    for i, url in enumerate(urls):
        print(f"Processing Tournament {i+1} of {total_tournaments}...")
        rounds += all_rounds_from_tourney(url)
        # To avoid DDOSing Tabroom
        print("Sleeping...")
        # sleep(10)

    # Calculate and sort the ELOs
    print("Calculting ELOs...")
    elos = update_elos({}, rounds)

    print("Sorting ELOS...")
    elos = sort_elos(elos)

    # Calculate and sort the Winrates
    print("Calculating winrates...")
    winrates = calc_winrates(rounds)

    print("Sorting winrates...")
    winrates = sort_and_eval_winrates(winrates)

    # Save all the data
    if not os.path.exists(DATASET):
        os.mkdir(DATASET)

    print("Saving Rounds...")
    rounds_json = json.dumps(rounds)
    with open(os.path.join(DATASET, "rounds.txt"), "w") as f:
        f.write(rounds_json)

    print("Saving ELOs...")
    elos_json = json.dumps(elos)
    with open(os.path.join(DATASET, "elos.txt"), "w") as f:
        f.write(elos_json)

    print("Saving winrates...")
    winrates_json = json.dumps(winrates)
    with open(os.path.join(DATASET, "winrates.txt"), "w") as f:
        f.write(winrates_json)

    print("Saving Rankings...")
    elo_rankings = "\n".join(f"{n}. {name}: {floor(elo)}" for n,
                             (name, elo) in enumerate(elos.items(), 1))
    with open(os.path.join(DATASET, "elo_rankings.txt"), "w") as f:
        f.write(elo_rankings)

    wr_rankings = "\n".join(f"{n}. {name}: {winrate * 100}" for n,
                            (name, winrate) in enumerate(winrates.items(), 1))
    with open(os.path.join(DATASET, "winrate_rankings.txt"), "w") as f:
        f.write(wr_rankings)


if __name__ == "__main__":
    main()
