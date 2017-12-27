from sqlalchemy import Column, Integer,Float, String, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.expression import text
from datetime import date, datetime
from enum import Enum
from db.db_manager_md import create_my_engine
from dateutil.relativedelta import relativedelta
from forex_python.converter import CurrencyRates 


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
    sort_order=0
    currency_rate=CurrencyRates()
    currency_cache=dict()
    
        
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
            current_year_value=self.getTxTypeInt()*self.getTotalCurrentYearValue(year)
            if(verbose==True or current_year_value!=0):
                print("%d || %s || %d || %s || %s" %(year, self.name,current_year_value, self.acquire_date, self.getEndDate()))
    
    def convertCurrencies(self,from_currency, to_currency='USD'):
        if(from_currency==to_currency):
            return 1
        if(self.currency_cache.get(from_currency+"->"+to_currency)==None):
            self.currency_cache[from_currency+"->"+to_currency]= self.currency_rate.get_rate(from_currency,to_currency)
        return self.currency_cache.get(from_currency+"->"+to_currency)
    
        
    def getEndDate(self):       
        date_1 = datetime.date(self.acquire_date)
        if(self.frequency==Frequency.ANNUAL.value):
            return date_1 + relativedelta(years=self.recurrence)
        elif(self.frequency==Frequency.MONTHLY.value):
            return date_1 + relativedelta(months=self.recurrence)
        elif(self.frequency==Frequency.WEEKLY.value):
            return date_1 + relativedelta(days=self.recurrence*7)
        elif(self.frequency==Frequency.DAILY.value):
            return date_1 + relativedelta(days=self.recurrence)
        
    def isActive(self, year):
        return self.acquire_date.year<= year and self.getEndDate()>date(year,1,1)

    #Reduce amount logic here
    def reduceValue(self, expense, year):
        reduce_amount=expense.getTotalCurrentYearValue(year)
        reduce_amount_in_currency=reduce_amount*self.convertCurrencies(expense.amount_currency,self.amount_currency)
        if(self.getTotalCurrentYearValue(year)>=reduce_amount_in_currency):
            self.setTotalCurrentYearValue(self.getTotalCurrentYearValue(year)-reduce_amount_in_currency, year)
            expense.setTotalCurrentYearValue(0,year)
            return 0
        else:
            remaining_money= reduce_amount_in_currency-self.getTotalCurrentYearValue(year)
            self.setTotalCurrentYearValue(0,year)
            expense.setTotalCurrentYearValue(remaining_money*self.convertCurrencies(self.amount_currency, expense.amount_currency),year)
            return remaining_money
        
    def setTotalCurrentYearValue(self, amount, year=current_year):
        self.asset_year_end_values[year]=amount
        
    def yearsSince(self, year):
        return divmod((datetime(year,12,31)-(self.acquire_date)).total_seconds()+1*24*60*60,60)[0]/(60*24*365)
    
    def termsInAYear(self,year=current_year):
        acquire_dt=datetime.date(self.acquire_date)
        if(acquire_dt<=date(year,12,31)):
            start_date=max(date(year,1,1),acquire_dt)
        else:
            return 0
        if(self.getEndDate()>=date(year,1,1)):
            end_date=min(self.getEndDate(),date(year+1,1,1))
        else:
            return 0
        r = relativedelta(end_date, start_date)
        
        if(self.frequency==Frequency.DAILY.value):
            return r.days
        elif(self.frequency==Frequency.WEEKLY.value):
            return r.weeks
        elif(self.frequency==Frequency.MONTHLY.value):
            return r.months
        else:
            return r.years
        
        
    def getTotalCurrentYearValue(self, year=current_year):
        if(self.name=="Salary"):
            self.name="Salary"
        if(self.acquire_date.year>year):
            return 0
        elif(self.asset_year_end_values.get(year)==None):
            if(self.isActive(year)):
                assetValue=(self.amount*self.termsInAYear(year))*((1+((self.growth_rate*self.termsInAYear(year))/100))**(self.yearsSince(year)))
                carried_over_value=self.getTotalCurrentYearValue(year-1)*((1+(self.growth_rate/100))**self.termsInAYear(year))
                self.asset_year_end_values[year]=assetValue+carried_over_value
            else:
                self.asset_year_end_values[year] = self.getTotalCurrentYearValue(year-1)*((1+(self.growth_rate/100))**self.termsInAYear(year))
        return self.asset_year_end_values.get(year)
    
    def getTxTypeInt(self):
        if(self.txtype==TxType.CREDIT.value):
            return 1
        elif(self.txtype==TxType.DEBIT.value):
            return -1
        else:
            return 0
    
    def mark_start_of_year(self,year):
        self.current_year=year
    
    def mark_end_of_year(self,year):
        self.current_year=year
        self.asset_year_end_values[year]=self.getTotalCurrentYearValue(year)

engine = create_my_engine()
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
    