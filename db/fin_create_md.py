from sqlalchemy import Column, Integer,Float, String, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.expression import text
from datetime import date
from enum import Enum
from db.db_manager_md import create_my_engine

class Currency(Enum):
    USD='USD'
    EUR='EUR'
    INR='INR'

class TxType(Enum):
    CREDIT='CREDIT'
    DEBIT='DEBIT'

class Liquidity(Enum):
    PERM_FIXED_ASSET=10
    FIXED_ASSET=20
    DEPOSITS=30
    SAVINGS=40
    FLUID=50
    
    def succ(self):
        v = self.value + 10
        if v > self.FLUID:
            raise ValueError('Enumeration ended')
        return Liquidity(v)

    def pred(self):
        v = self.value - 10
        if v == 0:
            raise ValueError('Enumeration ended')
        return Liquidity(v)

class Frequency(Enum):
    DAILY=1
    WEEKLY=7
    MONTHLY=30
    ANNUAL=365

Base = declarative_base()
   
class Asset(Base):
    __tablename__ = 'Asset'
    id = Column(Integer, primary_key=True)
    name=Column(String(100), nullable=False)
    description=Column(String(1000))
    amount=Column(Integer, nullable=False)
    amount_currency=Column(String(10), nullable=False, server_default=Currency.USD.value)
    txtype=Column(String(10), nullable=False, server_default=TxType.DEBIT.value)
    acquire_date=Column(DateTime)
    liquidity=Column(Integer, nullable=False, server_default=str(Liquidity.FLUID.value))
    recurrence =Column (Integer, nullable=False, server_default='1')
    frequency=Column(Integer, nullable=False, server_default=str(Frequency.ANNUAL.value))
    growth_rate=Column(Float,nullable=False, server_default=str('0.0'))
    active=Column(String(45), nullable=False, server_default='True')
    create_date=Column(DateTime, nullable=False, server_default=text('current_timestamp'))
    update_date=Column(DateTime, nullable=False, server_default=text('current_timestamp on update current_timestamp'))
    #create_date=Column(DateTime, nullable=False, server_default=text('current_timestamp'))
    #update_date=Column(DateTime, nullable=False, server_default=text('current_timestamp'))
    year_end_balance=0
    carry_over_value=0
    current_year=0
    asset_year_end_values=None
    
        
    @orm.reconstructor
    def init_on_load(self):
        self.asset_year_end_values=dict()
        self.year_end_balance=0
        self.carry_over_value=0
        self.current_year=0

    def printMe(self):
            print("Original Value of the Asset is: %d" %self.amount)
            print("Original acquisition date of the asset is: %s" %self.acquire_date)
            print("End date of Asset: %s" %self.getEndDate())

    def printMeMini(self, year, verbose=False):
            current_year_value=self.getNetCurrentYearValue(year)
            if(verbose==True or current_year_value!=0):
                print("%d || %s || %d || %s || %s" %(year, self.name,current_year_value, self.acquire_date, self.getEndDate()))
    
    def getEndDate(self):
        try:
            return self.acquire_date.replace(year = self.acquire_date.year + self.recurrence)
        except ValueError:
            return self.acquire_date + (date(self.acquire_date.year + self.recurrence, 3, 1) - date(self.acquire_date.year, 3, 1))
        
    def isActive(self, year):
        return self.acquire_date.year<= year and self.getEndDate().year>year

    def reduceValue(self, money, year):
        if(self.getTotalCurrentYearValue(year)>=money):
            self.setTotalCurrentYearValue(self.getTotalCurrentYearValue(year)-money, year)
            return 0
        else:
            remaining_money= money-self.getTotalCurrentYearValue(year)
            self.setTotalCurrentYearValue(0,year)
            return remaining_money
    
    def yearsSince(self, year):
        return self.acquire_date.year-year
        
    def setTotalCurrentYearValue(self, amount, year=current_year):
        self.asset_year_end_values[year]=amount
        
    def getTotalCurrentYearValue(self, year=current_year):
        if(self.acquire_date.year>year):
            return 0
        elif(self.asset_year_end_values.get(self.current_year)==None):
            if(self.isActive(year)):
                assetValue=self.amount*(1+self.growth_rate/100)**self.yearsSince(year)
                carried_over_value=self.getTotalCurrentYearValue(year-1)*(1+(self.growth_rate/100))
                self.asset_year_end_values[self.current_year]=assetValue+carried_over_value
            else:
                self.asset_year_end_values[self.current_year]= self.getTotalCurrentYearValue(year-1)*(1+(self.growth_rate/100))
        return self.asset_year_end_values.get(self.current_year)
    
    def getNetCurrentYearValue(self,year=current_year):
        return self.getTxTypeInt()*self.getTotalCurrentYearValue(year)
    
    def getTxTypeInt(self):
        if(self.txtype==TxType.CREDIT.value):
            return 1
        elif(self.txtype==TxType.DEBIT.value):
            return -1
        else:
            return 0
    
    def mark_start_of_year(self,year):
        self.current_year=year
        self.asset_year_end_values[year]=self.getTotalCurrentYearValue(year)
    
    def mark_end_of_year(self,year):
        self.current_year=year

engine = create_my_engine()
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
    