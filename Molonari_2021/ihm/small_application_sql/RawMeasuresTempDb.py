class RawMeasuresTempDb():
    def __init__(self, con, model) -> None:    
        self.con = con
        self.model = model
        
        self.model.setTable("measures_temp")
    
    def insertRawMeasuresTempFromStudy(self, study):
        
        points = study.getPointsDb()
        
        for point in points:
            col = point.dftemp.columns
            for ind in point.dftemp.index:
                
                r = self.model.record()
                r.setValue("Date", point.dftemp[col[0]][ind])
                r.setValue("Temp1", point.dftemp[col[1]][ind])
                r.setValue("Temp2", point.dftemp[col[2]][ind])
                r.setValue("Temp3", point.dftemp[col[3]][ind])
                r.setValue("Temp4", point.dftemp[col[4]][ind])
                r.setValue("Point_key", 1)
                
                self.model.insertRecord(-1, r)
                