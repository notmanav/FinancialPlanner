from sqlalchemy.orm import sessionmaker
from db.db_manager_md import create_my_engine
from db.fin_create_md import Base , Asset
from db.db_manager_md import db_session




class ReadManager():
    
    session=None
    engine = None
    assetdata=None
    readmanager=None
    i=1
    
    def __init__(self):
        self.assetdata=None
        engine = create_my_engine()
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)  
        self.session = DBSession()
    
    def getReadManager(self):
        if(ReadManager.readmanager==None):
            ReadManager.readmanager=ReadManager()
        return ReadManager.readmanager
        
    def getassetdata(self):
        if(self.assetdata==None):
            print("reading asset data # %d %s" %(self.i, self.assetdata))
            self.i+=1
            with db_session() as db:  
                self.assetdata=db.query(Asset).order_by(Asset.txtype,Asset.liquidity).all()
        return self.assetdata
        
