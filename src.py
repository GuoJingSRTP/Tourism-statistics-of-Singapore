
# coding: utf-8

# # Record of Visitor Arrivals & Tourism Receipts in Singapore

# In[127]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# <li> Step 1. Read records --- Annual International Visitor Arrivals by Country of Residence, 2006 - 2015

# In[876]:

arrival_df = pd.read_excel('https://www.stb.gov.sg/statistics-and-market-insights/documents/2015_annualtourismstats.xlsx',sheetname ='2.2_AnnCOR',skiprows=3,parse_cols=[0]+list(range(4,30,3)),index_col=0)
arrival_df = arrival_df.dropna()

# remove unwanted items
removalItems =  ["TOTAL1", "TOTAL", "NOT STATED", "NORTH ASIA","SOUTHEAST ASIA","SOUTH ASIA","Southeast Asia", "North Asia", "South Asia", "West Asia","AMERICAS","ASIA","EUROPE","OCEANIA","AFRICA"]
arrival_df = arrival_df.loc[[ x for x in arrival_df.index if x not in removalItems]]

# add new col about continents
continents = {"AMERICAS":["Canada","USA","Other Countries in Americas"],
              "ASIA":["Brunei Darussalam","Indonesia","Malaysia","Myanmar","Philippines","Thailand","Vietnam","Other Countries in Southeast Asia","China","Taiwan","Hong Kong SAR","Japan","South Korea","Other Countries in North Asia","Bangladesh","India","Nepal","Pakistan","Sri Lanka","Other Countries in South Asia","Iran","Israel","Kuwait","Saudi Arabia","United Arab Emirates","Other Countries in West Asia"],
              "EUROPE":["Austria","Belgium & Luxembourg","Denmark","Finland","France","Germany","Greece","Italy","Netherlands","Norway","Poland","Rep of Ireland","Russian Federation","Spain","Sweden","Switzerland","Turkey","UK","Other Countries in Eastern Europe","Other Countries in Western Europe"],
              "OCEANIA":["Australia","New Zealand","Other Countries in Oceania"],
              "AFRICA":["Egypt","Mauritius","South Africa (Rep of)","Other Countries in Africa"]}

list_key_value =[]
for k,v in continents.items():
    [ list_key_value.append([k,i]) for i in v]

_ = pd.DataFrame(list_key_value,columns=["Continent","COUNTRY OF RESIDENCE"]).set_index("COUNTRY OF RESIDENCE")


arrival_df = arrival_df.join(_,how="inner")



# <li> Step 2. Read records --- Annual Tourism Receipts by Country of Residence, 2011 - 2015
# (S$ MILLION)
# 
# Tourism Receipts comprise any expenditure incurred by visitors (including transit passengers,
# foreign air/sea crew and foreign students) during their stay in Singapore as well as the amount
# they prepaid on components such as accommodation and sightseeing tours before arrival. 

# In[879]:

# this excel file only contains data from 2011 to 2015
receipts_df = pd.read_excel('https://www.stb.gov.sg/statistics-and-market-insights/documents/2015_annualtourismstats.xlsx',sheetname ='3.3_TR Country',skiprows=3,parse_cols=[0]+list(range(1,10,2)),index_col=0)
receipts_df = receipts_df.dropna()
receipts_df = receipts_df.loc[[ x for x in receipts_df.index if x not in removalItems]]
receipts_df = receipts_df.iloc[1:]
receipts_df = receipts_df.astype('int32')

# additional data from 2007 to 2011 are collected from https://www.stb.gov.sg/statistics-and-market-insights/marketstatistics/x1annual_report_on_tourism_statistics_2010_2011.pdf
# the data are saved in 2007-2011_annualtourismreceipts.xlsx
_receipts_df = pd.read_excel('https://github.com/NetLand-NTU/Tourism-statistics-of-Singapore/blob/master/data/2007-2011_annualtourismreceipts.xlsx?raw=true',index_col=0)
_receipts_df = _receipts_df[_receipts_df.columns[:-1]] #remove 2011 col

receipts_df = _receipts_df.join(receipts_df,how="inner")


# <li> Step 3. Combine above two records

# In[860]:

tourism_sin = receipts_df.join(arrival_df,how="inner",lsuffix='_receipt',rsuffix='_arrival',sort=True)


# <li> Step 4. Sources of tourists

# In[602]:

arrivals = tourism_sin.pivot_table(values=tourism_sin.columns[9:-1],columns=['Continent'],aggfunc=[np.mean,np.sum,np.median,np.std])


# In[478]:



def plot_bar_box(data,mytitle,ifplotHist=True):
    plt.figure(figsize=(15,5))
    
    # plot sum
    plt.subplot(131)
    _ = np.cumsum(data,axis=1)
    ind = np.arange(data.shape[0])
    for i in reversed(_.columns):
        plt.bar(ind,_[i].T,width=0.8,alpha=0.8,align='center')

    plt.title(mytitle[0]) 
    plt.xticks(ind, np.arange(2007,2016))
    plt.legend(list(reversed(_.columns)),loc=2)

    plt.plot(ind,_[_.columns[-1]],'-ro')
    
    #plot box
    plt.subplot(132)
    plt.boxplot(data.as_matrix(),widths=0.8,labels=_.columns,sym='b+',showfliers=True)
    plt.title(mytitle[1]) 
    
    #plot hist
    if ifplotHist:
        ax = plt.subplot(133)
        from collections import Counter
        counts_continents = Counter(tourism_sin['Continent'])

        ind = np.arange(len(counts_continents))
        plt.barh(ind,counts_continents.values(),align='center',height=0.7)
        ax.invert_xaxis()
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        plt.title('Number of Countries on Each Continent')
        plt.yticks(ind, counts_continents.keys())

    plt.show()
    


# In[482]:

mytitle = ['Visitor Arrivals by Continent of Residence',
           'Distribution of Total Visitor Arrivals by Continent in 2007-2015']
plot_bar_box(arrivals[('sum',)],mytitle)


# <li> Step 5. Expenses of tourists

# In[830]:

receipts = tourism_sin.pivot_table(values=tourism_sin.columns[0:9],columns=['Continent'],aggfunc=[np.mean,np.sum,np.median,np.std])

decrease = [-receipts[('sum','AMERICAS')]['2014_receipt']+receipts[('sum','AMERICAS')]['2015_receipt'],
           -receipts[('sum','ASIA')]['2014_receipt']+receipts[('sum','ASIA')]['2015_receipt'],0,
           -receipts[('sum','OCEANIA')]['2014_receipt']+receipts[('sum','OCEANIA')]['2015_receipt']]
increase = [0,0,-receipts[('sum','EUROPE')]['2014_receipt']+receipts[('sum','EUROPE')]['2015_receipt'],0]

 
plt.figure()
X = np.arange(4)
plt.bar(X, increase, facecolor='#ff9999', edgecolor='white')
plt.bar(X, decrease, facecolor='#9999ff', edgecolor='white')

for x, y in zip(X, increase):
    if y ==0:
        plt.text(x + 0.4, y + 0.05, list(continents.keys())[x]+' %.2f' % decrease[x] , ha='center', va='bottom')
    else:
        plt.text(x + 0.4, y + 0.05, 'EUROPE %.2f' % y, ha='center', va='bottom')
plt.xticks([])
plt.show()


# In[540]:

mytitle = ['Tourism Receipts by Continent of Residence',
           'Tourism Receipts Per Country by Continent of Residence']
plot_bar_box(receipts[('sum',)],mytitle)


# <li> Step 6. Look into Asian Countries

# In[699]:

asian_countries = tourism_sin[tourism_sin['Continent'] == "ASIA"]


# In[681]:

# receipts
import matplotlib.gridspec as gridspec
plt.figure(figsize=(15,15))
gs = gridspec.GridSpec(3, 3)
ind = np.arange(9)
for i in ind:
    x,y = [int(i/3), i%3]
    plt.subplot(gs[x,y])
    plt.pie(asian_countries[asian_countries.columns[i]], labels=asian_countries.index, autopct='%1.1f%%',
        shadow=True, startangle=90)
    plt.title(asian_countries.columns[i])
plt.show()


# In[682]:

plt.figure(figsize=(15,15))
gs = gridspec.GridSpec(3, 3)
ind = np.arange(9)
for i in ind:
    x,y = [int(i/3), i%3]
    plt.subplot(gs[x,y])
    plt.pie(asian_countries[asian_countries.columns[i+9]], labels=asian_countries.index, autopct='%1.1f%%',
        shadow=True, startangle=90)
    plt.title(asian_countries.columns[i+9])
plt.show()


# In[772]:

def plot_asian_bar_box(data,mytitle):
    plt.figure(figsize=(10,5))
    
    ax=plt.gca()
    
    #?? doesn't work ???
    from cycler import cycler
    ax.set_prop_cycle(cycler('color', [plt.cm.RdBu(i) for i in np.linspace(0, 1, 11)]))
    
    
    # plot sum
    data1 = data[data.columns[0:9]]
    _ = np.cumsum(data1,axis=0)
    ind = np.arange(data1.shape[0])
    for i in reversed(_.index):
        plt.bar(ind,_.loc[i],width=0.8,alpha=0.8,align='center')

    #plt.title(mytitle[0]) 
    plt.xticks(ind, np.arange(2007,2016))
    ax.legend(list(reversed(_.index)),bbox_to_anchor=(-0.3, 0.5),loc='center left')
    ax.set_ylabel(mytitle[0])

    #plot arrivals
    data2 = data[data.columns[9:18]]
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', [plt.cm.RdBu(i) for i in np.linspace(0, 1, 11)]))
    ax2.plot(data2.T.as_matrix(),'-o')
    ax2.set_ylabel(mytitle[1])
    ax2.legend(list((_.index)),bbox_to_anchor=(1.1, 0.5),loc='center left')
    ax2.grid(False)
    
    plt.show()
    


# In[776]:

mytitle = ['Tourism Receipts by Country of Residence','Visitor Arrivals by Country of Residence']
plot_asian_bar_box(asian_countries,mytitle)


# <li> Step 7. Calculate travel receipts per person 

# In[700]:

for i in range(9):
    asian_countries[asian_countries.columns[i]+'_per_thousand_person'] = 1000*asian_countries[asian_countries.columns[i]]/asian_countries[asian_countries.columns[i+9]]


# In[850]:


#plot box
plt.figure()
plt.boxplot(asian_countries[asian_countries.columns[19:]].T.as_matrix(),widths=0.8,labels=asian_countries.index,sym='b+',showfliers=True)
plt.xticks(rotation=45)
plt.title('Tourism Receipts per thousand visitor')
plt.show()   


# <li> Step 8. Correlation analsis

# In[775]:

#AMERICAS	ASIA	EUROPE	OCEANIA
asian_receipts = asian_countries[asian_countries.columns[0:9]]
asian_arrivals = asian_countries[asian_countries.columns[9:18]]

for i in range(asian_countries.shape[0]):
    print(asian_countries.index[i],' ',np.corrcoef(asian_receipts.iloc[i], asian_arrivals.iloc[i])[0,1])


# <li> Step 9. Indonesia & China

# In[858]:

#Indonesia  #China

plt.figure()
plt.plot(range(9),asian_countries.loc['Indonesia'][19:].tolist(),'-o',range(9),asian_countries.loc['China'][19:].tolist(),'-o')
plt.xticks(range(9),['2007','2008','2009','2010','2011','2012','2013','2014','2015'])
plt.legend(['Indonesia','China'])
plt.ylabel('Tourism Receipts per thousand visitor')

ax1 = plt.gca().twinx()
ax1.plot(range(9),asian_arrivals.loc['Indonesia'].tolist(),'--',range(9),asian_arrivals.loc['China'].tolist(),'--')
ax1.set_ylabel('Visitor Arrivals')
#ax1.legend(list((_.index)),bbox_to_anchor=(1.1, 0.5),loc='center left')
ax1.grid(False)

plt.show()


# In[865]:

(asian_arrivals.loc['China']['2015_arrival']-asian_arrivals.loc['China']['2014_arrival'])


# In[864]:

(asian_arrivals.loc['Indonesia']['2015_arrival']-asian_arrivals.loc['Indonesia']['2014_arrival'])


# In[868]:

(asian_receipts.loc['China']['2015_receipt']-asian_receipts.loc['China']['2014_receipt'])


# In[869]:

(asian_receipts.loc['Indonesia']['2015_receipt']-asian_receipts.loc['Indonesia']['2014_receipt'])


# In[872]:

(asian_countries.loc['Indonesia'][-1]-asian_countries.loc['Indonesia'][-2])/asian_countries.loc['Indonesia'][-2]


# In[873]:

(asian_countries.loc['China'][-1]-asian_countries.loc['China'][-2])/asian_countries.loc['China'][-2]


# In[ ]:



