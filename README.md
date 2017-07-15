# transcations-mapper

Script which maps bank statement export files to a common format suitable to be imported to our excel spredsheet.

## Features

- map Lloyds export csv format to our csv format
- map Monzo export csv format to our csv format
- map TSB export csv format to our csv format

## Prerequisities

Requires Python 3.5 or greater.

## Usage

1. Clone the repo

    `git clone git@github.com:jakubka/transcations-mapper.git`

2. Save export files

    - `lloyds_maja.csv` - will be mapped with LloydsMaja account name
    - `lloyds_master.csv` - will be mapped with LloydsMaster account name
    - `monzo_maja.csv` - will be mapped with MonzoMaja account name
    - `monzo_jakub.csv` - will be mapped with MonzoJakub account name
    - `tsb.csv` - will be mapped with TSBJakub account name

3. Run

    ```sh
    python mapper.py
    ```

4. Output will be written to `output.csv`
5. Open new excel workbook and insert data
6. Copy date to the main workbook (paste values)
7. Fill categories and account names
