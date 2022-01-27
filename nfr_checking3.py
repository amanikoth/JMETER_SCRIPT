import argparse
import json
import numpy as np
import os
import pandas as pd
import sys
from  itertools import chain

"""
"""
def load_project_file(filename):
  #
  #   Verify that the project json file exists.
  #
  if not os.path.isfile(filename):
    print("Project file[{0}] cannot be found".format(filename))
    sys.exit(-1)
  
  #
  #   Open the project file and load structure. If all goes well return the dictionary of the loaded data
  #   for the project.
  #
  with open(filename) as json_file:
    try:
      json_data = json.load(json_file)
      return json_data
    
    except ValueError as err:
      print("ERROR loading JSON file [{0}] : [{1}]".format(filename, str(err)))
      sys.exit(-1)




"""
"""
def load_dataframe(filename, type = "jtl"):
  df = pd.read_csv(filename)
  if type == "jtl":
    df["label"] = df["label"].astype("category")
    df["responseCode"] = df["responseCode"].astype("category")
    df["responseMessage"] = df["responseMessage"].astype("category")
    df["threadName"] = df["threadName"].astype("category")
    df["dataType"] = df["dataType"].astype("category")
    df["success"] = df["success"].astype("category")

  # print(df.info())
  return df


"""
"""
def filter_dataframe_offset(df, offset):
  filtered_df = df
  if (offset["start"] > 0 or offset["finish"] > 0):
    timestamps = filtered_df["timeStamp"].sort_values(ascending = True)
    start = timestamps.head(1).item() + offset["start"]
    finish = timestamps.tail(1).item() - offset["finish"]
    filtered_df = filtered_df[filtered_df["timeStamp"].between(start, finish)]

  return filtered_df


def filter_dataframe_include_exclude(df, label):
  filtered_df = df

  if (len(label["include"]) > 0):
    filtered_df = filtered_df[filtered_df["label"].isin(label["include"])]

  if (len(label["exclude"]) > 0):
    filtered_df = filtered_df[~filtered_df["label"].isin(label["exclude"])]

  return filtered_df

def process_success(filtered_df, success):
  if (success != None and success != {}):
    print("Process success")
    success_report = []
    if "amount" in success:
      min_value = success["amount"]["min_value"] if "min_value" in success["amount"] else None
      min_tolerance = success["amount"]["min_tolerance"] if "min_tolerance" in success["amount"] else None
      min_priority = success["amount"]["min_priority"] if "min_priority" in success["amount"] else None
      count = len(filtered_df[filtered_df["success"] != True])
      min_tolerance_value = (min_value - (min_value * min_tolerance / 100.0))
   
      if (min_value == None):
        print("success -> minErrorAmount -> value missing")
      else:
        if (count >= min_value):
          min_result = 'pass'        
        elif (count >= min_tolerance_value):
          min_result = 'conditional'
        else:
          min_result = 'fail'

      max_value = success["amount"]["max_value"] if "max_value" in success["amount"] else None
      max_tolerance = success["amount"]["max_tolerance"] if "max_tolerance" in success["amount"] else None
      max_priority = success["amount"]["max_priority"] if "max_priority" in success["amount"] else None
      max_count = len(filtered_df[filtered_df["success"] != True])
      max_tolerance_value = (max_value + (max_value * max_tolerance / 100.0))

      if (max_value == None):
        print("success -> maxErrorAmount -> value missing")
      else:
        if (max_count <= max_value):
          max_result = 'pass'
        elif (max_count <= (max_value + (max_value * max_tolerance / 100.0))):
          max_result = 'conditional'
        else:
          max_result = 'fail'

    success_report.append({ "ErrorAmount": { "min_result": min_result, "min_priority": min_priority, "min_wanted_value": min_value, "min_tolerance_value": min_tolerance_value, "max_result": max_result, "max_priority": max_priority, "max_wanted_value": max_value, "max_tolerance_value": max_tolerance_value, "actual_value": count }})

    print(success_report)
    if "percent" in success:
      min_value = success["percent"]["min_value"] if "min_value" in success["percent"] else None
      min_tolerance = success["percent"]["min_tolerance"] if "min_tolerance" in success["percent"] else None
      min_priority = success["percent"]["min_priority"] if "min_priority" in success["percent"] else None
      min_count = len(filtered_df[filtered_df["success"] != True])
      min_total = len(filtered_df)
      min_actual_value = (min_count / min_total) * 100
      min_tolerance_value = (min_value + (min_value * min_tolerance / 100.0))

      if (min_value == None):
        print("success -> percent -> value missing")
      else:
        if (min_actual_value >= min_value):
          min_result = 'pass'
        elif ((min_count / min_total) * 100 >= (min_value + (min_value * min_tolerance / 100.0))):
          min_result = 'conditional'
        else:
          min_result = 'fail'

    if "percent" in success:
      max_value = success["percent"]["max_value"] if "max_value" in success["percent"] else None
      max_tolerance = success["percent"]["max_tolerance"] if "max_tolerance" in success["percent"] else None
      max_priority = success["percent"]["max_priority"] if "max_priority" in success["percent"] else None
      max_count = len(filtered_df[filtered_df["success"] != True])
      max_total = len(filtered_df)
      max_actual_value = (max_count / max_total) * 100
      max_tolerance_value = (max_value + (max_value * max_tolerance / 100.0))

      if (max_value == None):
        print("success -> maxErrorPercentage -> value missing")
      else:
        if ((max_count / max_total) * 100 <= max_value):

          max_result = 'pass'
        elif ((max_count / max_total) * 100 <= (max_value + (max_value * max_tolerance / 100.0))):

          max_result = 'conditional'
        else:

          max_result = 'fail'

    success_report.append({ "ErrorPercentage": { "min_result": min_result, "min_priority": min_priority, "min_wanted_value": min_value, "min_tolerance_value": min_tolerance_value, "max_result": max_result, "max_priority": max_priority, "max_wanted_value": max_value, "max_tolerance_value": max_tolerance_value, "actual_value": count }})

  return success_report



def process_elapsed(filtered_df, elapsed):
  if (elapsed != None and elapsed != {}):
    # print("Process elapsed")
    elapsed_report = []
    # print(elapsed)
    if "minmax" in elapsed:
      print('MINMAX')
      print(elapsed['minmax'])
      min_value = elapsed["minmax"]["min_value"] if "min_value" in elapsed["minmax"] else None
      print('VALUE')
      print(min_value)
      min_tolerance = elapsed["minmax"]["min_tolerance"] if "min_tolerance" in elapsed["minmax"] else None
      print('TOLERANCE')
      print(min_tolerance)
      min_priority = elapsed["minmax"]["min_priority"] if "min_priority" in elapsed["minmax"] else None
      print('PRIORITY')
      print(min_priority)
      actual_min = round(filtered_df["elapsed"].min(),3).astype('float')
      min_count = len(filtered_df[filtered_df["elapsed"] < min_value])
      min_count2 = len(filtered_df[filtered_df["elapsed"] < (min_value + (min_value * min_tolerance / 100.0))])
      min_tolerance_value = (min_value + (min_value * min_tolerance / 100.0))

      if (min_value == None):
        print("elapsed -> min -> value missing")
      else:
        if (min_count == 0):
          min_result = 'pass'


        elif (min_count2 == 0):
          min_result = 'conditional'
        else:
          min_result = 'fail'


    if "minmax" in elapsed:
      max_value = elapsed["minmax"]["max_value"] if "max_value" in elapsed["minmax"] else None
      max_tolerance = elapsed["minmax"]["max_tolerance"] if "max_tolerance" in elapsed["minmax"] else None
      max_priority = elapsed["minmax"]["max_priority"] if "max_priority" in elapsed["minmax"] else None

      actual_max = round(filtered_df["elapsed"].max(),3).astype('float')
      max_count = len(filtered_df[filtered_df["elapsed"] > max_value])
      max_count2 = len(filtered_df[filtered_df["elapsed"] > (max_value + (max_value * max_tolerance / 100.0))])
      max_tolerance_value = (max_value + (max_value * max_tolerance / 100.0))

      if (max_value == None):
        print("elapsed -> max -> value missing")
      else:
        if (max_count == 0):
          max_result = 'pass'
        elif (max_count2 == 0):
          max_result = 'conditional'
        else:
          max_result = 'fail'

      elapsed_report.append({ "minmax": { "min_result": min_result, "min_priority": min_priority, "min_wanted_value": min_value, "min_tolerance_value": min_tolerance_value, "max_result": max_result, "max_priority": max_priority, "max_wanted_value": max_value, "max_tolerance_value": max_tolerance_value, "actual_min": actual_min, "actual_max": actual_max }})

  return elapsed_report

"""
"""
def process_percentiles(filtered_df, percentiles):
  percentiles_report = {}
  percentiles_report_items = []
  percentiles_keys = percentiles.keys()
  # print(percentiles)

  # print(percentiles['90']['min'])
  for percentile in percentiles_keys:
    wanted_percentile = int(percentile)
    # print('WANTED')
    # print(wanted_percentile)
    pct = filtered_df["elapsed"].quantile(wanted_percentile / 100.0)
    checks = percentiles[percentile]
    # print(pct, checks)

    if "min" in checks:
      # print(checks["min"])
      min_value = checks["min"]["value"] if "value" in checks["min"] else None
      min_tolerance = checks["min"]["tolerance"] if "tolerance" in checks["min"] else None
      min_priority = checks["min"]["priority"] if "priority" in checks["min"] else None
      # print(value, tolerance, priority)
      min_tolerance_value = (min_value - (min_value * min_tolerance / 100.0))

      if (pct > min_value):
        # percentiles_report_items.append({ "percentile": percentile, "check": "min", "result": "pass", "priority": priority, "wanted_value": value, "tolerance_value": tolerance_value, "actual_value": pct})
        min_result = 'pass'
      elif (pct > (min_value - min_value * (min_tolerance / 100.0))):
        # percentiles_report_items.append({ "percentile": percentile, "check": "min", "result": "conditional", "priority": priority, "wanted_value": value, "tolerance_value": tolerance_value, "actual_value": pct})
        min_result = 'conditional'
      else:
        # percentiles_report_items.append({ "percentile": percentile, "check": "min", "result": "fail", "priority": priority, "wanted_value": value, "tolerance_value": tolerance_value, "actual_value": pct})
        min_result = 'fail'

    if "max" in checks:
      # print(checks["max"])
      max_value = checks["max"]["value"] if "value" in checks["max"] else None
      max_tolerance = checks["max"]["tolerance"] if "tolerance" in checks["max"] else None
      max_priority = checks["max"]["priority"] if "priority" in checks["max"] else None
      # print(value, tolerance, priority)
      max_tolerance_value = (max_value + (max_value * max_tolerance / 100.0))

      if (pct <= max_value):
        # percentiles_report_items.append({ "percentile": percentile, "check": "max", "result": "pass", "priority": priority, "wanted_value": value, "tolerance_value": tolerance_value, "actual_value": pct})
        max_result = 'pass'
      elif (pct <= (max_value + max_value * (max_tolerance / 100.0))):
        # percentiles_report_items.append({ "percentile": percentile, "check": "max", "result": "conditional", "priority": priority, "wanted_value": value, "tolerance_value": tolerance_value, "actual_value": pct})
        max_result = 'conditional'
      else:
        # percentiles_report_items.append({ "percentile": percentile, "check": "max", "result": "fail", "priority": priority, "wanted_value": value, "tolerance_value": tolerance_value, "actual_value": pct})
        max_result = 'fail'

    percentiles_report_items.append({percentile :{ "min_result": min_result, "min_priority": min_priority, "min_wanted_value": min_value, "min_tolerance_value": min_tolerance_value, "max_result": max_result, "max_priority": max_priority, "max_wanted_value": max_value, "max_tolerance_value": max_tolerance_value, "actual_value": pct}})
  percentiles_report["percentiles"] = percentiles_report_items
  return (percentiles_report)

def process_tps(filtered_df, tps):
  print("Process TPS")
  print(tps['max_tolerance'])
  tps_report = {}
  timestamps = filtered_df["timeStamp"].sort_values(ascending = True)
  start = timestamps.head(1).item()
  finish = timestamps.tail(1).item()
  duration = (finish - start) / 1000.00
  print(start)
  print(finish)

  count = len(filtered_df)
  if duration != 0:
    actual_tsp = count / duration
  else:
    actual_tsp = 0
  # print(start, finish, duration, count, count / duration)

  # if "min" in tps:
    # print(tps["min"])
  min_value = tps["min_value"] if "min_value" in tps else None
  min_tolerance = tps["min_tolerance"] if "min_tolerance" in tps else None
  min_priority = tps["min_priority"] if "min_priority" in tps else None
  # print(min_value, min_tolerance, min_priority, duration)
  min_tolerance_value = (min_value - (min_value * min_tolerance / 100.0))

  if (actual_tsp >= min_value):
    min_result = 'pass'

  elif (actual_tsp >= min_tolerance_value):
    min_result = 'conditional'
  else:
    min_result = 'fail'


  max_value = tps["max_value"] if "max_value" in tps else None
  max_tolerance = tps["max_tolerance"] if "max_tolerance" in tps else None
  max_priority = tps["max_priority"] if "max_priority" in tps else None
  # print(max_value, max_tolerance, max_priority, duration)
  max_tolerance_value = (max_value + (max_value * max_tolerance / 100.0))

  if (actual_tsp <= max_value):
    max_result = 'pass'
  elif (actual_tsp <= max_tolerance_value):
    max_result = 'conditional'
  else:
    max_result = 'fail'

  tps_report = ({"min_result": min_result, "min_priority": min_priority, "min_wanted_value": min_value, "min_tolerance_value": min_tolerance_value, "max_result": max_result, "max_priority": max_priority, "max_wanted_value": max_value, "max_tolerance_value": max_tolerance_value, "actual_value": actual_tsp})
  
  return tps_report


"""
"""
def process_dataframe(nfrs, df):
  report = []
  trans_nfrs = nfrs["transaction_nfrs"]
  for nfr in trans_nfrs:
    keys = nfr.keys()
    # print(keys)

    name = nfr["name"] if "name" in keys else ""
    priority = nfr["priority"] if "priority" in keys else -1
    report_item = { "name": name, "priority": priority }
    offset = nfr["offset"] if "offset" in keys else { "start": 0, "finish": 0}
    label = nfr["label"] if "label" in keys else { "include": [], "exclude": [] }
    success = nfr["success"] if "success" in keys else None
    elapsed = nfr["elapsed"] if "elapsed" in keys else None
    tps = nfr["tps"] if "tps" in keys else None
    
    filtered_df = filter_dataframe_offset(df, offset)
    filtered_df = filter_dataframe_include_exclude(filtered_df, label)
    print(label)
    if (success != None):
      print('analysing success')
      success_report = process_success(filtered_df, success)
      report_item["success"] = success_report

    if (elapsed != None):
      print('analysing minmax')
      elapsed_report = process_elapsed(filtered_df, elapsed)
      print('ELAPSED REPORT MINMAX')
      print(elapsed_report)

      if "percentiles" in elapsed:
        print('analysing percentile')
        percentiles_report = process_percentiles(filtered_df, elapsed["percentiles"])
        # print(percentiles_report)
        elapsed_report.append(percentiles_report)

      report_item["elapsed"] = elapsed_report
    print('ELAPSED REPORT')
    print(elapsed_report)

    if ("tps" != None):
      print('analysing tps')
      report_item["tps"] = process_tps(filtered_df, tps)

    # print('TPS')
    # print(report_item['tps']
    # )
    report.append(report_item)

  # print('REPORT')
  # print(report)
  print(len(df), len(filtered_df))
  return report

def get_result_colour(chkObj):
  print(chkObj)
  if chkObj['max_result'] == 'fail':
    return '#F53837'
  elif chkObj['max_result'] == 'conditional':
    return '#F4E02F'
  else:
    if chkObj['min_result'] == 'fail':
      return 'magenta'
    elif chkObj['min_result'] == 'conditional':
      return 'blue'
    else:
      return ''

def get_success_colour(arrMin, arrMax):
  # print('MAX')
  # print(arrMax['priority'])
  # print('MIN')
  # print(arrMin['priority'])
  if arrMax['result'] == 'fail':
    return '#F53837'
  elif arrMax['result'] == 'conditional':
    return '#F4E02F'
  else:
    if arrMin['result'] == 'fail':
      return 'blue'
    elif arrMin['result'] == 'conditional':
      return 'magenta'
    else:
      return ''

def get_result_priority(chkObj):
  if chkObj['max_result'] == 'fail':
    return chkObj['max_priority'] * 10
  elif chkObj['max_result'] == 'conditional':
    return chkObj['max_priority'] * 5
  else:
    if chkObj['min_result'] == 'fail':
      chkObj['min_priority'] * 10
    elif chkObj['min_result'] == 'conditional':
      return chkObj['min_priority'] * 5
    else:
      return 0

def get_success_priority(arrMin, arrMax):
  # print('MAX')
  # print(arrMax['priority'])
  # print('MIN')
  # print(arrMin['priority'])
  if arrMax['result'] == 'fail':
    return arrMax['priority'] * 10
  elif arrMax['result'] == 'conditional':
    return arrMax['priority'] * 5
  else:
    if arrMin['result'] == 'fail':
      return arrMax['priority'] * 10
    elif arrMin['result'] == 'conditional':
      arrMax['priority'] * 5
    else:
      return 0
      
#
# Where it all begins
#
if __name__ == "__main__":

  aparser = argparse.ArgumentParser(description='Used to perform NFR checking of the input file metrics',
                                  epilog='Sample usage:\n\tpython nfr_checking.py -n <nfrs-json> -i <input-file> -o <output-file')
  aparser.add_argument('-n', '--nfrs', default=None, required=True, dest='nfrs_file',
                      help='A Json file containing the NFRs to be checked')
  aparser.add_argument('-i', '--input_file', default=None, required=True, dest='input_file',
                      help='The input file to be checked against the NFRs')
  aparser.add_argument('-o', '--output_file', default=None, required=True, dest='output_file',
                      help='The output file with the results of the NFR checking')
  aparser.add_argument('-w', '--html_file', default=None, required=False, dest='html_file',
                      help='The output file with the results of the NFR checking in HTML format')
  aparser.add_argument('-s', '--sort_order', default=None, required=False, dest='sort_order',
                      help='The order in which the output will be sorted. Either label or score.')
  
  args = aparser.parse_args()


  nfrs = load_project_file(args.nfrs_file.lstrip())
  print("Processing {0} NFRs, Version {1}".format(nfrs["project"], nfrs["version"]))

  df = load_dataframe(args.input_file.lstrip())

  report = process_dataframe(nfrs, df)
  # print(report)

  #sort by score


  if args.html_file != None:
    print('===================================================================')
    strHTML = '<html><head>\n'
    strHTML += '</tbody></table>\n\n\n'

    strHTML += '<style>\n'
    strHTML += '.hasTooltip span {\n'
    strHTML += '  display: none;\n'
    strHTML += '  color: #000;\n'
    strHTML += '  text-decoration: none;\n'
    strHTML += '  padding: 3px;\n'
    strHTML += '}\n\n\n'

    strHTML += '.hasTooltip:hover span {\n'
    strHTML += '  display: block;\n'
    strHTML += '  position: absolute;\n'
    strHTML += '  background-color: #FFF;\n'
    strHTML += '  border: 1px solid #CCC;\n'
    strHTML += '  margin: 2px 10px;\n'
    strHTML += '  text-align: left;\n'
    strHTML += '}\n\n\n'
    strHTML += 'tr:nth-child(even) {\n'
    strHTML += 'background-color: #f2f2f2;\n'
    strHTML += '}\n'
    strHTML += 'td:nth-child(n+2) {text-align: right}\n'
    strHTML += '</style>\n'
    strHTML += '</head><body style=\'font-family: segoe\'>'
    strHTML += '<table class=\"\" id=\"nfr_table\" style=\"width: 95%; font-size: 0.75rem; border:none\">\n<thead class=\"\" style=\"text-align:center\">\n<tr>\n<th style=\"text-align:left\">Label</th>\n<th>Error Count</th>\n<th>Error %</th>\n<th>TPS</th>\n<th>Min</th>\n<th>90th</th>\n<th>95th</th>\n<th>99th</th>\n<th>Max</th>\n<th>Score</th>\n</tr>\n</thead><tbody>\n'
    
    numScore = 0
    dfHTML = pd.DataFrame()
    for itm in report:
      rowScore = 0
      # print('TEST')
      # print(itm['success'][0]['ErrorAmount']['actual_value'])
      strRow = '<tr><td>' + itm['name'] + '</td>\n'
      print(itm['name'])
      print('ALL')
      print(itm)
      print('ELAPSED')
      print(itm['elapsed'])
      print('SUCCESS')
      print(itm['success'])
      print('TPS')
      print(itm['tps'])
      if (itm['success'] != None and itm['success'] != {}):
        for i in range(len(itm['success'])):
          if 'ErrorAmount' in itm['success'][i]:
            # print('EA')
            # print(itm['success'][i]['ErrorAmount']['actual_value'])
            strEA = '<td style=\'background-color : \'' + get_result_colour(itm['success'][i]['ErrorAmount']) + '\'><div class=\'hastooltip\'>' + str(round(itm['success'][i]['ErrorAmount']['actual_value'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['success'][i]['ErrorAmount']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['success'][i]['ErrorAmount']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['success'][i]['ErrorAmount']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['success'][i]['ErrorAmount']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
            rowScore += get_result_priority(itm['success'][i]['ErrorAmount'])
          else:
            # print(itm['success'][i]['ErrorPercentage']['actual_value'])
            # print('EP')
            strEP = '<td style=\'background-color : \'white\'\'><div class=\'hastooltip\'>' + str(round(itm['success'][i]['ErrorPercentage']['actual_value'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['success'][i]['ErrorPercentage']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['success'][i]['ErrorPercentage']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['success'][i]['ErrorPercentage']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['success'][i]['ErrorPercentage']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
            rowScore += get_result_priority(itm['success'][i]['ErrorPercentage'])
      else:
        strEA = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'
        strEP = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'

      strTPS = '<td style=\'background-color : ' + get_result_colour(itm['tps']) + '\'><div class=\'hastooltip\'>' + str(round(itm['tps']['actual_value'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['tps']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['tps']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['tps']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['tps']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
      rowScore += get_result_priority(itm['tps'])

      # print(itm['elapsed'])
      
      for j in range(len(itm['elapsed'])):
          # print("ELAPSED")
          # print(itm['elapsed'][j])
          if 'minmax' in itm['elapsed'][j]:
            print('minmax')
            strMin = '<td style=\'background-color : ' + get_result_colour(itm['elapsed'][j]['minmax']) + '\'><div class=\'hastooltip\'>' + str(round(itm['elapsed'][j]['minmax']['actual_min'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['elapsed'][j]['minmax']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j]['minmax']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['elapsed'][j]['minmax']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j]['minmax']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
            strMax = '<td style=\'background-color : ' + get_result_colour(itm['elapsed'][j]['minmax']) + '\'><div class=\'hastooltip\'>' + str(round(itm['elapsed'][j]['minmax']['actual_max'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['elapsed'][j]['minmax']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j]['minmax']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['elapsed'][j]['minmax']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j]['minmax']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
            rowScore += get_result_priority(itm['elapsed'][j]['minmax'])
          elif 'percentiles' in itm['elapsed'][j]:
            for k in itm['elapsed'][j]:
              print('PERC')
              # print(len(itm['elapsed'][j][k]))
              for l in range(len(itm['elapsed'][j][k])):
                if '90' in itm['elapsed'][j][k][l]:
                  print('found 90')
                  str90 = '<td style=\'background-color : ' + get_result_colour(itm['elapsed'][j][k][l]['90']) + '\'><div class=\'hastooltip\'>' + str(round(itm['elapsed'][j][k][l]['90']['actual_value'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['elapsed'][j][k][l]['90']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j][k][l]['90']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['elapsed'][j][k][l]['90']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j][k][l]['90']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
                  rowScore += get_result_priority(itm['elapsed'][j][k][l]['90'])
                elif '95' in itm['elapsed'][j][k][l]:
                  str95 = '<td style=\'background-color : ' + get_result_colour(itm['elapsed'][j][k][l]['95']) + '\'><div class=\'hastooltip\'>' + str(round(itm['elapsed'][j][k][l]['95']['actual_value'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['elapsed'][j][k][l]['95']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j][k][l]['95']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['elapsed'][j][k][l]['95']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j][k][l]['95']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
                  rowScore += get_result_priority(itm['elapsed'][j][k][l]['95'])
                elif '99' in itm['elapsed'][j][k][l]:
                  str99 = '<td style=\'background-color : ' + get_result_colour(itm['elapsed'][j][k][l]['99']) + '\'><div class=\'hastooltip\'>' + str(round(itm['elapsed'][j][k][l]['99']['actual_value'],3)) + '<span><div style=\'font-weight: 600\'>Min <hr></div><div>Target : ' + str(round(itm['elapsed'][j][k][l]['99']['min_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j][k][l]['99']['min_tolerance_value'],3)) + '</div><div style=\'padding-top: 5px; font-weight: 600\'>Max <hr></div><div>Target : ' + str(round(itm['elapsed'][j][k][l]['99']['max_wanted_value'],3)) + '</div><div>Tolerance : ' + str(round(itm['elapsed'][j][k][l]['99']['max_tolerance_value'],3)) + '</div></span></div></td>\n'
                  rowScore += get_result_priority(itm['elapsed'][j][k][l]['99'])
          else:
            strMin = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'
            strMax = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'
            str90 = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'
            str95 = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'
            str99 = '<td style=\'background-color : \'light-gray\'><div class=\'hastooltip\'>0</div></td>\n'
            
      strScore = '<td>' + str(rowScore * itm['priority']) + '</td>\n'

      numScore += rowScore * itm['priority']
      # numScore += rowScore 
      strRow += strEA + strEP + strTPS + strMin + str90 + str95 + str99 + strMax + strScore + '</tr>\n'
      dfHTML = dfHTML.append({'label' : itm['name'], 'Score': rowScore * itm['priority'],'html': strRow}, ignore_index=True)

    if args.sort_order == 'score':
      dfHTML.sort_values(by='Score', ascending=False, inplace=True, ignore_index=True)
    elif args.sort_order == 'label':
      dfHTML.sort_values(by='label', ascending=True, inplace=True, ignore_index=True)

    for itm in dfHTML['html']:
      strHTML += itm

    strHTML += '</tbody></table>\n'
    strHTML += '<div>SCORE : ' + str(numScore) + '</div>'
    # print('HTML')
    # print(dfHTML)

    # print(dfHTML.columns)
    # dfHTML.sort_values(by='Score', ascending=False, inplace=True)
    # print('Sorted HTML')
    # print(dfHTML)

    with open(args.html_file, 'w') as filehandle:
        filehandle.write(strHTML)
    filehandle.close()
  
  with open(args.output_file, 'w') as filehandle:
      filehandle.write(json.dumps(report,indent=4))
  filehandle.close()

