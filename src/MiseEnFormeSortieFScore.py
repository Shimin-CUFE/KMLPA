def MiseEnFormeSortie(pathResult, pathTransformed):
    output = open(pathResult, "r")
    com = {}
    for indx, line in enumerate(output):
        if indx > 5:
            line = line.rstrip()

            fields = line.split("\t")

            if fields[1] in com.keys():
                com[fields[1]].append(fields[0])
            else:
                com[fields[1]] = [fields[0]]

    outputFinal = open(pathTransformed, "w")
    for l in com.itervalues():
        for i in l:
            outputFinal.write(str(i).rstrip('\n') + '\t')
        outputFinal.write('\n')
