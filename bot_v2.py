import ast
import json
import time
import numpy as np
import keras.models
from keras.models import Model
from pybittrex.client import Client
from keras.models import load_model
from keras.layers import Input, Dense
from keras.models import model_from_json
from keras.models import model_from_yaml
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import timeit
import schedule

'''----------------------------------------Data Structurs---------------------------------------------------'''

c = Client(api_key='abc', api_secret='123')

depth =100
OrderBookDepth     = 100
MarketHistoryDepth = 100


MarketHistory_Price=[]
MarketHistory_Quantity=[]
MarketHistory_FillType_Z = [] #ZERO encodecd
MarketHistory_OrderType_Z = []

OrderBook_buy_Quantity = []
OrderBook_buy_Rate = []
OrderBook_sell_Quantity = []
OrderBook_sell_Rate = []

Tick_Ask = []
Tick_Bid = []
Tick_Last = []

Eval_mat_list = []
n = 0

global Prediction_Input

markets_data     = {}

list_of_market_stat_data = {}

market_stat_data ={"Market"        : "cc",
                   "Tick"          : "cc",
                   "OrderBook"     : "cc",
                   "MarketHistory" : "cc" }



market_list = [
'USDT-BTC'
]

'''------------------------------------------model loading ---------------------------------------------------'''
model2m  = load_model('pridic2min.h5')
#model4m  = load_model('pridic4min.h5')
model10m = load_model('pridic10min.h5')
#model14m = load_model('pridic14min.h5')
#model20m = load_model('pridic20min.h5')
model30m = load_model('pridic30min.h5')
model1h  = load_model('pridic1h.h5')
#model2h  = load_model('pridic2h.h5')
#model3h  = load_model('pridic3h.h5')
model4h  = load_model('pridic4h.h5')
model8h  = load_model('pridic8h.h5')
#model16h  = load_model('pridic16h.h5')


'''--------------------------------------------Load old data Data------------------------------------------------------'''

# load the dataset
json_data = []
with open("USDT-BTC_Market_Boot_support_Trading_Data.txt") as file :
    for line in file:
        json_data.append(json.loads(line))
# convert an array of values into a dataset matrix
for i in range(len(json_data)):
   
    if ( (json_data[i]!= []or None) and
         (json_data[i]['Tick'] != []or None ) and         
         (json_data[i]['OrderBook'] != [] or None) and
         (json_data[i]['MarketHistory'] != [] or None) and
         (json_data[i]['MarketHistory']['result'] != [] or None) and
         (json_data[i]['OrderBook']['result']['buy'] != []or None )and
         (json_data[i]['OrderBook']['result']['sell']!= [] or None)and
         (json_data[i]['Tick'] ['result'] != [] or  None) and
         (json_data[i]['Tick'] ['result'] ['Ask'] !=  [] or  None  ) and
         (json_data[i]['Tick'] ['result'] ['Bid'] != [] or None ) and
         (json_data[i]['Tick'] ['result'] ['Last']!= [] or None) 
       ):
      
        Tick_Ask.append(json_data[i]['Tick'] ['result'] ['Ask'])
        Tick_Bid.append(json_data[i]['Tick'] ['result'] ['Bid'])
        Tick_Last.append(json_data[i]['Tick'] ['result'] ['Last'])
        
  
        for m in range(len((json_data[1]['OrderBook']['result']['buy']))) :   
            OrderBook_buy_Quantity.append(json_data[i]['OrderBook']['result']['buy'][m]['Quantity'])
            OrderBook_buy_Rate.append(json_data[i]['OrderBook']['result']['buy'][m]['Rate'])
            #xx=xx+1
            #print("dedata 1 no{}".format(xx))


        for m in range(len((json_data[1]['OrderBook']['result']['sell']))) :
                OrderBook_sell_Quantity.append(json_data[i]['OrderBook']['result']['sell'][m]['Quantity'])
                OrderBook_sell_Rate.append(json_data[i]['OrderBook']['result']['sell'][m]['Rate']) 


        for m in range(len((json_data[1]['MarketHistory']['result']))) :                                                                            
                MarketHistory_Price.append(json_data[i]['MarketHistory']['result'][m]['Price'])
                MarketHistory_Quantity.append(json_data[i]['MarketHistory']['result'][m]['Quantity'])
                                              
                if (json_data[i]['MarketHistory']['result'][m]['FillType']) == 'PARTIAL_FILL' :
                    MarketHistory_FillType_Z.append(0)
                elif (json_data[i]['MarketHistory']['result'][m]['FillType']) == 'FILL' :
                    MarketHistory_FillType_Z.append(1)
                if (json_data[i]['MarketHistory']['result'][m]['OrderType']) == 'BUY' :
                    MarketHistory_OrderType_Z.append(0)
                elif (json_data[i]['MarketHistory']['result'][m]['OrderType']) == 'SELL' :
                    MarketHistory_OrderType_Z.append(1)







'''--------------------------------------------Get NEW Data and pedict------------------------------------------------------'''
'''    
for market in market_list :
    markets_data[market] = []
'''         
              
    
def Get_market_stat_data():
    global MarketHistory_Price
    global MarketHistory_Quantity
    global MarketHistory_FillType_Z 
    global MarketHistory_OrderType_Z 
    global OrderBook_buy_Quantity 
    global OrderBook_buy_Rate 
    global OrderBook_sell_Quantity 
    global OrderBook_sell_Rate
    global Tick_Ask
    global Tick_Bid 
    global Tick_Last
    global market_stat_data
    global Eval_mat_list
    global n
    global Current_price
    global Prediction_UN2m
    global Prediction_UN10m
    global Prediction_Input
    global Prediction_Input
    
    if c.get_ticker('USDT-BTC'):
        for market in market_list:
            with c.get_ticker(market) :
                market_stat_data["Tick"] = (c.get_ticker(market).json())
            with c.get_orderbook(market , "both"):    
                market_stat_data["OrderBook"] = (c.get_orderbook(market , "both").json())
            with c.get_market_history(market) :    
                market_stat_data["MarketHistory"] = (c.get_market_history(market).json())
        
            market_stat_data["OrderBook"]['result']['buy'] = market_stat_data["OrderBook"]['result']["buy"][:OrderBookDepth] # lemting ordebook buy depth 
            market_stat_data["OrderBook"]['result']['sell'] = market_stat_data["OrderBook"]['result']["sell"][:OrderBookDepth] # lemting ordebook sell depth   # i discuverd a bug  here i was wrting back the market sell order book to the market buy order book no lemting it all gatherd data befor 29/11/2017 7 pm are corupted      
            market_stat_data['MarketHistory']['result'] = market_stat_data['MarketHistory']['result'][:MarketHistoryDepth] # lemting MarketHistory depth 
    
        markets_data[market] = (market_stat_data.copy())
        Tick_Ask.append(market_stat_data['Tick'] ['result'] ['Ask'])
        Tick_Bid.append(market_stat_data['Tick'] ['result'] ['Bid'])
        Tick_Last.append(market_stat_data['Tick'] ['result'] ['Last'])
        
        for m in range(len((market_stat_data['OrderBook']['result']['buy']))) :
            OrderBook_buy_Quantity.append(market_stat_data['OrderBook']['result']['buy'][m]['Quantity'])
            OrderBook_buy_Rate.append(market_stat_data['OrderBook']['result']['buy'][m]['Rate'])
       
        for m in range(len((market_stat_data['OrderBook']['result']['sell']))) :
            OrderBook_sell_Quantity.append(market_stat_data['OrderBook']['result']['sell'][m]['Quantity'])
            OrderBook_sell_Rate.append(market_stat_data['OrderBook']['result']['sell'][m]['Rate'])
 
        for m in range(len((market_stat_data['MarketHistory']['result']))) :                                                                            
            MarketHistory_Price.append(market_stat_data['MarketHistory']['result'][m]['Price'])
            MarketHistory_Quantity.append(market_stat_data['MarketHistory']['result'][m]['Quantity'])
                                              
            if (market_stat_data['MarketHistory']['result'][m]['FillType']) == 'PARTIAL_FILL' :
                MarketHistory_FillType_Z.append(0)
            elif (market_stat_data['MarketHistory']['result'][m]['FillType']) == 'FILL' :
                MarketHistory_FillType_Z.append(1)
            if (market_stat_data['MarketHistory']['result'][m]['OrderType']) == 'BUY' :
                MarketHistory_OrderType_Z.append(0)
            elif (market_stat_data['MarketHistory']['result'][m]['OrderType']) == 'SELL' :
                MarketHistory_OrderType_Z.append(1)  #you have to empty it at the end of the function  
            
        prdiction_data_depth = len(Tick_Ask)
        if prdiction_data_depth > 10000 :
            prdiction_data_depth = 10000
        
        print("prdiction_data_depth {} \n".format(prdiction_data_depth)) 
        
        Tick_Ask                  = Tick_Ask[(len(Tick_Ask)-prdiction_data_depth):len(Tick_Ask)]
        Tick_Bid                  = Tick_Bid[(len(Tick_Bid)-prdiction_data_depth):len(Tick_Bid)]
        Tick_Last                 = Tick_Last[(len(Tick_Last)-prdiction_data_depth):len(Tick_Last)]
        OrderBook_buy_Rate        = OrderBook_buy_Rate[(len(OrderBook_buy_Rate)-prdiction_data_depth*OrderBookDepth):len(OrderBook_buy_Rate)]
        OrderBook_sell_Rate       = OrderBook_sell_Rate[(len(OrderBook_sell_Rate)-prdiction_data_depth*OrderBookDepth):len(OrderBook_sell_Rate)]
        OrderBook_buy_Quantity    = OrderBook_buy_Quantity[(len(OrderBook_buy_Quantity)-prdiction_data_depth*OrderBookDepth):len(OrderBook_buy_Quantity)]
        OrderBook_sell_Quantity   = OrderBook_sell_Quantity[(len(OrderBook_sell_Quantity)-prdiction_data_depth*OrderBookDepth):len(OrderBook_sell_Quantity)]
        MarketHistory_Price       = MarketHistory_Price[(len(MarketHistory_Price)-prdiction_data_depth*MarketHistoryDepth):len(MarketHistory_Price)]
        MarketHistory_Quantity    = MarketHistory_Quantity[(len(MarketHistory_Quantity)-prdiction_data_depth*MarketHistoryDepth):len(MarketHistory_Quantity)]
        MarketHistory_FillType_Z  = MarketHistory_FillType_Z[(len(MarketHistory_FillType_Z)-prdiction_data_depth*OrderBookDepth):len(MarketHistory_FillType_Z)]
        MarketHistory_OrderType_Z = MarketHistory_OrderType_Z[(len(MarketHistory_OrderType_Z)-prdiction_data_depth*OrderBookDepth):len(MarketHistory_OrderType_Z)]
        
        
        MarketHistory_Price1=np.reshape( MarketHistory_Price, (depth,int(len(MarketHistory_Price)/depth)))
        MarketHistory_Quantity1=np.reshape(MarketHistory_Quantity, (depth,int(len(MarketHistory_Quantity)/depth)))
        MarketHistory_FillType_Z1=np.reshape(MarketHistory_FillType_Z, (depth,int(len(MarketHistory_FillType_Z)/depth)))
        MarketHistory_OrderType_Z1=np.reshape(MarketHistory_OrderType_Z, (depth,int(len(MarketHistory_OrderType_Z)/depth)))
        OrderBook_buy_Quantity1=np.reshape(OrderBook_buy_Quantity, (depth,int(len(OrderBook_buy_Quantity)/depth)))
        OrderBook_buy_Rate1=np.reshape(OrderBook_buy_Rate, (depth,int(len(OrderBook_buy_Rate)/depth)))
        OrderBook_sell_Quantity1=np.reshape(OrderBook_sell_Quantity, (depth,int(len(OrderBook_sell_Quantity)/depth)))
        OrderBook_sell_Rate1=np.reshape(OrderBook_sell_Rate, (depth,int(len(OrderBook_sell_Rate)/depth)))
        Tick_Ask1 =np.reshape(Tick_Ask ,(1,int(len(Tick_Ask))))
        Tick_Bid1 =np.reshape(Tick_Bid ,(1,int(len(Tick_Bid))))
        Tick_Last1=np.reshape(Tick_Last ,(1,int(len(Tick_Last))))
    
    
        Prediction_Input = np.concatenate((
                       MarketHistory_Price1,
                       MarketHistory_Quantity1,
                       MarketHistory_FillType_Z1,
                       MarketHistory_OrderType_Z1,
                       OrderBook_buy_Quantity1,
                       OrderBook_buy_Rate1,
                       OrderBook_sell_Quantity1,
                       OrderBook_sell_Rate1
                      ))
        Current_price = np.concatenate((
                       Tick_Ask1,
                       Tick_Bid1,
                       Tick_Last1
                      ))
    
       
        scalerCurrent_price = MinMaxScaler(feature_range=(0, 1))
        Traning_Output_Normalized =scalerCurrent_price.fit_transform(Current_price)
    
        scalertraininput = MinMaxScaler(feature_range=(0, 1))
        Prediction_Input_Normalized =scalertraininput.fit_transform(Prediction_Input)
    
        Prediction_Input_Normalized = np.reshape(Prediction_Input_Normalized, (Prediction_Input_Normalized.shape[1],1, Prediction_Input_Normalized.shape[0]))

    
        Prediction2m  = model2m.predict(Prediction_Input_Normalized)
        #Prediction4m  = model4m.predict(Prediction_Input_Normalized)
        Prediction10m = model10m.predict(Prediction_Input_Normalized)
        #Prediction14m = model14m.predict(Prediction_Input_Normalized)
        #Prediction20m = model20m.predict(Prediction_Input_Normalized)
        Prediction30m = model30m.predict(Prediction_Input_Normalized)
        Prediction1h  = model1h.predict(Prediction_Input_Normalized)
        #Prediction2h  = model2h.predict(Prediction_Input_Normalized)
        #Prediction3h  = model3h.predict(Prediction_Input_Normalized)
        Prediction4h  = model4h.predict(Prediction_Input_Normalized)
        Prediction8h  = model8h.predict(Prediction_Input_Normalized)
        #Prediction16h = model16h.predict(Prediction_Input_Normalized)

    
    
        
        #m = Current_price1
        #z = Prediction30m
        
        Prediction2m = np.reshape(Prediction2m, (Prediction2m.shape[1], Prediction2m.shape[0]))
        Prediction_UN2m =scalerCurrent_price.inverse_transform(Prediction2m)
    
        #Prediction4m = np.reshape(Prediction4m, (Prediction4m.shape[0], Prediction4m.shape[1]))
        #Prediction_UN4m =scalerCurrent_price.inverse_transform(Prediction4m)
    
        Prediction10m = np.reshape(Prediction10m, (Prediction10m.shape[1], Prediction10m.shape[0]))
        Prediction_UN10m =scalerCurrent_price.inverse_transform(Prediction10m)
    
        #Prediction14m = np.reshape(Prediction14m, (Prediction14m.shape[0], Prediction14m.shape[1]))
        #Prediction_UN14m =scalerCurrent_price.inverse_transform(Prediction14m)
    
        #Prediction20m = np.reshape(Prediction20m, (Prediction20m.shape[0], Prediction20m.shape[1]))
        #Prediction_UN20m =scalerCurrent_price.inverse_transform(Prediction20m)
    
        Prediction30m = np.reshape(Prediction30m, (Prediction30m.shape[1], Prediction30m.shape[0]))
        Prediction_UN30m =scalerCurrent_price.inverse_transform(Prediction30m)
    
        Prediction1h = np.reshape(Prediction1h, (Prediction1h.shape[1], Prediction1h.shape[0]))
        Prediction_UN1h =scalerCurrent_price.inverse_transform(Prediction1h)
    
        #Prediction2h = np.reshape(Prediction2h, (Prediction2h.shape[0], Prediction2h.shape[1]))
        #Prediction_UN2h =scalerCurrent_price.inverse_transform(Prediction2h)
    
        #Prediction3h = np.reshape(Prediction3h, (Prediction3h.shape[0], Prediction3h.shape[1]))
        #Prediction_UN3h =scalerCurrent_price.inverse_transform(Prediction3h)
    
        Prediction4h = np.reshape(Prediction4h, (Prediction4h.shape[1], Prediction4h.shape[0]))
        Prediction_UN4h =scalerCurrent_price.inverse_transform(Prediction4h)
    
        Prediction8h = np.reshape(Prediction8h, (Prediction8h.shape[1], Prediction8h.shape[0]))
        Prediction_UN8h =scalerCurrent_price.inverse_transform(Prediction8h)
    
        #Prediction16h = np.reshape(Prediction16h, (Prediction16h.shape[0], Prediction16h.shape[1]))
        #Prediction_UN16h =scalerCurrent_price.inverse_transform(Prediction16h)
    

        Prediction_UN2m  = np.reshape(Prediction_UN2m,  (Prediction_UN2m.shape[0] , Prediction_UN2m.shape[1])) 
        #Prediction_UN4m  = np.reshape(Prediction_UN4m,  (Prediction_UN4m.shape[1] , Prediction_UN4m.shape[0]))
        Prediction_UN10m = np.reshape(Prediction_UN10m, (Prediction_UN10m.shape[0], Prediction_UN10m.shape[1]))
        #Prediction_UN14m = np.reshape(Prediction_UN14m, (Prediction_UN14m.shape[1], Prediction_UN14m.shape[0]))
        #Prediction_UN20m = np.reshape(Prediction_UN20m, (Prediction_UN20m.shape[1], Prediction_UN20m.shape[0]))
        Prediction_UN30m = np.reshape(Prediction_UN30m, (Prediction_UN30m.shape[0], Prediction_UN30m.shape[1]))
        Prediction_UN1h  = np.reshape(Prediction_UN1h,  (Prediction_UN1h.shape[0] , Prediction_UN1h.shape[1]))
        #Prediction_UN2h  = np.reshape(Prediction_UN2h,  (Prediction_UN2h.shape[1] , Prediction_UN2h.shape[0]))
        #Prediction_UN3h  = np.reshape(Prediction_UN3h,  (Prediction_UN3h.shape[1] , Prediction_UN3h.shape[0]))
        Prediction_UN4h  = np.reshape(Prediction_UN4h,  (Prediction_UN4h.shape[0] , Prediction_UN4h.shape[1]))
        Prediction_UN8h  = np.reshape(Prediction_UN8h,  (Prediction_UN8h.shape[0] , Prediction_UN8h.shape[1]))
        #Prediction_UN16h = np.reshape(Prediction_UN16h, (Prediction_UN16h.shape[1], Prediction_UN16h.shape[0]))
        #Current_price1 = np.reshape(Current_price1, (Current_price1.shape[1], Current_price1.shape[0]))

        
    
        Eval_mat = np.concatenate((
                    Current_price[:,-1],
                    Prediction_UN2m[:,-1],
                    Prediction_UN10m[:,-1],
                    Prediction_UN30m[:,-1],
                    Prediction_UN1h[:,-1],
                    Prediction_UN4h[:,-1],
                    Prediction_UN8h[:,-1]
                    ))
        #print("Current_price {} \n".format(Current_price))        
        print("Eval_mat {} \n".format(Eval_mat))
        Eval_mat_list= Eval_mat.tolist()
        for market in market_list:
            with open("{}_Market_predictions.txt".format(market), "a+") as market_file :
                    json.dump(Eval_mat_list, market_file)
                    market_file.write("\n") #padding the jason object in file with a newline indcator "evey opject in his owen line"
                    market_file.close()
            n = n+1
        print("#-------prediction no. {} the format is ASK-BID-LAST-----# \n".format(n))
        print("Current price {} \n".format(Current_price[:,-1]))
        print("prediction+2min {} \n".format(Prediction_UN2m[:,-1]))
        #print("prediction+4min {} \n".format(Prediction_UN4m[-1])[:])
        print("prediction+10min {} \n".format(Prediction_UN10m[:,-1]))
        print("prediction+30min {} \n".format(Prediction_UN30m[:,-1]))
        print("prediction+1h {} \n".format(Prediction_UN1h[:,-1]))
        print("prediction+4h {} \n".format(Prediction_UN4h[:,-1]))
        print("prediction+8h {} \n".format(Prediction_UN8h[:,-1]))
        print("#-------------------------------------------------------------------------#")
        print("\n")
        

    

'''-----------------------------------------schedular and main entry point--------------------------------------'''
'''
for i in range(5):
        Get_market_stat_data()
        time.sleep(30)


'''
schedule.every(119).seconds.do(Get_market_stat_data)
while True:
    schedule.run_pending()
    time.sleep(1)



