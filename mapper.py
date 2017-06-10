import csv
import datetime


def read_bank_statement(file_name):
    with open(file_name, newline='') as f:
        return list(csv.reader(f))[1:]


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


lloyds_transactions = read_bank_statement('lloyds.csv')
output_lloyds = map_lloyds_transactions(lloyds_transactions, 'LloydsMaja')

tsb_transactions = read_bank_statement('tsb.csv')
output_tsb = map_lloyds_transactions(tsb_transactions, 'TSBJakub')

monzo_transactions = read_bank_statement('monzo.csv')
output_monzo = map_monzo_transactions(monzo_transactions, 'MonzoMaja')

output = output_lloyds + output_tsb + output_monzo

write_output(output)
