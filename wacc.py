#necessary libraries
import streamlit as st
import numpy as np  
import pandas as pd   
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


#geomean function
def gmean(x):
    a = np.log(x)
    return np.exp(a.mean())

#importing data
erp_data = pd.read_html("https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html")[0]
tax_data = pd.read_html("https://tradingeconomics.com/country-list/corporate-tax-rate")[0]
spread_data = pd.read_html("https://www.imf.org/en/Publications/WEO/weo-database/2022/April/weo-report?c=512,914,612,171,614,311,213,911,314,193,122,912,313,419,513,316,913,124,339,638,514,218,963,616,223,516,918,748,618,624,522,622,156,626,628,228,924,233,632,636,634,238,662,960,423,935,128,611,321,243,248,469,253,642,643,939,734,644,819,172,132,646,648,915,134,652,174,328,258,656,654,336,263,268,532,944,176,534,536,429,433,178,436,136,343,158,439,916,664,826,542,967,443,917,544,941,446,666,668,672,946,137,546,674,676,548,556,678,181,867,682,684,273,868,921,948,943,686,688,518,728,836,558,138,196,278,692,694,962,142,449,564,565,283,853,288,293,566,964,182,359,453,968,922,714,862,135,716,456,722,942,718,724,576,936,961,813,726,199,733,184,524,361,362,364,732,366,144,146,463,528,923,738,578,537,742,866,369,744,186,925,869,746,926,466,112,111,298,927,846,299,582,487,474,754,698,&s=PCPIPCH,&sy=2020&ey=2027&ssm=0&scsm=1&scc=0&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1")[0]
beta_debt_data = pd.read_html("https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html")[0]
cod_data = pd.read_html("https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html")[0]
mature_market_data = pd.read_html("https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histimpl.html")[0]

#extracting the list of countries which are in both datasets
countries_first = []
for i in erp_data[0].tolist():
  if i in tax_data["Country"].tolist():
    countries_first.append(i)
countries_second = []
for i in countries_first:
  if i in spread_data["Country"].tolist():
    countries_second.append(i)
    
#extracting the list of industries which are in both datasets
industries = []
for i in cod_data[0].tolist():
  if i in cod_data[0].tolist():
    industries.append(i)
    
#starting date for the mature market risk premium
years = mature_market_data[0]

#app title
st.title("Weighted Average Cost of Capital")
st.markdown("---")

#sidebar
st.sidebar.subheader('Query parameters')
country = st.sidebar.selectbox("Select a Country:", options = countries_second)
industry = st.sidebar.selectbox("Select an Industry:", options = industries[1:])
start_date = st.sidebar.selectbox("Starting date for the Risk Premium calculation:", options = years[2:])
maturity = st.sidebar.selectbox("T-bond maturity:", options =[10,20,30])

#mature market equity risk premium
def risk_premium(data,starting_year):
  data.set_index(0,inplace = True)
  data.set_axis(data.iloc[0].tolist(),axis = 1 ,inplace = True)
  separated = []
  numbers = data.loc[str(starting_year):]["Implied ERP (FCFE)"].tolist()
  for n in numbers:
    separated.append(float(n.replace("%",""))/100)
    np.mean(separated)
  return np.mean(separated)

mature_risk_premium = risk_premium(data = mature_market_data,starting_year = start_date)



#risk free rate
def risk_free(years):
  url = f"https://www.marketwatch.com/investing/bond/tmubmusd{years}y/download-data?countrycode=bx&mod=mw_quote_tab"
  tables = pd.read_html(url)

  leng = []
  for i in tables:
    leng.append(len(i))
  delta = np.max(leng)
  f_index = leng.index(delta)

  data_range = tables[f_index]

  risk_free = data_range.iloc[0]["Close"].replace("%","")

  return float(risk_free)/100

risk_free_rate = risk_free(years = maturity)



#country risk premium
def country_risk_premium(data,country):
  try:
    data.set_index(0,inplace = True)
    data.set_axis(erp_data.iloc[0].tolist(),axis = 1 ,inplace = True)
  except:
    pass
  country_premium = float(erp_data.loc[country]["Equity Risk  Premium"].replace("%",""))/100 - float(erp_data.loc["United States"]["Equity Risk  Premium"].replace("%",""))/100
  return country_premium

risk_premium = country_risk_premium(data = erp_data, country = country)



#unlevered beta and debt/equity ratio
def beta_debt(data,industries,industry):
  try:
    data.set_index(0,inplace = True)
    data.set_axis(data.iloc[0].tolist(),axis = 1 ,inplace = True)
  except:
    pass
  index = industries.index(industry)
  unlevered_beta = float(data.iloc[index]["Unlevered beta"])
  debt_to_equity = float(data.iloc[index]["D/E Ratio"].replace("%",""))/100
  return [unlevered_beta, debt_to_equity]

unlev_beta = beta_debt(data = beta_debt_data,industries = industries,industry = industry)[0]
debt_equity_ratio = beta_debt(data = beta_debt_data,industries = industries,industry = industry)[1]



#tax rate
def corp_tax_rate(data,country):
  try:
    data.set_index("Country", inplace = True)
  except:
    pass
  rate = data.loc[country]["Last"]/100
  return rate

tax_rate = corp_tax_rate(data = tax_data,country = country)



#cost of debt
def cost_of_debt(data, industries, industry):
  try:
    data.set_index(0,inplace = True)
    data.set_axis(data.iloc[0].tolist(),axis = 1, inplace = True)
  except:
    pass
  index = industries.index(industry)
  cod = float(data.iloc[index]["Cost of Debt"].replace("%",""))/100
  return cod

cod = cost_of_debt(data = cod_data, industries = industries, industry = industry)



#currency spread
def spread(data, country):
  try:
    data.set_index("Country", inplace = True)
    data.drop(labels=["Subject Descriptor","Units","Country/Series-specific Notes","Scale","2020","2021"], axis = 1, inplace= True)
  except:
    pass
  try:
    spread = gmean(spread_data.loc[country]/100+1)-gmean(spread_data.loc["United States"]/100+1)
  except:
    spread = 0
  return spread



currency_spread = spread(data = spread_data, country = country)


st.header("Result:")


#printing materials
risk_free_rate_print = str(round(risk_free_rate,4)*100)+"%"
erp_print = str(round(mature_risk_premium,4)*100)+"%"
levered_beta = unlev_beta*(1+debt_equity_ratio*(1-tax_rate))
levered_beta_print = str(round(levered_beta,2))
debt_equity_print = str(round(debt_equity_ratio,4)*100)+"%"
crp_print = str(round(risk_premium,4)*100)+"%"
coe = risk_free_rate + round(levered_beta*mature_risk_premium + risk_premium,4)
coe_print = str(round(coe,4)*100)+"%"
tax_print = str(round(tax_rate,4)*100)+"%"
cod_print = str(round(cod,4)*100)+"%"
wacc_usd = coe/(1+debt_equity_ratio)+cod*(1-tax_rate)*(debt_equity_ratio/(1+debt_equity_ratio))
wacc_usd_print = str(round(wacc_usd,4)*100)+"%"
wacc_local = (1+wacc_usd)*(1+currency_spread)-1
spread_print = str(round(currency_spread,4)*100)+"%"
wacc_local_print = str(round(wacc_local,4)*100)+"%"



st.text("->   Risk Free Rate:" + " "*(45-len("->   Risk Free Rate:"))+ risk_free_rate_print)
st.text("->   Equity Risk Premium:"+ " "*(45-len("->   Equity Risk Premium:"))+ erp_print)
st.text("->   Levered Beta:"+ " "*(45-len("->   Levered Beta:"))+ levered_beta_print)
st.text("->   Debt/Equity:"+ " "*(45-len("->   Debt/Equity:"))+ debt_equity_print)
st.text("->   Country Risk Premium:"+ " "*(45-len("->   Country Risk Premium:"))+ crp_print)
st.text("->   Cost of Equity:"+ " "*(45-len("->   Cost of Equity:"))+ coe_print)
st.text("->   Corporate Tax Rate:"+ " "*(45-len("->   Corporate Tax Rate:"))+ tax_print)
st.text("->   Cost of Debt:"+ " "*(45-len("->   Cost of Debt:"))+ cod_print)
st.text("->   WACC, in USD:"+ " "*(45-len("->   WACC, in USD:"))+ wacc_usd_print)
if spread == 0:
    pass
else:
    st.text("->   Currency Spread:"+ " "*(45-len("->   Currency Spread:"))+ spread_print)
    st.text("->   WACC, in local currency:"+ " "*(45-len("->   WACC, in local currency:"))+ wacc_local_print)











