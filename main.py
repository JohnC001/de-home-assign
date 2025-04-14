import os
import pandas as pd
#import psycopg2
from sqlalchemy import create_engine

#conn=psycopg2.connect(host="localhost", dbname="database")
#cur=conn.cursor()

engine=create_engine('postgresql:///database')
csv_dir='./storage/shared/data-engineering/external-funds'


for file in os.listdir(csv_dir):
	if file.endswith('.csv'):
		name,date_part=file[:-4].rsplit('.',1)
		date=date_part[:10].replace("-","/")
	df=pd.read_csv(os.path.join(csv_dir,file))
	if 'SEDOL' in df.columns:
		df=df.drop(columns=['SEDOL'])
	if 'ISIN' in df.columns:
		df=df.drop(columns=['ISIN'])
	df.assign(name=name,date=date).to_sql('external_funds',engine,if_exists='append',index=False)
	print(f"Imported:{file}")


df_equities=pd.read_sql("""SELECT a.*,c."PRICE" "REF_PRICE",a."PRICE"-c."PRICE" "difference" FROM external_funds a LEFT JOIN equity_reference b ON a."SECURITY NAME"=b."SECURITY NAME" LEFT JOIN equity_prices c ON b."SYMBOL"=c."SYMBOL" AND a."date"=c."DATETIME" WHERE a."FINANCIAL TYPE"='Equities';""",engine)
#print(df_equities.columns)
df_bonds=pd.read_sql("""SELECT a.*,c."PRICE" "REF_PRICE",a."PRICE"-c."PRICE" "difference" FROM external_funds a LEFT JOIN bond_reference b ON a."SECURITY NAME"=b."SECURITY NAME" LEFT JOIN bond_prices c ON b."ISIN"=c."ISIN" AND a."date"=c."DATETIME" WHERE a."FINANCIAL TYPE"='Government Bond';""",engine)
#print(df_bonds.columns)
df_all=pd.concat([df_equities,df_bonds])

with pd.ExcelWriter('reconciliation_report.xlsx') as writer:
	df_all.to_excel(writer,index=False)


#cur.execute("select * from bond_reference limit 5;")
#print(cur.fetchall())
#conn.commit()

#cur.close()
#conn.close()
