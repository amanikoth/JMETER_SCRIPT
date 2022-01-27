import os, csv, sys, json, ast
import pandas as pd
import numpy as np

def build_nfr(data, df):
    nfr_out = []
    tran_out = []

    for index, row in df.iterrows():
        print(row['label'])
        if row['label'] != 'JSR223 Sampler':
            ser_work = data[data['label'].eq(row['label'])]
            ser_work['success'] = ser_work['success'].map({False: 1, True: 0})
            # print(ser_work['success'].head())
            dfq = ser_work['elapsed'].quantile([.9,.95,.99]).to_frame()
            dfq.reset_index()

            intMinTime = ser_work['timeStamp'].min()
            intMaxTime = ser_work['timeStamp'].max()
            intTxnCount = ser_work['success'].count()
            print('FAILS : ' +str(ser_work['success'].sum()))

            intSuccess = ser_work['success'].sum()/ser_work['success'].count()
            intMax = ser_work['elapsed'].max()
            intMin = ser_work['elapsed'].min()

            tran_out.append({
                "offset": { "start": 0, "finish": 0 },
                "priority": 1,
                "name": row["label"],
                "label": {
                    "include": [row["label"]],
                    "exclude": []
                },
                "success": {
                    "amount" : {"min_value": 0, "min_tolerance": 0.0, "min_priority": 1, "max_value": int(ser_work["success"].sum()), "max_tolerance": 10.0, "max_priority": 1 },
                    "percent" : {"min_value": 0, "min_tolerance": 0.0, "min_priority": 1, "max_value": round(intSuccess*100,0), "max_tolerance": 10.0, "max_priority": 1 }
                },
                "elapsed": {
                    "minmax" : {"max_value": float(round(intMax.astype(float),3)), "max_tolerance": 10, "max_priority": 1, "min_value": float(round(intMin.astype(float),3)), "min_tolerance": 10, "min_priority": 1 },
                    "movingAverages": {},
                    "percentiles": {
                    "90": {
                        "max": { "value": round(dfq.iloc[0,0],3), "tolerance": 10, "priority": 1 },
                        "min":{ "value": 0, "tolerance": 0.0, "priority": 1 }
                    },
                    "95": {
                        "max": { "value": round(dfq.iloc[1,0],3), "tolerance": 10, "priority": 1 },
                        "min": { "value": 0, "tolerance": 0.0, "priority": 1 }
                    },
                    "99": {
                        "max": { "value": round(dfq.iloc[2,0],3), "tolerance": 10, "priority": 1 },
                        "min": { "value": 0, "tolerance": 0.0, "priority": 1 }
                    }
                    }
                },
                "tps": {
                    "max_value": round(intTxnCount/((intMaxTime - intMinTime)/1000),3), "max_tolerance": 10, "max_priority": 1 ,
                    "min_value": 0, "min_tolerance": 0, "min_priority": 1 }
            })

    nfr_out = {
        'project': "TfNSW",
        "version": "0.1",
        "transaction_nfrs":tran_out}

    #nfr_out.append({
        #'project': 'TfNSW',
        #'version': '0.1',
        #'transaction_nfrs':tran_out})
    
    # print(nfr_out)
    # with open(sys.argv[2] + '.nfr.json', "w") as outfile:
    #     json.dump(nfr_out, outfile,indent=4)
    # json.dump(nfr_out,sys.argv[2] + '.nfr.json',indent=4 )
    # print(json.dump(nfr_out))
    with open(sys.argv[2] + '.nfr.json', 'w') as filehandle:
        filehandle.write(json.dumps(nfr_out,indent=4))
    filehandle.close()

##load the JTL file
data = pd.read_csv(sys.argv[1], low_memory=False)

##create unique list of labels
df = pd.DataFrame(data['label'].unique())
##add column header
df.columns = ['label']
##save filter list to file
df.to_csv(sys.argv[2], encoding='utf-8', index=False)
##save JTL file to pickle format for faster loading
data.to_pickle(sys.argv[1] + '.pkl')

#if the parameter is set to Y build the NFR shell
if sys.argv[3] == 'Y':
    build_nfr(data,df)
