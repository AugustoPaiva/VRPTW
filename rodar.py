# -*- coding: utf-8 -*-
# sample_C204.py

import random
from core import gaVRPTW


def main():
    random.seed(64)

    instName = 'C101'

    unitCost = 8.0
    initCost = 100.0
    waitCost = 1.0
    #delayCost = 1.5

    indSize = 100
    popSize = 80
    cxPb = 0.85
    mutPb = 0.1
    NGen = 100

    #exportCSV = True

    gaVRPTW(
        instName=instName,
        unitCost=unitCost,
        initCost=initCost,
        waitCost=waitCost,
        #delayCost=delayCost,
        indSize=indSize,
        popSize=popSize,
        cxPb=cxPb,
        mutPb=mutPb,
        NGen=NGen,
        #exportCSV=exportCSV
    )


if __name__ == '__main__':
    main()
