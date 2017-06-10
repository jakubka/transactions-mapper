import csv


def read_bank_statement(file_name):
    input = []
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            input.append(row)
    return input


def map_lloyds_transactions(transactions, account_name):
    output = []
    for input_row in transactions[1:]:
        credit = 0 if input_row[6] == '' else float(input_row[6])
        debit = 0 if input_row[5] == '' else float(input_row[5])

        output_row = [
            input_row[0],
            account_name,
            credit - debit,
            '',
            '',
            '',
            input_row[4],
            input_row[4],
            '',
            '',
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

output = output_lloyds + output_tsb

write_output(output)
