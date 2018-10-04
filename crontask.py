import datetime
today_date = str(datetime.datetime.now().date())
import pymongo
from pymongo import MongoClient
connection = MongoClient('localhost:27017')
      
db = connection.analytics
collection = db.shippr_inventory
import pymssql
server = 'MILFOIL.arvixe.com'
user = 'usrShipprTech'
password = 'usr@ShipprTech'

conn = pymssql.connect(server, user, password, "dbShipprTech")
cursor = conn.cursor(as_dict=True)


info = {}
info['$regex'] = today_date
query = {}
query['_id'] = info
data = collection.find(query)

for d in data:
    collectionreport = db.report
    try:
        rep  = {}
        rep['_id'] = d['_id']
        collectionreport.insert(rep)
    except:
        pass
    box_dict  = {}
    id =  d['_id'][len(today_date)+1:]
    
    cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReport] where ReportDateIST = '" + str(today_date) + "' and DepotCode ='" + id+ "' order by ID Desc")
    reports = cursor.fetchall()
    if len(reports) > 0:
        report_id = reports[0]['ID']
        
        cursor.execute("SELECT box.RouteCode as code, box.BoxID as box, box.AmountDue as amountdue,box.AmountPaid as amntpaid,ISNULL(box.DeliveredQuantity, 0)  as dlvrd_qty,box.DeliveryStateReasonText as dlvd_reason, box.Description as Dsc, box.DeliveryStateReasonText as text,ISNULL(box.FailedQuantity, 0) as failedqty,box.FailedReasonText as failedreason,box.NoOfItems as qty,ISNULL(box.RejectedQuantity, 0)  as rej_qty, box.RejectedReasonText as rej_reason,box.Sequence as seq,route_detail.DropPointCode as DropPointCode, ISNULL(rs.DAName, 'DA NOT ASSIGNED') as da, ISNULL(rs.DriverName, 'Driver NOT ASSIGNED') as drv, rs.DriverContactNumber as drv_number, rs.DAContactNumber as da_number,rs.DVRCNumber as vehicle_number FROM[dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]  box join[dbShipprTech].[usrTYP00].[tReportRouteDetail] route_detail on box.ReportRouteSummaryID = route_detail.ReportRouteSummaryID and box.Sequence = route_detail.Sequence left join[dbShipprTech].[usrTYP00].[tReportRouteResource] rs on   box.ReportRouteSummaryID = rs.ReportRouteSummaryID where box.ReportID  = '" + str(report_id) + "' order by code,seq")
        boxids = cursor.fetchall()
        for box in boxids:
            key =  box['box']
            ind = key.index("-")
            if ind != -1:
                key = key[ind+1:]
            
            if box['rej_reason'] != 'Damaged Item':
               returned_boxes = box['dlvrd_qty']
            else:
               returned_boxes = box['dlvrd_qty'] + box['rej_qty']
            try:
                box_dict[key] += returned_boxes
            except:
                box_dict[key] = returned_boxes
    info = {}   
    for inv in d["inventory_data"]:
        try:
            box_key =  str(int(inv['PRODUCT CODE']))
        except:
            box_key = inv['PRODUCT CODE']
        try:
            
            inv['INVOICE QTY'] -= box_dict[box_key]
            
        except:
            pass
        try:
            info[str(int(inv['PRODUCT CODE']))] = inv 
        except:
            info[str(inv['PRODUCT CODE'])] = inv 
    collection = db.shippr_inventory_summary
    
    data_sum = collection.find_one({'_id': id })
    if data_sum == None:
        result = {}
        result['_id'] = id
        result['inventory_data'] = info
        
        collection.insert(result)
    else:
        data = data_sum["inventory_data"]
        data_keys = set(data.keys())
        info_keys = set(info.keys())
        intersect = info_keys.intersection(data_keys)
        diff = info_keys - data_keys
        
        for i in intersect:
            data[i]['INVOICE QTY'] += info[i]['INVOICE QTY']
        
        for i in diff:
            data[str(i)] = info[i]
        collection.update({"_id": id},{"inventory_data":data})
