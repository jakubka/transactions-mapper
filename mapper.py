import csv
import datetime
import os
import re
import glob

OUTPUT_COLUMN_DATE = 0
OUTPUT_COLUMN_ACCOUNT_NAME = 1
OUTPUT_COLUMN_AMOUNT_GBP = 2
OUTPUT_COLUMN_AMOUNT_CZK = 3
OUTPUT_COLUMN_CATEGORY = 4
OUTPUT_COLUMN_SUB_CATEGORY = 5
OUTPUT_COLUMN_NOTE = 6
OUTPUT_COLUMN_MERCHANT = 7
OUTPUT_COLUMN_HOLIDAY = 8
OUTPUT_COLUMN_HOLIDAY = 9
OUTPUT_COLUMN_BUSINESS = 10


def read_bank_statement(file_name_pattern):
    file_paths = glob.glob(file_name_pattern)
    print('INFO: found {} files matching {} pattern: {}'
          .format(len(file_paths), file_name_pattern, file_paths))

    def generate():
        for file_path in file_paths:
            with open(file_path, newline='') as f:
                transactions = list(csv.reader(f))[1:]
                print('INFO: loaded {} transactions from {}'.format(len(transactions), file_path))
                yield from transactions
    return list(generate())


def map_lloyds_transactions(transactions, account_name):
    output = []
    for input_row in transactions:
        credit = 0 if input_row[6] == '' else float(input_row[6])
        debit = 0 if input_row[5] == '' else float(input_row[5])

        output_row = [
            input_row[0],  # Date
            account_name,  # Account
            credit - debit,  # Amount GBP
            '',  # Amount CZK
            '',  # Category
            '',  # Sub-category
            input_row[4],  # Note
            input_row[4],  # Merchant
            '',  # Holiday
            '',  # Business
        ]
        output.append(output_row)

    return output


def map_monzo_transactions(transactions, account_name):
    output = []

    for input_row in transactions:
        transaction_datetime = datetime.datetime.strptime(input_row[1], '%Y-%m-%d %H:%M:%S %z')

        output_row = [
            transaction_datetime.strftime('%d/%m/%Y'),  # Date
            account_name,  # Account
            float(input_row[2]),  # Amount GBP
            '',  # Amount CZK
            '',  # Category
            '',  # Sub-category
            input_row[8],  # Note
            input_row[8],  # Merchant
            '',  # Holiday
            '',  # Business
        ]
        output.append(output_row)

    return output


def map_amex_transactions(transactions):
    output = []

    for input_row in transactions:
        transaction_datetime = datetime.datetime.strptime(input_row[0], '%d %b %Y')

        output_row = [
            transaction_datetime.strftime('%d/%m/%Y'),  # Date
            'Amex',  # Account
            -float(input_row[3].replace('£', '')),  # Amount GBP
            '',  # Amount CZK
            '',  # Category
            '',  # Sub-category
            input_row[2],  # Note
            input_row[2],  # Merchant
            '',  # Holiday
            '',  # Business
        ]
        output.append(output_row)

    return output


EATING_OUT_LUNCH = ("EatingOut", "Lunch")
EATING_OUT_DRINKS = ("EatingOut", "Drinks")

merchant_to_category_mapping = [
    ("NETFLIX.COM", ("Entertainment", "")),
    ("tfl", ("Transport", "TFL")),
    ("(marks)|(m&s)", ("Groceries", "")),
    ("waitrose", ("Groceries", "")),
    ("pret a manger", ("EatingOut", "")),
    ("co-op", ("Groceries", "")),
    ("ocado", ("Groceries", "")),
    ("lookfantastic", ("Shopping", "Essentials")),
    ("uber bv", ("EatingOut", "Restaurant")),  # UberEATS
    ("uber", ("Transport", "Taxi")),
    ("treatwell", ("Bodycare", "")),
    ("amazon", ("Shopping", "")),
    ("sainsbury", ("Groceries", "")),
    ("tesco", ("Groceries", "")),
    ("interest", ("Income", "Interest")),
    ("leon", EATING_OUT_LUNCH),
    ("pod", EATING_OUT_LUNCH),
    ("MICROSOFT   \*ONEDR", ("Fixed", "Cloud")),
    ("PAYPAL\*PAYPAL\*MICROSOFT", ("Fixed", "Cloud")),
    ("THE GYM LTD", ("Sport", "Gym")),
    ("H&M", ("Shopping", "Clothing")),
    ("DELIVEROOCOUK", ("EatingOut", "Restaurant")),
    ("audible", ("Education", "Book")),
    ("skyscanner", ("Income", "Salary")),
    ("czechinvest", ("Income", "Salary")),
    ("GIFFGAFF.COM", ("Fixed", "Phone")),
    ("ITUNES.COM/BILL", ("Fixed", "Cloud")),
    ("CLUB LLOYDS (FEE)|(WAIVED)", ("Other", "")),
    ("LINDA MCCALLUM", ("Fixed", "Rent")),
    ("Boots", ("Shopping", "Essentials")),
    ("Better Gyms", ("Sport", "OneTime")),
    ("Papaya", EATING_OUT_LUNCH),
    ("Bricklayers Arms", ("EatingOut", "Drinks")),
    ("Tufnell Park Tavern", ("EatingOut", "Drinks")),
    ("Barbican Pubs", ("EatingOut", "Drinks")),
    ("CYCLE HIRE", ("Transport", "CycleHire")),
    ("GOOGLE STORAGE", ("Fixed", "Cloud")),
    ("YOU ME SUSHI", EATING_OUT_LUNCH),
    ("BIG FERNAND", EATING_OUT_LUNCH),
    ("SHAKE SHACK", EATING_OUT_LUNCH),
    ("RYANAIR", ("Transport", "Flight")),
    ("BREWDOG", ("EatingOut", "Drinks")),
    ("WASABI", EATING_OUT_LUNCH),
    ("PATTY AND BUN", ("EatingOut", "")),
    ("COCO DI MAMA", EATING_OUT_LUNCH),
    ("Kimchee To Go", EATING_OUT_LUNCH),
    ("COCO DI MAMA", EATING_OUT_LUNCH),
    ("DATAQUEST", ("Education", "Course")),
    ("International Debit Card .* Fee", ("Other", "StupidFee")),
    ("Cancer research", ("Charity", "")),
    ("Greater Anglia", ("Transport", "Train")),
    ("The Flintlock", EATING_OUT_DRINKS),
    ("The Two Brewers", EATING_OUT_DRINKS),
    ("The Marquis of Granby", EATING_OUT_DRINKS),
    ("The Craft Beer Co", EATING_OUT_DRINKS),
    ("COLLEGE ARMS", EATING_OUT_DRINKS),
    ("VIRGIN MEDIA", ("Fixed", "Internet")),
    ("T K MAXX", ("Shopping", "Clothing")),
    ("ZARA", ("Shopping", "Clothing")),
    ("Wok to Walk", EATING_OUT_LUNCH),
]


def get_category_from_merchant(merchant):
    for merchant_regex, category in merchant_to_category_mapping:
        if re.search(merchant_regex, merchant, re.IGNORECASE):
            return category
    return None


def fill_internal_transaction_details(transactions_row):
    def is_monzo_jakub_topup():
        return transactions_row[OUTPUT_COLUMN_ACCOUNT_NAME] == 'MonzoJakub' and \
            transactions_row[OUTPUT_COLUMN_AMOUNT_GBP] >= 100 and \
            transactions_row[OUTPUT_COLUMN_MERCHANT] == ''

    def is_lloyds_to_monzo_jakub():
        return transactions_row[OUTPUT_COLUMN_ACCOUNT_NAME] == 'LloydsMaster' and \
            transactions_row[OUTPUT_COLUMN_AMOUNT_GBP] <= -100 and \
            'MONZO' in transactions_row[OUTPUT_COLUMN_MERCHANT]

    def is_monzo_maja_topup():
        return transactions_row[OUTPUT_COLUMN_ACCOUNT_NAME] == 'MonzoMaja' and \
            transactions_row[OUTPUT_COLUMN_AMOUNT_GBP] >= 100 and \
            transactions_row[OUTPUT_COLUMN_MERCHANT] == ''

    def is_lloyds_to_monzo_maja():
        return transactions_row[OUTPUT_COLUMN_ACCOUNT_NAME] == 'LloydsMaja' and \
            transactions_row[OUTPUT_COLUMN_AMOUNT_GBP] <= -100 and \
            'MONZO' in transactions_row[OUTPUT_COLUMN_MERCHANT]

    if is_monzo_jakub_topup():
        transactions_row[OUTPUT_COLUMN_CATEGORY] = 'Internal'
        transactions_row[OUTPUT_COLUMN_MERCHANT] = 'LloydsMaster'
        transactions_row[OUTPUT_COLUMN_NOTE] = ''
        return True
    if is_lloyds_to_monzo_jakub():
        transactions_row[OUTPUT_COLUMN_CATEGORY] = 'Internal'
        transactions_row[OUTPUT_COLUMN_MERCHANT] = 'MonzoJakub'
        transactions_row[OUTPUT_COLUMN_NOTE] = ''
        return True
    elif is_monzo_maja_topup():
        transactions_row[OUTPUT_COLUMN_CATEGORY] = 'Internal'
        transactions_row[OUTPUT_COLUMN_MERCHANT] = 'LloydsMaja'
        transactions_row[OUTPUT_COLUMN_NOTE] = ''
        return True
    if is_lloyds_to_monzo_maja():
        transactions_row[OUTPUT_COLUMN_CATEGORY] = 'Internal'
        transactions_row[OUTPUT_COLUMN_MERCHANT] = 'MonzoMaja'
        transactions_row[OUTPUT_COLUMN_NOTE] = ''
        return True

    #TODO: lloydsmaster -> lloydsmaja 1500 kazdy miesionc
    # lloydsmaja -> lloyds maja monthly saver 400 kazdy miesionc
    # OUTPUT:
    #   02/06/17	LloydsMaja	-£400 		Internal	Investment		LloydsMonthlySaverMaja
    #   03/07/17	LloydsMonthlySaverMaja	 £400 		Investment			LloydsMaja
    # Amex payment

    return False


def fill_categories(mapped_transactions):
    categories_filled_count = 0
    for transactions_row in mapped_transactions:
        categories = get_category_from_merchant(transactions_row[7])
        if categories is not None:
            transactions_row[OUTPUT_COLUMN_CATEGORY] = categories[0]
            transactions_row[OUTPUT_COLUMN_SUB_CATEGORY] = categories[1]
            categories_filled_count += 1
        else:
            filled_internal = fill_internal_transaction_details(transactions_row)
            if filled_internal:
                categories_filled_count += 1

    print("INFO: filled categories for {} transactions out of {}".format(
        categories_filled_count, len(mapped_transactions)))


def write_output(output):
    with open('output.csv', 'w', newline='') as f:
        f.write('Date\tAccount\tAmount GBP\tAmount CZK\tCategory\tSub-category\tNote\tMerchant\tHoliday\tBusiness\n')

        writer = csv.writer(f, delimiter='\t')
        writer.writerows(output)


lloyds_maja_transactions = read_bank_statement('input/**/lloyds_maja.csv')
output_lloyds_maja = map_lloyds_transactions(lloyds_maja_transactions, 'LloydsMaja')

lloyds_master_transactions = read_bank_statement('input/**/lloyds_master.csv')
output_lloyds_master = map_lloyds_transactions(lloyds_master_transactions, 'LloydsMaster')

tsb_transactions = read_bank_statement('input/**/tsb.csv')
output_tsb = map_lloyds_transactions(tsb_transactions, 'TSBJakub')

monzo_maja_transactions = read_bank_statement('input/**/monzo_maja.csv')
output_monzo_maja = map_monzo_transactions(monzo_maja_transactions, 'MonzoMaja')

monzo_jakub_transactions = read_bank_statement('input/**/monzo_jakub.csv')
output_monzo_jakub = map_monzo_transactions(monzo_jakub_transactions, 'MonzoJakub')

amex_transations = read_bank_statement('input/**/amex.csv')
output_amex = map_amex_transactions(amex_transations)

mapped_transactions = output_lloyds_maja + output_lloyds_master + \
    output_tsb + output_monzo_maja + output_monzo_jakub + output_amex

fill_categories(mapped_transactions)


def get_key(transaction):
    return datetime.datetime.strptime(transaction[OUTPUT_COLUMN_DATE], '%d/%m/%Y')


mapped_transactions.sort(key=get_key)

if len(mapped_transactions) == 0:
    print('ERROR: no transactions found')
else:
    write_output(mapped_transactions)

    print('INFO: written {} transactions to output.csv'.format(len(mapped_transactions)))
