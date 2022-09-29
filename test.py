SUM=0
SIZE=0
with open("tsv_files/data.tsv") as f:
    lines=f.readlines()
    for line in lines:
        rating=float(line.split("\t")[1])
        voteN=int(line.split("\t")[2])
        SIZE+=1
    print(SIZE)
    print(SUM/SIZE)

