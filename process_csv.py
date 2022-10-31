files = {
    "customer.csv" : "customer_processed.csv",
    "lineitem.csv" : "lineitem_processed.csv",
    "nation.csv" : "nation_processed.csv",
    "orders.csv" : "orders_processed.csv",
    "part.csv" : "part_processed.csv",
    "partsupp.csv" : "partsupp_processed.csv",
    "region.csv" : "region_processed.csv",
    "supplier.csv" : "supplier_processed.csv",
}

# remove the last "\\|" in every row
for key, value in files.items():
    with open(key, 'r') as r, open(value, 'w') as w:    
        for num, line in enumerate(r):  
            newline = line[:-2] + "\n" if "\n" in line else line[:-1]             
            w.write(newline)