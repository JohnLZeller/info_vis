import json
import csv
import requests
from datetime import datetime


def generateMapData_fromNASAAmountsCSV():
    # Grab data from csv
    data = []
    with open('map/a.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                data.append(r)
    data.pop(0)  # remove header

    # Count dollars and contracts
    dists = {}
    for d in data:
        amt = float(d[2])
        if dists.get(d[1]):
                dists[d[1]]['amt'] += amt
                dists[d[1]]['contracts'] += 1
        else:
                dists[d[1]] = {'amt': amt, 'contracts': 1}

    # Print what we have so far
    for k, v in dists.iteritems():
        print "{0} - {1}".format(k, v)

    # Generate maximum and minumum dollar amounts
    max = 0
    for k, v in dists.iteritems():
        if v['district'] == '':
                pass
        elif v['amt'] > max:
                max = v['amt']

    min = max
    for k, v in dists.iteritems():
        if v['district'] == '':
                pass
        elif v['amt'] < min:
                max = v['amt']

    # Calculate amount ratio
    for k, v in dists.iteritems():
        v['ratio'] = ((-1.00 * min) + v['amt'])/((-1.00 * min) + max)
        v['ratio'] = round(v['ratio'], 4)

    # Generate maximum and minimum numbers of contracts - can't have negative contracts
    max = 0
    for k, v in dists.iteritems():
        if v['district'] == '':
                pass
        elif v['contracts'] > max:
                max = v['contracts']
    
    # Calculate number of contracts ratio
    for k, v in dists.iteritems():
        v['cont-ratio'] = float(v['contracts']) / max
        v['cont-ratio'] = round(v['cont-ratio'], 4)

    # Output to file in tsv format
    out = []
    for k, v in dists.iteritems():
        out.append((k, v['amt'], v['ratio'], v['contracts'], v['cont-ratio']))

    s = "district\tamt\tamt-ratio\tcontracts\tcont-ratio\n"
    for item in out:
        s += "{0}\t{1}\t{2}\t{3}\t{4}\n".format(item[0], item[1], item[2], item[3], item[4])

    f = open('map/contracts-amounts.tsv', 'wb')
    f.write(s)
    f.close()


def generateCorrelationData_fromNASAAmountsCSV():
    # Grab data from csv
    data = []
    with open('companies/b.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                data.append(r)
    data.pop(0)  # remove header

    # Count dollars and contracts by company
    comps = {}
    for d in data:
        district = d[1]
        numEmps = d[3]
        amt = float(d[4])
        if comps.get(d[0]):
                comps[d[0]]['amt'] += amt
                comps[d[0]]['contracts'] += 1
                if district not in comps[d[0]]['district']:
                    comps[d[0]]['district'].append(district)
        else:
                comps[d[0]] = {'amt': amt, 'employees': numEmps, 'contracts': 1, 'district': [district]}

    # Print what we have so far
    for k, v in comps.iteritems():
        print "{0} - {1}".format(k, v)

    # Output big dataset to file in tsv format
    out = []
    for k, v in comps.iteritems():
        out.append((k, v['contracts'], v['amt'], v['employees'], v['district']))

    s = "company\tcontracts\tamt\temployees\tdistrict\n"
    for item in out:
        s += "{0}\t{1}\t{2}\t{3}\t{4}\n".format(item[0], item[1], item[2], item[3], item[4])

    f = open('companies/byCompany-contracts-amounts-employees.tsv', 'wb')
    f.write(s)
    f.close()

    # Output dataset for correlation only to file in tsv format
    out = []
    for k, v in comps.iteritems():
        out.append((v['contracts'], v['employees']))

    s = "contracts\temployees\n"
    for item in out:
        s += "{0}\t{1}\n".format(item[0], item[1])

    f = open('companies/byCompany-correlation.tsv', 'wb')
    f.write(s)
    f.close()

    # Output dataset for company amount only to file in tsv format
    out = []
    for k, v in comps.iteritems():
        out.append((k, v['amt']))

    s = "company\tamt\n"
    for item in out:
        s += "{0}\t{1}\n".format(item[0], item[1])

    f = open('companies/byCompany-amounts.tsv', 'wb')
    f.write(s)
    f.close()


def generateAllData_fromNASABeforeCSV_byDistrict():
    # Find Missing Districts
    findMissingDistricts()

    # Grab data from csv
    data = []
    with open('NASA-Before-Fixed.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                data.append(r)
    data.pop(0)  # remove header

    # Read in FIPS state codes and put them in a dict
    stateCodes = []
    with open('stateFips.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                stateCodes.append(r)
    stateCodes.pop(0)  # remove header
    states = {}
    for s in stateCodes:
        states[s[1]] = s[0]

    # Put into nicer format
    rows = []
    for d in data:
        if d[5] == 'USA':
            rows.append({'company': d[0], 'state': d[4], 'stateFIPS': states[d[4]], 'district': str(d[6]), 
                     'employees': d[8], 'amt': float(d[12]), 'effectiveDate': d[20],
                     'ultimateCompletionDate': d[22], 'fundedThroughDate': d[23]})
        else:
            rows.append({'company': d[0], 'state': d[4], 'stateFIPS': 0, 'district': str(d[6]), 
                     'employees': d[8], 'amt': float(d[12]), 'effectiveDate': d[20],
                     'ultimateCompletionDate': d[22], 'fundedThroughDate': d[23]})

    # Create an overallDistrict code for each row
    for r in rows:
        if int(r['district']) < 0:
            r['masterDistrict'] = r['district']
        else:
            districtPadded = str(r['district'])
            if int(districtPadded) < 10:
                districtPadded = '0' + districtPadded
            r['masterDistrict'] = str(r['stateFIPS']) + districtPadded

    # Organize into a dict of districts, each with a list of line items
    dists = {}
    for r in rows:
        if dists.get(r['masterDistrict']):
            dists[r['masterDistrict']]['rows'].append(r)
        else:
            dists[r['masterDistrict']] = {'rows': [r], 'contracts': 0, 'amt': 0.00,
                                    'contract-ratio': 0.00, 'amt-ratio': 0.00,
                                    'fundingDuration': 0, 'ultimateDuration': 0,
                                    'ultimateDurationRatio': 0.0, 'fundedDurationRatio': 0.0}

    # Find the number of contracts and amounts by district
    for d, v in dists.iteritems():
        v['contracts'] = len(v['rows'])
        for r in v['rows']:
            v['amt'] += r['amt']

    # Print what we have so far
    for d, v in dists.iteritems():
        print "{0}: ${1} and {2} contracts".format(d, v['amt'], v['contracts'])

    # Calculate max contracts and min/max amts
    maxCont = 0
    maxAmt = 0
    for d, v in dists.iteritems():
        if (v['contracts'] > maxCont) and (d >= -1):  # Include outside the US, but don't include unknown
            maxCont = v['contracts']
        if (v['amt'] > maxAmt) and (d >= -1):  # Include outside the US, but don't include unknown
            maxAmt = v['amt']
    minAmt = 0
    for d, v in dists.iteritems():
        if (v['amt'] < minAmt) and (d >= -1):  # Include outside the US, but don't include unknown
            minAmt = v['amt']

    # Calculate contract and amt ratios
    for d, v in dists.iteritems():
        v['contract-ratio'] = float(v['contracts']) / maxCont
        v['contract-ratio'] = round(v['contract-ratio'], 4)
        v['amt-ratio'] = (abs(minAmt) + float(v['amt'])) / (abs(minAmt) + maxAmt)
        v['amt-ratio'] = round(v['amt-ratio'], 4)

    # Print what we have so far
    for d, v in dists.iteritems():
        print "{0}: {1} amt-ratio and {2} cont-ratio".format(d, v['amt-ratio'], v['contract-ratio'])

    # Calculate fundingDuration and ultimateDuration for each row
    for d, v in dists.iteritems():
        for r in v['rows']:
            if not r['effectiveDate']:
                # There should be one, so error
                r['fundingDuration'] = None
                r['ultimateDuration'] = None
            else:
                effectiveDate = datetime.strptime(r['effectiveDate'], "%Y-%m-%d %H:%M:%S")

                # Check ultimateCompletionDate existence
                if r['ultimateCompletionDate']:
                    ultimateCompletionDate = datetime.strptime(r['ultimateCompletionDate'], "%Y-%m-%d %H:%M:%S")
                else:
                    ultimateCompletionDate = effectiveDate

                # Check fundedThroughDate existence
                if r['fundedThroughDate']:
                    fundedThroughDate = datetime.strptime(r['fundedThroughDate'], "%Y-%m-%d %H:%M:%S")
                else:
                    fundedThroughDate = effectiveDate

                # Calculate durations
                r['fundingDuration'] = (fundedThroughDate - effectiveDate).days
                r['ultimateDuration'] = (fundedThroughDate - ultimateCompletionDate).days

    # Average contract durations by district
    for d, v in dists.iteritems():
        fundingDurationTotal = 0.0
        ultimateDurationTotal = 0.0
        for r in v['rows']:
            fundingDurationTotal += float(r['fundingDuration'])
            ultimateDurationTotal += float(r['ultimateDuration'])
        v['fundingDuration'] = float(fundingDurationTotal) / float(v['contracts'])
        v['fundingDuration'] = int(v['fundingDuration'])
        v['ultimateDuration'] = float(ultimateDurationTotal) / float(v['contracts'])
        v['ultimateDuration'] = int(v['ultimateDuration'])

    # Print what we have so far
    for d, v in dists.iteritems():
        print "{0}: {1} fundingDuration and {2} ultimateDuration".format(d, v['fundingDuration'], v['ultimateDuration'])

    # Calculate duration ratios
    maxUlt = 0
    maxFun = 0
    for d, v in dists.iteritems():
        if (v['fundingDuration'] > maxFun) and (d >= 0):  # Include outside the US, but don't include unknown
            maxFun = v['fundingDuration']
        if (v['ultimateDuration'] > maxUlt) and (d >= 0):  # Include outside the US, but don't include unknown
            maxUlt = v['ultimateDuration']
    for d, v in dists.iteritems():
        v['ultimateDurationRatio'] = float(v['ultimateDuration']) / maxUlt
        v['ultimateDurationRatio'] = round(v['ultimateDurationRatio'], 4)
        v['fundingDurationRatio'] = float(v['fundingDuration']) / maxFun
        v['fundingDurationRatio'] = round(v['fundingDurationRatio'], 4)

    # Print what we have so far
    for d, v in dists.iteritems():
        print "{0}: {1} fundingDuration and {2} ultimateDuration".format(d, v['fundingDurationRatio'], v['ultimateDurationRatio'])

    # Output total needed map data to a tsv
    s = "district\tamt\tamtRatio\tcontracts\tcontRatio\tavgFundingDuration\tavgUltimateDuration\tfundingDurationRatio\tultimateDurationRatio\n"
    for d, v in dists.iteritems():
        s += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n".format(d, v['amt'], v['amt-ratio'], v['contracts'], v['contract-ratio'], v['fundingDuration'], v['ultimateDuration'], v['fundingDurationRatio'], v['ultimateDurationRatio'])
    
    f = open('map/byDistrict/MAP-contracts-amounts-durations.tsv', 'wb')
    f.write(s)
    f.close()

    # Output total MINIMUM needed map data to a tsv
    s = "district\tamt\tamtRatio\tcontracts\tcontRatio\tfundingDuration\tfundingDurationRatio\n"
    for d, v in dists.iteritems():
        s += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(d, v['amt'], v['amt-ratio'], v['contracts'], v['contract-ratio'], v['fundingDuration'], v['fundingDurationRatio'])
    
    f = open('map/byDistrict/MAP-MINIMUM-contracts-amounts-durations.tsv', 'wb')
    f.write(s)
    f.close()

    # Output just data for contract ratios
    s = "district\tcontRatio\n"
    for d, v in dists.iteritems():
        s += "{0}\t{1}\n".format(d, v['contract-ratio'])

    f = open('map/byDistrict/MAP-contractRatios.tsv', 'wb')
    f.write(s)
    f.close()

    # Output just data for amount ratios
    s = "district\tamtRatio\n"
    for d, v in dists.iteritems():
        s += "{0}\t{1}\n".format(d, v['amt-ratio'])

    f = open('map/byDistrict/MAP-amountRatios.tsv', 'wb')
    f.write(s)
    f.close()

    # Output just funding duration ratios
    s = "district\tfundingDurationRatio\n"
    for d, v in dists.iteritems():
        s += "{0}\t{1}\n".format(d, v['fundingDurationRatio'])

    f = open('map/byDistrict/MAP-fundingDurationRatios.tsv', 'wb')
    f.write(s)
    f.close()


def generateAllData_fromNASABeforeCSV_byState():
    # Find Missing Districts
    findMissingDistricts()

    # Grab data from csv
    data = []
    with open('NASA-Before-Fixed.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                data.append(r)
    data.pop(0)  # remove header

    # Read in FIPS state codes and put them in a dict
    stateCodes = []
    with open('stateFips.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                stateCodes.append(r)
    stateCodes.pop(0)  # remove header
    stateFIPS = {}
    for s in stateCodes:
        stateFIPS[s[1]] = s[0]

    # Put into nicer format
    rows = []
    for d in data:
        if d[5] == 'USA':
            rows.append({'company': d[0], 'state': d[4], 'stateFIPS': stateFIPS[d[4]], 'district': str(d[6]), 
                     'employees': d[8], 'amt': float(d[12]), 'effectiveDate': d[20],
                     'ultimateCompletionDate': d[22], 'fundedThroughDate': d[23]})
        else:
            rows.append({'company': d[0], 'state': d[4], 'stateFIPS': 0, 'district': str(d[6]), 
                     'employees': d[8], 'amt': float(d[12]), 'effectiveDate': d[20],
                     'ultimateCompletionDate': d[22], 'fundedThroughDate': d[23]})

    # Organize into a dict of states, each with a list of line items
    states = {}
    for r in rows:
        if states.get(r['stateFIPS']):
            states[r['stateFIPS']]['rows'].append(r)
        else:
            states[r['stateFIPS']] = {'rows': [r], 'contracts': 0, 'amt': 0.00,
                                      'contract-ratio': 0.00, 'amt-ratio': 0.00,
                                      'fundingDuration': 0, 'ultimateDuration': 0,
                                      'ultimateDurationRatio': 0.0, 'fundedDurationRatio': 0.0}

    # Find the number of contracts and amounts by state
    for s, v in states.iteritems():
        v['contracts'] = len(v['rows'])
        for r in v['rows']:
            v['amt'] += r['amt']

    # Print what we have so far
    for s, v in states.iteritems():
        print "{0}: ${1} and {2} contracts".format(s, v['amt'], v['contracts'])

    # Calculate max contracts and min/max amts
    maxCont = 0
    maxAmt = 0
    for s, v in states.iteritems():
        if (v['contracts'] > maxCont):
            maxCont = v['contracts']
        if (v['amt'] > maxAmt):
            maxAmt = v['amt']
    minAmt = 0
    for s, v in states.iteritems():
        if (v['amt'] < minAmt):
            minAmt = v['amt']

    # Calculate contract and amt ratios
    for s, v in states.iteritems():
        v['contract-ratio'] = float(v['contracts']) / maxCont
        v['contract-ratio'] = round(v['contract-ratio'], 4)
        v['amt-ratio'] = (abs(minAmt) + float(v['amt'])) / (abs(minAmt) + maxAmt)
        v['amt-ratio'] = round(v['amt-ratio'], 4)

    # Print what we have so far
    for s, v in states.iteritems():
        print "{0}: {1} amt-ratio and {2} cont-ratio".format(s, v['amt-ratio'], v['contract-ratio'])

    # Calculate fundingDuration and ultimateDuration for each row
    for s, v in states.iteritems():
        for r in v['rows']:
            if not r['effectiveDate']:
                # There should be one, so error
                r['fundingDuration'] = None
                r['ultimateDuration'] = None
            else:
                effectiveDate = datetime.strptime(r['effectiveDate'], "%Y-%m-%d %H:%M:%S")

                # Check ultimateCompletionDate existence
                if r['ultimateCompletionDate']:
                    ultimateCompletionDate = datetime.strptime(r['ultimateCompletionDate'], "%Y-%m-%d %H:%M:%S")
                else:
                    ultimateCompletionDate = effectiveDate

                # Check fundedThroughDate existence
                if r['fundedThroughDate']:
                    fundedThroughDate = datetime.strptime(r['fundedThroughDate'], "%Y-%m-%d %H:%M:%S")
                else:
                    fundedThroughDate = effectiveDate

                # Calculate durations
                r['fundingDuration'] = (fundedThroughDate - effectiveDate).days
                r['ultimateDuration'] = (fundedThroughDate - ultimateCompletionDate).days

    # Average contract durations by district
    for s, v in states.iteritems():
        fundingDurationTotal = 0.0
        ultimateDurationTotal = 0.0
        for r in v['rows']:
            fundingDurationTotal += float(r['fundingDuration'])
            ultimateDurationTotal += float(r['ultimateDuration'])
        v['fundingDuration'] = float(fundingDurationTotal) / float(v['contracts'])
        v['fundingDuration'] = int(v['fundingDuration'])
        v['ultimateDuration'] = float(ultimateDurationTotal) / float(v['contracts'])
        v['ultimateDuration'] = int(v['ultimateDuration'])

    # Print what we have so far
    for s, v in states.iteritems():
        print "{0}: {1} fundingDuration and {2} ultimateDuration".format(s, v['fundingDuration'], v['ultimateDuration'])

    # Calculate duration ratios
    maxUlt = 0
    maxFun = 0
    for s, v in states.iteritems():
        if (v['fundingDuration'] > maxFun):
            maxFun = v['fundingDuration']
        if (v['ultimateDuration'] > maxUlt):
            maxUlt = v['ultimateDuration']
    for s, v in states.iteritems():
        v['ultimateDurationRatio'] = float(v['ultimateDuration']) / maxUlt
        v['ultimateDurationRatio'] = round(v['ultimateDurationRatio'], 4)
        v['fundingDurationRatio'] = float(v['fundingDuration']) / maxFun
        v['fundingDurationRatio'] = round(v['fundingDurationRatio'], 4)

    # Print what we have so far
    for s, v in states.iteritems():
        print "{0}: {1} fundingDuration and {2} ultimateDuration".format(s, v['fundingDurationRatio'], v['ultimateDurationRatio'])

    # Output total needed map data to a tsv
    string = "state\tamt\tamtRatio\tcontracts\tcontRatio\tavgFundingDuration\tavgUltimateDuration\tfundingDurationRatio\tultimateDurationRatio\n"
    for s, v in states.iteritems():
        string += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n".format(s, v['amt'], v['amt-ratio'], v['contracts'], v['contract-ratio'], v['fundingDuration'], v['ultimateDuration'], v['fundingDurationRatio'], v['ultimateDurationRatio'])
    
    f = open('map/byState/MAP-contracts-amounts-durations.tsv', 'wb')
    f.write(string)
    f.close()

    # Output total MINIMUM needed map data to a tsv
    string = "state\tamt\tamtRatio\tcontracts\tcontRatio\tfundingDuration\tfundingDurationRatio\n"
    for s, v in states.iteritems():
        string += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(s, v['amt'], v['amt-ratio'], v['contracts'], v['contract-ratio'], v['fundingDuration'], v['fundingDurationRatio'])
    
    f = open('map/byState/MAP-MINIMUM-contracts-amounts-durations.tsv', 'wb')
    f.write(string)
    f.close()

    # Output just data for contract ratios
    string = "state\tcontRatio\n"
    for s, v in states.iteritems():
        string += "{0}\t{1}\n".format(s, v['contract-ratio'])

    f = open('map/byState/MAP-contractRatios.tsv', 'wb')
    f.write(string)
    f.close()

    # Output just data for amount ratios
    string = "state\tamtRatio\n"
    for s, v in states.iteritems():
        string += "{0}\t{1}\n".format(s, v['amt-ratio'])

    f = open('map/byState/MAP-amountRatios.tsv', 'wb')
    f.write(string)
    f.close()

    # Output just funding duration ratios
    string = "state\tfundingDurationRatio\n"
    for s, v in states.iteritems():
        string += "{0}\t{1}\n".format(s, v['fundingDurationRatio'])

    f = open('map/byState/MAP-fundingDurationRatios.tsv', 'wb')
    f.write(string)
    f.close()


def generateAllData_fromNASABeforeCSV_byCompany():
    # Find Missing Districts
    findMissingDistricts()

    # Grab data from csv
    data = []
    with open('NASA-Before-Fixed.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                data.append(r)
    data.pop(0)  # remove header

    # Read in FIPS state codes and put them in a dict
    stateCodes = []
    with open('stateFips.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                stateCodes.append(r)
    stateCodes.pop(0)  # remove header
    stateFIPS = {}
    for s in stateCodes:
        stateFIPS[s[1]] = s[0]

    # Put into nicer format
    rows = []
    for d in data:
        if d[5] == 'USA':
            rows.append({'company': d[0], 'state': d[4], 'stateFIPS': stateFIPS[d[4]], 'district': str(d[6]), 
                     'employees': d[8], 'amt': float(d[12]), 'effectiveDate': d[20],
                     'ultimateCompletionDate': d[22], 'fundedThroughDate': d[23]})
        else:
            rows.append({'company': d[0], 'state': d[4], 'stateFIPS': 0, 'district': str(d[6]), 
                     'employees': d[8], 'amt': float(d[12]), 'effectiveDate': d[20],
                     'ultimateCompletionDate': d[22], 'fundedThroughDate': d[23]})

    # Create an overallDistrict code for each row
    for r in rows:
        if int(r['district']) < 0:
            r['masterDistrict'] = r['district']
        else:
            districtPadded = str(r['district'])
            if int(districtPadded) < 10:
                districtPadded = '0' + districtPadded
            r['masterDistrict'] = str(r['stateFIPS']) + districtPadded

    # Organize into a dict of companies, each with a list of line items
    comps = {}
    for r in rows:
        if comps.get(r['company']):
            comps[r['company']]['rows'].append(r)
        else:
            comps[r['company']] = {'rows': [r], 'contracts': 0, 'amt': 0.00,
                                   'contract-ratio': 0.00, 'amt-ratio': 0.00,,
                                   'employees': r['employees'], 'fundingDuration': 0, 
                                   'ultimateDuration': 0, 'fundingDurationRatio': 0, 'ultimateDurationRatio': 0}

    # Find the number of contracts and amounts by company
    for c, v, in comps.iteritems():
        v['contracts'] = len(v['rows'])
        for r in v['rows']:
            v['amt'] += r['amt']

    # Print what we have so far
    for c, v, in comps.iteritems():
        print "{0}: ${1} and {2} contracts".format(c, v['amt'], v['contracts'])

    # Calculate max contracts and min/max amts
    maxCont = 0
    maxAmt = 0
    for c, v, in comps.iteritems():
        if (v['contracts'] > maxCont):
            maxCont = v['contracts']
        if (v['amt'] > maxAmt):
            maxAmt = v['amt']
    minAmt = 0
    for c, v, in comps.iteritems():
        if (v['amt'] < minAmt):
            minAmt = v['amt']

    # Calculate contract and amt ratios
    for c, v, in comps.iteritems():
        v['contract-ratio'] = float(v['contracts']) / maxCont
        v['contract-ratio'] = round(v['contract-ratio'], 4)
        v['amt-ratio'] = (abs(minAmt) + float(v['amt'])) / (abs(minAmt) + maxAmt)
        v['amt-ratio'] = round(v['amt-ratio'], 4)

    # Print what we have so far
    for c, v, in comps.iteritems():
        print "{0}: {1} amt-ratio and {2} cont-ratio".format(c, v['amt-ratio'], v['contract-ratio'])

    # Calculate fundingDuration and ultimateDuration for each row
    for c, v, in comps.iteritems():
        for r in v['rows']:
            if not r['effectiveDate']:
                # There should be one, so error
                r['fundingDuration'] = None
                r['ultimateDuration'] = None
            else:
                effectiveDate = datetime.strptime(r['effectiveDate'], "%Y-%m-%d %H:%M:%S")

                # Check ultimateCompletionDate existence
                if r['ultimateCompletionDate']:
                    ultimateCompletionDate = datetime.strptime(r['ultimateCompletionDate'], "%Y-%m-%d %H:%M:%S")
                else:
                    ultimateCompletionDate = effectiveDate

                # Check fundedThroughDate existence
                if r['fundedThroughDate']:
                    fundedThroughDate = datetime.strptime(r['fundedThroughDate'], "%Y-%m-%d %H:%M:%S")
                else:
                    fundedThroughDate = effectiveDate

                # Calculate durations
                r['fundingDuration'] = (fundedThroughDate - effectiveDate).days
                r['ultimateDuration'] = (fundedThroughDate - ultimateCompletionDate).days

    # Average contract durations by company
    for c, v, in comps.iteritems():
        fundingDurationTotal = 0.0
        ultimateDurationTotal = 0.0
        for r in v['rows']:
            fundingDurationTotal += float(r['fundingDuration'])
            ultimateDurationTotal += float(r['ultimateDuration'])
        v['fundingDuration'] = float(fundingDurationTotal) / float(v['contracts'])
        v['fundingDuration'] = int(v['fundingDuration'])
        v['ultimateDuration'] = float(ultimateDurationTotal) / float(v['contracts'])
        v['ultimateDuration'] = int(v['ultimateDuration'])

    # Print what we have so far
    for c, v, in comps.iteritems():
        print "{0}: {1} fundingDuration and {2} ultimateDuration".format(c, v['fundingDuration'], v['ultimateDuration'])

    # Calculate duration ratios
    maxUlt = 0
    maxFun = 0
    for c, v in comps.iteritems():
        if (v['fundingDuration'] > maxFun):
            maxFun = v['fundingDuration']
        if (v['ultimateDuration'] > maxUlt):
            maxUlt = v['ultimateDuration']
    for c, v in comps.iteritems():
        v['ultimateDurationRatio'] = float(v['ultimateDuration']) / maxUlt
        v['ultimateDurationRatio'] = round(v['ultimateDurationRatio'], 4)
        v['fundingDurationRatio'] = float(v['fundingDuration']) / maxFun
        v['fundingDurationRatio'] = round(v['fundingDurationRatio'], 4)

    # Print what we have so far
    for c, v in comps.iteritems():
        print "{0}: {1} fundingDuration and {2} ultimateDuration".format(c, v['fundingDurationRatio'], v['ultimateDurationRatio'])

    # Make sure we've counted employees
    for c, v in comps.iteritems():
        for r in v['rows']:
            if v['employees'] < r['employees']:
                v['employees'] = r['employees']

    # Output total needed company data to a tsv
    string = "company\tamt\tamtRatio\tcontracts\tcontRatio\temployees\tavgFundingDuration\tavgUltimateDuration\tfundingDurationRatio\tultimateDurationRatio\n"
    for c, v, in comps.iteritems():
        string += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n".format(c, v['amt'], v['amt-ratio'], v['contracts'], v['contract-ratio'], v['employees'], v['fundingDuration'], v['ultimateDuration'], v['fundingDurationRatio'], v['ultimateDurationRatio'])

    f = open('byCompany/COMPANY-contracts-amounts-durations.tsv', 'wb')
    f.write(string)
    f.close()

    # Output total MINIMUM needed company data to a tsv
    string = "company\tamt\tamtRatio\tcontracts\tcontRatio\temployees\n"
    for c, v, in comps.iteritems():
        string += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(c, v['amt'], v['amt-ratio'], v['contracts'], v['contract-ratio'], v['employees'])

    f = open('byCompany/COMPANY-MINIMUM-contracts-amounts-durations.tsv', 'wb')
    f.write(string)
    f.close()

    # Output just data for contracts vs employees
    string = "contracts\temployees\n"
    for c, v, in comps.iteritems():
        string += "{0}\t{1}\n".format(v['contracts'], v['employees'])

    f = open('byCompany/COMPANY-contractsVSemployees.tsv', 'wb')
    f.write(string)
    f.close()

    # Output just data for total value of contracts
    string = "company\tamt\n"
    for c, v, in comps.iteritems():
        string += "{0}\t{1}\n".format(c, v['amt'])

    f = open('byCompany/COMPANY-amounts.tsv', 'wb')
    f.write(string)
    f.close()

    # Output just data for total contracts
    string = "company\tcontracts\n"
    for c, v, in comps.iteritems():
        string += "{0}\t{1}\n".format(c, v['contracts'])

    f = open('byCompany/COMPANY-contracts.tsv', 'wb')
    f.write(string)
    f.close()


def findMissingDistricts():
    preUrl = "http://nominatim.openstreetmap.org/search?format=json&q="

    # Grab data from csv
    data = []
    with open('NASA-Before.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
                data.append(r)
    data.pop(0)  # remove header

    # To make things easier, let's make all districts into ints
    for d in data:
        if d[6]:
            d[6] = int(d[6])

    # Check for missing districts, mark non-USA, call openstreetmap
    for d in data:
        district = d[6]
        country = d[5]
        if not district:
            if country == 'USA':
                # Build the request URL with query
                reqURL = preUrl
                addr = d[1]
                zipcode = d[2]
                city = d[3]
                state = d[4]
                query = addr + ' ' + city + ' ' + state + ' ' + zipcode
                query = '+'.join(query.split(' '))
                reqURL += query

                # Make the request
                r = requests.get(reqURL)
                d[6] = json.dumps(r.json())
            else:
                d[6] = -1  # Outside of USA, set district to -1

    # Check results, and extract lat/lon
    for d in data:
        district = d[6]
        if type(district) == type(str()):  # Only our data should show
            district = json.loads(district)
            result = []
            for r in district:
                result.append({'lat': r['lat'], 'lon': r['lon']})
            d[6] = json.dumps(result)

    # Call Open Congress API to find districts
    preUrl = "https://congress.api.sunlightfoundation.com/districts/locate?"
    apiKey = "&apikey=578f15b9d3a44ebb8c829860d609bba8"

    for d in data:
        district = d[6]
        if type(district) == type(str()):  # Only our data should show
            district = json.loads(district)
            result = []
            if len(district) == 0:
                d[6] = -2
            else:
                for idx, coordinates in enumerate(district):
                    # Build the request URL with query
                    reqURL = preUrl
                    lat = coordinates['lat']
                    lon = coordinates['lon']
                    query = "latitude={0}&longitude={1}".format(lat, lon)
                    reqURL += '+'.join(query.split(' '))
                    reqURL += apiKey

                    # Make the request
                    r = requests.get(reqURL)
                    result.append(r.json())
                d[6] = json.dumps(result)

    # Check results, and extract district
    for d in data:
        district = d[6]
        if type(district) == type(str()):  # Only our data should show
            district = json.loads(district)
            result = []
            for r in district:
                if r['count'] > 0:
                    try:
                        result.append(r['results'][0]['district'])
                    except Exception as e:
                        print "ERROR! " + e
            d[6] = json.dumps(result)

    # Finally, find the results with multiple districts and decide on those
    for d in data:
        district = d[6]
        if type(district) == type(str()):  # Only our data should show
            district = json.loads(district)
            if len(district) == 1:
                d[6] = district[0]
            elif len(district) == 0:
                d[6] = -2
            else:
                # Count uniques
                uniques = {}
                for i in district:
                    if uniques.get(i):
                        uniques[i] += 1
                    else:
                        uniques[i] = 1

                # If all the same
                if len(uniques.keys()) == 1:
                    d[6] = uniques.keys()[0]
                else:
                    # If we reach this point, then we need to just make a judgement call.. we're going with whatever shows up the most
                    highest = (0, 0)
                    for k, v in uniques.iteritems():
                        if v > highest[1]:
                            highest = (k, v)
                    d[6] = highest[0]

    # To make things easier, make all the districts into strings again
    for d in data:
        if d[6]:
            d[6] = str(d[6])

    s = "vendorName,streetAddress,ZIPCode,city,state,countryCode,congressionalDistrictCode,annualRevenue,"
    s += "numberOfEmployees,PIID,modNumber,transactionNumber,obligatedAmount,majorProgramCode,mainAccountCode,"
    s += "placeOfPerformanceZIPCode,placeOfPerformanceCongressionalDistrict,placeOfPerformanceCountryCode,"
    s += "placeOfPerformanceStateCode,signedDate,effectiveDate,currentCompletionDate,ultimateCompletionDate,"
    s += "fundedThroughDate,principalNAICSCode,countryOfOrigin,placeOfManufacture\n"
    for d in data:
        s += "{0},{1},{2},{3},{4},{5},{6},{7},{8},".format(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8])
        s += "{9},{10},{11},{12},{13},{14},{15},".format(d[9],d[10],d[11],d[12],d[13],d[14],d[15])
        s += "{16},{17},{18},{19},{20},{21},{22},".format(d[16],d[17],d[18],d[19],d[20],d[21],d[22])
        s += "{23},{24},{25},{26},\n".format(d[23],d[24],d[25],d[26])

    f = open('NASA-Before-Fixed.csv', 'wb')
    f.write(s)
    f.close()


