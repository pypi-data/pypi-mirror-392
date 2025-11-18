import os
import baostock as bs
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

class BAOSTOCK:
    def __init__(self, _market='cn') -> None:
        self.market = 'cn'

        self.home = "%s" % (os.getenv('HOME'))
        self.dir = "cn"
        self.csvDir = f'{self.home}/project/data/{self.dir}'

    def getK(self, _code):
        try:
            bs.login()
            #code = "sh.600036"
            rs = bs.query_history_k_data_plus(_code,
    "date,code,open,high,low,close,volume,amount",
    start_date="2000-01-01",
    frequency="d", adjustflag="2")
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            hist = pd.DataFrame(data_list, columns=rs.fields)
            bs.logout()
        except Exception as e:
            print(f'failed: {e}')
            bs.logout()
            return None

        #print(hist.head())
        if len(hist) <= 10:
            return hist

        hist.columns = ["Date", "Code", "Open", "High", "Low", "Close", "Volume", "Amount"]
        hist = hist.reset_index()
        hist = hist.set_index('Date')
        hist = hist.dropna()
        csvPath = "%s/%s.csv" % (self.csvDir, _code)
        #print("--------", _code, csvPath)
        hist.to_csv(csvPath)
        return hist

    def getListPath(self):
        # Define the file path
        list_path = "%s/project/data/list/cn_baostock.txt" % (self.home)
        return list_path

    def getKFromList(self):
        # Define the file path
        list_path = "%s/project/data/list/cn_baostock.txt" % (self.home)

        try:
            with open(list_path, 'r') as file:
                for line in file:
                    code = line.strip()
                    print(code)
                    _ = self.getK(code)
        except FileNotFoundError:
            print(f"File '{list_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__=="__main__":
    b = BAOSTOCK()
    data = b.getK('sh.601088')
    print(data)

    b.getKFromList()
