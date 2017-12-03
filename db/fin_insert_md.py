from sqlalchemy.orm import sessionmaker
from db.db_manager_md import create_my_engine
from db.fin_create_md import Base , Asset, Frequency, Currency,TxType , Liquidity
from db.db_manager_md import db_session
from datetime import date

class InsertManager:
    assetdata=None
    session=None

    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()

    
    def __init__(self):
        engine = create_my_engine()
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)  
        self.session = DBSession()
        
    def insertdata(self):
        expense=Asset(name='House Rent',description='House Rent for the current apartment',amount=2000, amount_currency=Currency.USD.value,txtype=TxType.DEBIT.value, acquire_date='2017-01-01',recurrence=1,frequency=Frequency.MONTHLY.value, growth_rate=0.5, liquidity=Liquidity.FLUID.value)
        asset=Asset(name='J803',description='Pune Home',amount=7000000, amount_currency='INR',txtype=TxType.CREDIT.value, acquire_date='2010-10-19',recurrence=1, growth_rate=4, liquidity=Liquidity.PERM_FIXED_ASSET.value)
        asset2=Asset(name='C2E 606',description='Pune Home2',amount=5000000, amount_currency='INR',txtype=TxType.CREDIT.value,acquire_date='2015-10-19',recurrence=1, growth_rate=4, liquidity=Liquidity.PERM_FIXED_ASSET.value)
        asset3=Asset(name='Salary',description='Annual Salary+Bonus',amount=100000, amount_currency=Currency.USD.value,txtype=TxType.CREDIT.value, acquire_date='2017-01-01',recurrence=1, growth_rate=4, liquidity=Liquidity.FLUID.value)
        with db_session() as db:
            db.add(expense)          
            db.add(asset)
            db.add(asset2)
            db.add(asset3)
            db.commit()
     
    
    def insertsqlitedata(self):
        expense=Asset(id=int(1),name='House Rent',description='House Rent for the current apartment',amount=int(2000), amount_currency=Currency.USD.value,txtype=TxType.DEBIT.value, acquire_date=date('2017-01-01'),recurrence=int(1),frequency=int(30), growth_rate=float(0.5),liquidity=int(50))
        #asset=Asset(id=2,name='J803',description='Pune Home',amount=7000000, amount_currency='INR',txtype=TxType.CREDIT.value, acquire_date=date('2010-10-19'),recurrence=1, growth_rate=4, liquidity=10)
        #asset2=Asset(id=3,name='C2E 606',description='Pune Home2',amount=5000000, amount_currency='INR',txtype=TxType.CREDIT.value,acquire_date=date('2015-10-19'),recurrence=1, growth_rate=4, liquidity=10)
        #asset3=Asset(id=4,name='Salary',description='Annual Salary+Bonus',amount=100000, amount_currency=Currency.USD.value,txtype=TxType.CREDIT.value, acquire_date=date('2017-01-01'),recurrence=1, growth_rate=4, liquidity=50)
        with db_session() as db:
            db.add(expense)          
            #self.session.add(asset)
            #self.session.add(asset2)
            #self.session.add(asset3)
            db.commit()
                
class Main(object):    
    if __name__ == '__main__':
        InsertManager().insertdata()
        #InsertManager().insertsqlitedata()