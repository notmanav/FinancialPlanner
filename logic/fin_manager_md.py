
from db.fin_read_md import ReadManager
from db.fin_create_md import TxType

class asset_manager(object):
    default_begin_year=2010
    default_end_year=2020
    read_manager =None
    assets_by_liquidity=None
            
    def __init__(self):
        self.read_manager=ReadManager()
        self.assets_by_liquidity=list()
    
        
    def print_year_end_summary(self, current_year, verbose):
        if (verbose):
            print('********Beginning of the year: %d *********' % current_year)
        for assetitem in self.read_manager.getassetdata():
            assetitem.printMeMini(current_year, verbose)
            assetitem.mark_end_of_year(current_year)
        
        if (verbose):
            print('=========End of the year: %d ===============' % current_year)

    def calculate_yealy_summary_beginning(self, begin_year=default_begin_year,end_year=default_end_year, verbose=False):
        self.begin_year=begin_year
        current_year=begin_year
        self.assets_by_liquidity=list()
        while(current_year<=end_year):
            for assetitem in self.read_manager.getassetdata():
                if(assetitem.txtype==TxType.CREDIT.value):
                    assetitem.mark_start_of_year(current_year)
                    self.assets_by_liquidity.append(assetitem)
                    assetitem.mark_end_of_year(current_year)
            
            self.sort_by_liquidity()
            
            for assetitem in self.read_manager.getassetdata():
                if(assetitem.txtype==TxType.DEBIT.value):
                    assetitem.mark_start_of_year(current_year)
                    remainder=-1
                    while(remainder!=0):
                        remainder=self.getNextMostLiquidAsset().reduceValue(assetitem,current_year)
                        if(remainder!=0):
                            self.assets_by_liquidity.pop()
                            self.sort_by_liquidity()
            
            #Year End printing
            self.print_year_end_summary(current_year, verbose)
            current_year=current_year+1
            
    def sort_by_liquidity(self):
        self.assets_by_liquidity.sort(key=lambda x: x.liquidity*1000000000+x.amount, reverse=False)
        
    def getNextMostLiquidAsset(self):
        return self.assets_by_liquidity[-1]