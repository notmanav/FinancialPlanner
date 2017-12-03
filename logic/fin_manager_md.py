
from db.fin_read_md import ReadManager

class asset_manager(object):
    default_begin_year=2010
    default_end_year=2020
    read_manager =None
    assets_by_liquidity=None
    
    def __init__(self):
        self.read_manager=ReadManager()
        self.assets_by_liquidity=dict()
    
        
    def calculate_yealy_summary_beginning(self, begin_year=default_begin_year,end_year=default_end_year, verbose=False):
        self.begin_year=begin_year
        current_year=begin_year
        self.map_by_liquidity()
        while(current_year<=end_year):
            if(verbose):
                print('********Beginning of the year: %d *********' %current_year)
            for assetitem in self.read_manager.getassetdata():
                #assetitem.initialize()
                assetitem.mark_start_of_year(current_year)
                if(assetitem.getTxTypeInt()==-1):
                    remainder=-1
                    while(remainder!=0):
                        self.getNextMostLiquidAsset(assetitem).reduceValue(assetitem,current_year)
                assetitem.printMeMini(current_year,verbose)
                assetitem.mark_end_of_year(current_year)
            if(verbose):
                print('=========End of the year: %d ===============' %current_year)
            current_year=current_year+1
            
    def map_by_liquidity(self):
        for assetitem in self.read_manager.getassetdata():
            if(self.assets_by_liquidity[assetitem.liquidity]==None):
                self.assets_by_liquidity[assetitem.liquidity]=list()
            self.assets_by_liquidity[assetitem.liquidity].append(assetitem)
        
    def getNextMostLiquidAsset(self,assetitem):
        if(self.assets_by_liquidity[assetitem.liquidity]==None):
            