import csv

input = []

with open('lloyds.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        input.append(row)


# Transaction Date,   Transaction Type,   Sort Code,   Account Number,   Transaction Description,   Debit Amount,   Credit Amount,   Balance,
# Date, Account,  Amount GBP ,  Amount CZK , Category, Sub-category, Note, Merchant, Holiday, Business

output = []

for input_row in input[1:]:
  # mapping
  credit = 0 if input_row[6] == '' else float(input_row[6])
  debit = 0 if input_row[5] == '' else float(input_row[5])

  output_row = [
    input_row[0],
    'LloydsMaja',
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

with open('output.csv', 'w', newline='') as f:
    f.write('Date\tAccount\tAmount GBP\tAmount CZK\tCategory\tSub-category\tNote\tMerchant\tHoliday\tBusiness\n')

    writer = csv.writer(f, delimiter='\t')
    writer.writerows(output)
