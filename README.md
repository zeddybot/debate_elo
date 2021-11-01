# debate_elo

debate_elo is a script that allows for the downloading of data from debate rounds and the performing of simple analysis on the resultant data. Current features include the ability to calculate the ELO ranking of debaters in a given set of tournaments and to rank those debaters.

## Installation

This project uses Python 3.8.3. Some older versions may still be compatible.

After downloading, run `pip install -r requirements.txt` to install all required dependencies.

## Usage

For instructions on how to use the various functionalities of this project, run `python3 debate_elo.py -h`.

Note that any file to which data is to be written to must be created prior to program execution. If the file does not exist, the program will terminate early.

### Downloading Data

To download round data, run `python3 debate_elo.py -d [infile] [outfile]`. This will download all data from all the rounds in the tournaments indicated by the JSON in `infile` and store the resulting data in a JSON in `outfile`.
Sample tournament data is provided in the `data/ld_2020.json` file. To download data from other tournaments, locate the tournament page on Tabroom and open the page of a round of the desire format. The update the JSON with the tournament name, the tourn_id on Tabroom, and the round_id of the round on Tabroom. The round_id only matters insofar as it determines which event has rounds scraped from Tabroom. Choosing different rounds in the same event at the same tournament will have no effect on the functionality of the program.

When the program is run in append mode (as in `python3 debate_elo.py -d [infile] [outfile] -a`), round data will first be read from the JSON in `outfile`. Tournaments present in `outfile` will not be downloaded again, even if present in the JSON in `infile`. After downloading round data, this data will be combined with pre-existind data in `outfile` before being written to `outfile`.

### Calculating ELOs

To calculate ELOs, run `python3 debate_elo.py -c [infile] [outfile]`. This will compute the ELOs of all debaters present in rounds in `infile` and store those ELOs as a JSON in `outfile`. 

When the program is run in append mode (as in `python3 debate_elo.py -c [infile] [outfile] -a`), ELOs are first read from the JSON in `outfile`. These ELOs are used as the initial values before the rounds in `infile` are used to further update the ELOs. Therefore, if one wants to calculate the cumulative ELOs from tournaments spread across multiple JSON files, run `python3 debate_elo.py -c [infile] [outfile] -a` for every relevant JSON `infile`, while keeping `outfile` the same.

### Generating Rankings

To generate rankings, run `python3 debate_elo.py -r [infile] [outfile]`. This will read the ELOs from `infile` and convert them into a human-friendly format.

When the program is run in append mode, no change is made to the `--rank` functionality.

## License
[MIT](https://choosealicense.com/licenses/mit/)