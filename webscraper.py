from urllib.parse import urlencode
from web_utils import get_html


def tournament_to_url(tournament):
    """
    Convert a list of tournaments to a url that can be accessed
    through the requests library.
    """
    params = {"tourn_id": tournament["tourn_id"],
              "round_id": tournament["round_id"]}
    return "https://www.tabroom.com/index/tourn/results/round_results.mhtml?" + urlencode(params)


def get_round_urls(url):
    """
    Extracts a list of rounds urls from the url of a single round.
    """
    html = get_html(url)

    is_sidebar = lambda h4: "Results" in h4.string and "Event Results" not in h4.string
    sidebar = [h4 for h4 in html.find_all("h4") if is_sidebar(h4)][0].parent

    child_strings = lambda result: [child.string.strip().lower()
                                    for child in result.descendants if child.string is not None]
    is_result = lambda result: "round results" in child_strings(result)
    results = [result for result in sidebar.find_all("a") if is_result(result)]

    result_url = lambda result: "https://www.tabroom.com" + result["href"]
    result_urls = [result_url(result) for result in results]
    return reversed(result_urls)  # Puts the rounds in the correct order


def get_rounds(url):
    """
    Extracts every row of the table of rounds.
    """
    html = get_html(url)
    rounds = html.find("tbody").find_all("tr")
    return rounds


def debater_name(tag):
    name = tag["title"]
    words = tag.a.string.split()
    if words[-2:] == name.split():
        return ' '.join(words)
    else:
        return ' '.join(words[:-1]) + ' ' + name


def process_round(round):
    """
    Converts the BS4 Tree of a round into a
    dictionary of relevant information.
    """
    raw_info = [item for item in round.find_all(
        "td") if item["class"] == ["smallish"]]
    aff_tag, neg_tag, *rest_tags = raw_info
    aff, neg = debater_name(aff_tag), debater_name(neg_tag)
    if rest_tags:
        winner_tag = rest_tags[0]
        winners = [div.string.strip().upper()
                   for div in winner_tag.find_all("div")]
    else:
        winners = []

    return {"Aff": aff, "Neg": neg, "Winners": winners}


def all_rounds_from_tourney(tournament):
    """
    Processes all the rounds from a tournament.
    """
    round_urls = get_round_urls(tournament_to_url(tournament))
    rounds = [process_round(round) for round_url in round_urls
              for round in get_rounds(round_url)]
    return {"Tournament": tournament["Tournament"], "Rounds": rounds}


def process_tournaments_data(tournaments_data, log=print):
    tournaments = tournaments_data["Tournaments"]
    total_tournaments = len(tournaments)
    new_tournaments = []
    for i, tournament in enumerate(tournaments):
        log(f"Processing Tournament {i+1} of {total_tournaments}...")
        new_tournaments.append(all_rounds_from_tourney(tournament))
    return {"Tournaments": new_tournaments}
