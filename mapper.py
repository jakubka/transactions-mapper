import csv
import datetime
import os
import re


def read_bank_statement(file_name):
    if not os.path.isfile(file_name):
        print('INFO: {} file does not exist, ignoring it'.format(file_name))
        return []

    with open(file_name, newline='') as f:
        transactions = list(csv.reader(f))[1:]
        print('INFO: loaded {} transactions from {}'.format(len(transactions), file_name))
        return transactions


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
            float(input_row[3].replace('£', '')),  # Amount GBP
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


merchant_to_category_mapping = [
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
    ("leon", ("EatingOut", "Lunch")),
    ("pod", ("EatingOut", "Lunch")),
    ("MICROSOFT   \*ONEDR", ("Fixed", "Cloud")),
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
    ("Papaya", ("EatingOut", "Lunch")),
    ("Bricklayers Arms", ("EatingOut", "Drinks")),
    ("Tufnell Park Tavern", ("EatingOut", "Drinks")),
    ("Barbican Pubs", ("EatingOut", "Drinks")),
    ("CYCLE HIRE", ("Transport", "CycleHire")),
    ("GOOGLE STORAGE", ("Fixed", "Cloud")),
    ("YOU ME SUSHI", ("EatingOut", "Lunch")),
    ("BIG FERNAND", ("EatingOut", "Lunch")),
    ("SHAKE SHACK", ("EatingOut", "Lunch")),
    ("RYANAIR", ("Transport", "Flight")),
    ("BREWDOG", ("EatingOut", "Drinks")),
    ("WASABI", ("EatingOut", "Lunch")),
    ("PATTY AND BUN", ("EatingOut", "")),



]


def get_category_from_merchant(merchant):
    for merchant_regex, category in merchant_to_category_mapping:
        if re.search(merchant_regex, merchant, re.IGNORECASE):
            return category
    return None


def fill_categories(mapped_transactions):
    categories_filled_count = 0
    for transactions_row in mapped_transactions:
        categories = get_category_from_merchant(transactions_row[7])
        if categories is not None:
            transactions_row[4] = categories[0]
            transactions_row[5] = categories[1]
            categories_filled_count += 1

    print("INFO: filled categories for {} transactions out of {}".format(
        categories_filled_count, len(mapped_transactions)))


def write_output(output):
    with open('output.csv', 'w', newline='') as f:
        f.write('Date\tAccount\tAmount GBP\tAmount CZK\tCategory\tSub-category\tNote\tMerchant\tHoliday\tBusiness\n')

        writer = csv.writer(f, delimiter='\t')
        writer.writerows(output)


lloyds_maja_transactions = read_bank_statement('lloyds_maja.csv')
output_lloyds_maja = map_lloyds_transactions(lloyds_maja_transactions, 'LloydsMaja')

lloyds_master_transactions = read_bank_statement('lloyds_master.csv')
output_lloyds_master = map_lloyds_transactions(lloyds_master_transactions, 'LloydsMaster')

tsb_transactions = read_bank_statement('tsb.csv')
output_tsb = map_lloyds_transactions(tsb_transactions, 'TSBJakub')

monzo_maja_transactions = read_bank_statement('monzo_maja.csv')
output_monzo_maja = map_monzo_transactions(monzo_maja_transactions, 'MonzoMaja')

monzo_jakub_transactions = read_bank_statement('monzo_jakub.csv')
output_monzo_jakub = map_monzo_transactions(monzo_jakub_transactions, 'MonzoJakub')

amex_transations = read_bank_statement('amex.csv')
output_amex = map_amex_transactions(amex_transations)

mapped_transactions = output_lloyds_maja + output_lloyds_master + \
    output_tsb + output_monzo_maja + output_monzo_jakub + output_amex

fill_categories(mapped_transactions)

if len(mapped_transactions) == 0:
    print('ERROR: no transactions found')
else:
    write_output(mapped_transactions)

    print('INFO: written {} transactions to output.csv'.format(len(mapped_transactions)))
