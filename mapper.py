import csv
import datetime
import os


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

output = output_lloyds_maja + output_lloyds_master + output_tsb + output_monzo_maja + output_monzo_jakub

if len(output) == 0:
    print('ERROR: no transactions found')
else:
    write_output(output)

    print('INFO: written {} transactions to output.csv'.format(len(output)))
