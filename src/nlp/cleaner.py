import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')




df= pd.read_csv('../src/agoda_reviews.csv')

df['name'] = df['name'].astype('string')
df['name'] = df['name'].fillna("anonymous")





#df['review'] = df['review'].str.lower().str.strip()
#df['review']= df['review'].str.replace(r'<.*?>', '', regex=True)

df['review'] = df['review'].str.encode('ascii','ignore').str.decode('utf-8')



df.to_csv('../src/agoda_reviews.csv', index=False)
