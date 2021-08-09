import requests
import pandas as pd
from io import StringIO
import datetime
import os
from datetime import date
import json
import numpy as np
import plotly.graph_objects
from plotly.offline import plot
import plotly.express as px
from plotly.subplots import make_subplots


stock_i = input('Please entry stock ID：')
stock_id = stock_i + ".TW"


def stock_data():
    days = 24 * 60 * 60
    now = date.today()
    cur_date = now.strftime('%Y-%m-%d')
    time_start = "2015-01-01"
    time_end = cur_date
    initial = datetime.datetime.strptime('1970-01-01', '%Y-%m-%d')
    start = datetime.datetime.strptime(time_start, '%Y-%m-%d')
    end = datetime.datetime.strptime(time_end, '%Y-%m-%d')
    period1 = start - initial
    period2 = end - initial
    p1 = period1.days * days
    p2 = period2.days * days
    source_url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_id}?period1={str(p1)}&period2={str(p2)}&interval=1d&amp;events=history&amp;includeAdjustedClose=true"
    df = pd.read_csv(source_url)
    data = df.drop(columns="Adj Close")
    return data

df = stock_data()
print(df)

def generate_MA(day=5):
  CLOSE = [ x for x in df['Close'] ]
  MA = [np.array(CLOSE[i:i+day]).mean() for i in range(0,len(CLOSE)-day)]
  MA = [0]*day + MA
  MA = np.array(MA)
  return MA

df['5MA'] = generate_MA(5)
df['10MA'] = generate_MA(10)
df['20MA'] = generate_MA(20)
df['60MA'] = generate_MA(60)
df['120MA'] = generate_MA(120)
df['240MA'] = generate_MA(240)

sub_df = df[-360:]


fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing = 0.005, row_heights=[0.8, 0.2])

fig.add_trace(
    plotly.graph_objects.Candlestick(
      x=sub_df['Date'],
      open=sub_df['Open'],
      high=sub_df['High'],
      low=sub_df['Low'],
      close=sub_df['Close'],
      name='盤後資訊',
      increasing_line_color= '#F08080', decreasing_line_color= '#87E0B1'
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=[float(sub_df['Close'].tail(1))]*sub_df['Date'].shape[0],
      name='最新收盤價',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#BFC9CA', dash='dash')
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=sub_df['5MA'],
      name='  5日均線',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#FAD7A0')
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=sub_df['10MA'],
      name=' 10日均線',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#AED6F1')
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=sub_df['20MA'],
      name=' 20日均線',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#D2B4DE')
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=sub_df['60MA'],
      name=' 60日均線',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#3498DB')
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=sub_df['120MA'],
      name='120日均線',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#45B39D')
    ), row=1, col=1
)
fig.add_trace(
    plotly.graph_objects.Scatter(
      x=sub_df['Date'],
      y=sub_df['240MA'],
      name='240日均線',
      mode='lines',
      line=plotly.graph_objects.scatter.Line(color='#CD6155')
    ), row=1, col=1
)

colors = ['#F5B7B1' if x<0 else '#87E0B1' for x in sub_df['Close']-sub_df['Open']]
fig.add_trace(plotly.graph_objects.Bar(x=sub_df['Date'], y=[x for x in sub_df['Volume']], marker={'color': colors}, name='成交量'), row=2, col=1)

fig.update_layout(xaxis_rangeslider_visible=False, xaxis = dict(type="-"))

all_date = pd.date_range(start=df['Date'].iloc[0],end=df['Date'].iloc[-1])
all_date = [str(x).split(' ')[0] for x in all_date]
my_date = [x for x in sub_df['Date']]
dt_breaks = [d for d in all_date if d not in my_date]
fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
fig.update_xaxes(tickformat='%Y-%m-%d', showgrid=False)
fig.show()

def financial_data():
    source_url = f'https://www.wantgoo.com/stock/{stock_i}/financial-statements/monthly-revenue-data'
    headers = {'user-agent':'Mozilla/5.0'}
    response = requests.get(source_url,headers = headers)
    data = json.loads(response.text)

    df = pd.DataFrame()
    for item in data:
        item = {x:[y] for x,y in item.items()}
        new_df = pd.DataFrame(item)
        df = pd.concat([df,new_df],ignore_index=True)
    df['stockNo'] = pd.DataFrame({'stockNo':[int(str(x).strip()) for x in df['stockNo']]})
    print(df[['date','monthRevenue','preMonthRevenueDiff']])


    fig = px.bar(data, x='date', y='monthRevenue')
    fig.update_traces(marker_color='#8ABED0')
    fig.update_layout(xaxis_rangeslider_visible=True, xaxis=dict(type="-"))
    fig.show()
def company_info():
    source_url = f'https://marketinfo.api.cnyes.com/mi/api/v1/TWS:{stock_i}:STOCK/info'
    headers = {'user-agent': 'Mozilla/5.0'}
    response = requests.get(source_url, headers=headers)
    info = json.loads(response.text)

    data = stock_data()
    print({x:info['data'][y] for x,y in zip(['Stock ID','Company Name','Stock Type','Industry','Description'],['symbolId','companyName','stockType','industryType','description'])})




financial_data()
company_info()







