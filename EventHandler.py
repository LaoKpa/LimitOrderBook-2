from Order import Order
from Orderbook_new import Orderbook_new
import pandas as pd

data = pd.read_csv('Data/MSGData.csv')
data.columns = ['Index', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'TradeDirection']
print(data.head())
# read in csv 

# loop through the data frame 
    


    
