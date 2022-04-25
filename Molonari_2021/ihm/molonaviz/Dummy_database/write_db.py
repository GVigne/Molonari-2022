import pandas as pd
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery
from PyQt5.QtCore import QVariant


def convertDates(df: pd.DataFrame):
    """
    Convert dates from a list of strings by testing several different input formats
    Try all date formats already encountered in data points
    If none of them is OK, try the generic way (None)
    If the generic way doesn't work, this method fails
    (in that case, you should add the new format to the list)
    
    This function works directly on the giving Pandas dataframe (in place)
    This function assumes that the first column of the given Pandas dataframe
    contains the dates as characters string type
    
    For datetime conversion performance, see:
    See https://stackoverflow.com/questions/40881876/python-pandas-convert-datetime-to-timestamp-effectively-through-dt-accessor
    """
    formats = ("%m/%d/%y %H:%M:%S", "%m/%d/%y %I:%M:%S %p",
               "%d/%m/%y %H:%M",    "%d/%m/%y %I:%M %p",
               "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p", 
               "%d/%m/%Y %H:%M",    "%d/%m/%Y %I:%M %p",
               "%y/%m/%d %H:%M:%S", "%y/%m/%d %I:%M:%S %p", 
               "%y/%m/%d %H:%M",    "%y/%m/%d %I:%M %p",
               "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %I:%M:%S %p", 
               "%Y/%m/%d %H:%M",    "%Y/%m/%d %I:%M %p",
               None)
    times = df[df.columns[0]]
    for f in formats:
        try:
            # Convert strings to datetime objects
            new_times = pd.to_datetime(times, format=f)
            # Convert datetime series to numpy array of integers (timestamps)
            new_ts = new_times.values.astype(np.int64)
            # If times are not ordered, this is not the appropriate format
            test = np.sort(new_ts) - new_ts
            if np.sum(abs(test)) != 0 :
                #print("Order is not the same")
                raise ValueError()
            # Else, the conversion is a success
            #print("Found format ", f)
            df[df.columns[0]] = new_times
            return
        
        except ValueError:
            #print("Format ", f, " not valid")
            continue
    
    # None of the known format are valid
    raise ValueError("Cannot convert dates: No known formats match your data!")

def readCSVWithDates(path: str, skiprows=0, sep=','):
    try:
        df = pd.read_csv(path, skiprows=skiprows, sep=sep)
        df = df.columns[1:]
        print(df)
        # TODO : this takes toooooo long each time we read a CSV file !!!
        convertDates(df)
    except Exception as e :
        return pd.DataFrame()
    return df

def my_format(st):
    return "20"+st[0:2]+":"+st[3:5]+":"+st[6:8]+":"+st[9:17]

con = QSqlDatabase.addDatabase("QSQLITE")
con.setDatabaseName("MCMC.sqlite")
con.open()

con.transaction()
# df1 = pd.read_csv("../../../studies/study_2022/Point034/processed_data/processed_pressures.csv")
# df2 = pd.read_csv("../../../studies/study_2022/Point034/processed_data/processed_temperatures.csv")
# df = merged_inner = pd.merge(left=df1, right=df2, left_on="Date Heure, GMT+01:00", right_on="Date Heure, GMT+01:00")
# q= QSqlQuery()
# a = q.prepare("INSERT INTO CleanedMeasures (Date, TempBed, Temp1, Temp2, Temp3, Temp4, Pressure, PointKey) VALUES (:a,:b,:c,:d,:e,:f,:g,:h)")
# print(a)
# for rowIndex, row in df.iterrows(): #iterate over rows
#         elem = []
#         for columnIndex, value in row.items():
#             elem.append(value)
#         q.bindValue(":a", my_format(elem[0]))
#         q.bindValue(":g",elem[1])
#         q.bindValue(":b",elem[2])
#         q.bindValue(":c",elem[3])
#         q.bindValue(":d",elem[4])
#         q.bindValue(":e",elem[5])
#         q.bindValue(":f",elem[6])
#         q.bindValue(":h",1)    
#         q.exec()
# con.commit()

# df1 = pd.read_csv("../../../studies/study_2022/Point034/results/MCMC_results/advective_flux.csv")
# df2 = pd.read_csv("../../../studies/study_2022/Point034/results/MCMC_results/conductive_flux.csv")
# df3 = pd.read_csv("../../../studies/study_2022/Point034/results/MCMC_results/solved_temperatures.csv")
# df4 = pd.read_csv("../../../studies/study_2022/Point034/results/MCMC_results/total_flux.csv")

# df_1 = pd.merge(left=df1, right=df2, left_on="Date Heure, GMT+01:00", right_on="Date Heure, GMT+01:00")
# df_2 = pd.merge(left=df3, right=df4, left_on="Date Heure, GMT+01:00", right_on="Date Heure, GMT+01:00")
# df = pd.merge(left=df_1, right=df_2, left_on="Date Heure, GMT+01:00", right_on="Date Heure, GMT+01:00")
# print(df.head())

# q = QSqlQuery()
# q.prepare(f"""
# INSERT INTO TemperatureAndHeatFlows (
#                                         Date,
#                                         Depth,
#                                         Temperature,
#                                         AdvectiveFlow,
#                                         ConductiveFlow,
#                                         TotalFlow,
#                                         PointKey,
#                                         Quantile
#                                     )
#                                     VALUES (
#                                         :a,
#                                         :b,
#                                         :c,
#                                         :d,
#                                         :e,
#                                         :f,
#                                         1,
#                                         1
#                                     )
# """)


# for rowIndex, row in df.iterrows(): #iterate over rows
#             elem = []
#             for columnIndex, value in row.items():
#                 elem.append(value)
#             m= QSqlQuery(f"""SELECT Date.id FROM Date WHERE Date.Date = "{my_format(elem[0])}" """)
#             m.exec()
#             m.next()
#             q.bindValue(":a",m.value(0))
#             for i in range(1,100):
#                 q.bindValue(":b",i)
#                 q.bindValue(":d",elem[i])
#                 q.bindValue(":e",elem[i+100])
#                 q.bindValue(":c",elem[i+200])
#                 q.bindValue(":f",elem[i+300])
#                 q.exec()

# con.commit()

# df = pd.read_csv("../../../studies/study_2022/Point034/results/MCMC_results/MCMC_flows_quantiles.csv")
# q= QSqlQuery()
# q.prepare("""
#     INSERT INTO WaterFlow (
#                           WaterFlow,
#                           Date,
#                           PointKey,
#                           Quantile
#                       )
#                       VALUES (
#                           :a,
#                           :b,
#                           1,
#                           :c
#                       );

# """)
# for rowIndex, row in df.iterrows(): #iterate over rows
#             elem = []
#             for columnIndex, value in row.items():
#                 elem.append(value)
#             m= QSqlQuery(f"""SELECT Date.id FROM Date WHERE Date.Date = "{my_format(elem[0])}" """)
#             m.exec()
#             m.next()
#             q.bindValue(":b",m.value(0))
            
#             q.bindValue(":c",4) #0.05
#             q.bindValue(":a",elem[2])
#             q.exec()

#             q.bindValue(":c",2) #0.5
#             q.bindValue(":a",elem[3])
#             q.exec()

#             q.bindValue(":c",3) #0.95
#             q.bindValue(":a",elem[4])
#             q.exec()
# con.commit()



df = pd.read_csv("../../../studies/study_2022/Point034/results/MCMC_results/MCMC_temps_quantiles.csv")

q = QSqlQuery()
q.prepare(f"""
INSERT INTO TemperatureAndHeatFlows (
                                        Date,
                                        Depth,
                                        Temperature,
                                        AdvectiveFlow,
                                        ConductiveFlow,
                                        TotalFlow,
                                        PointKey,
                                        Quantile
                                    )
                                    VALUES (
                                        :a,
                                        :b,
                                        :c,
                                        :d,
                                        :e,
                                        :f,
                                        1,
                                        :g
                                    )
""")


for rowIndex, row in df.iterrows(): #iterate over rows
            elem = []
            for columnIndex, value in row.items():
                elem.append(value)
            print(len(elem))
            m= QSqlQuery(f"""SELECT Date.id FROM Date WHERE Date.Date = "{my_format(elem[0])}" """)
            m.exec()
            m.next()
            q.bindValue(":a",m.value(0))

            for i in range(1,400,4):
                q.bindValue(":b",(i+3)//4)
                q.bindValue(":d",0)
                q.bindValue(":e",0)
                q.bindValue(":f",0)

                q.bindValue(":c",elem[i+1])
                q.bindValue(":g",4) #0.05
                q.exec()

                q.bindValue(":c",elem[i+2])
                q.bindValue(":g",2) #0.5
                q.exec()

                q.bindValue(":c",elem[i+3])
                q.bindValue(":g",3) #0.95
                q.exec()

con.commit()