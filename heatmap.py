import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# encoding:utf-8
# 根据您选择的AK以为您生成调用代码
# 检测到您当前的AK设置了IP白名单校验
# 您的IP白名单中的IP非公网IP，请设置为公网IP，否则将请求失败
# 请在IP地址为0.0.0.0/0 外网IP的计算发起请求，否则将请求失败
def search(address):
    # 服务地址
    host = "https://api.map.baidu.com"
    # 接口地址
    uri = "/geocoding/v3"
    # 此处填写你在控制台-应用管理-创建应用后获取的AK
    ak = ""
    params = {
        "address": address,
        "output": "json",
        "ak": ak,
    }
    response = requests.get(url = host + uri, params = params)
    if response:
        print(response.json())
        return response.json()

def heatmap(data_name, sheet_names, save_name):
    # 读取地址数据文件到pandas DataFrame
    data_file = pd.ExcelFile(data_name)
    data = data_file.parse(sheet_names)
    #拼接各个数据形成新的属性 Address
    data["address"] = data["收件人地址"] + "省" + data["市_"] + "市" + data["区_"] + "区" + data["街道以下_"]
    data["address"] += data["大道/路"].apply(lambda x: "" if pd.isna(x) or x == "" else x)
    data["address"] += data["小区/大厦"]
    #去除地址为null的数据
    data = data.dropna(subset=["address"])
    data["count"] = data.groupby("address")["address"].transform("count")
    # 对数据进行去重
    data = data.drop_duplicates(subset=["address"]).reset_index(drop=True)
    data.reset_index(drop=True)
    # 将地址转换为经纬度并添加到pandas DataFrame中
    latitudes = []
    longitudes = []
    for address in data["address"]:
        location = search(address)
        if location is None:
            latitudes.append(np.nan)
            longitudes.append(np.nan)
        else:
            latitudes.append(location['result']['location']['lat'])
            longitudes.append(location['result']['location']['lng'])
    data.insert(len(data.columns), "latitude", latitudes) #纬度
    data.insert(len(data.columns), "longitude", longitudes) #经度
    # 创建folium Map对象并添加热力图
    m = folium.Map(location=[np.nanmean(data["latitude"]), np.nanmean(data["longitude"])], zoom_start=12)
    heat_data = [[row["latitude"], row["longitude"], row["count"]] for index, row in data.iterrows()]
    HeatMap(heat_data).add_to(m)

    # 保存热力图到HTML文件
    m.save(save_name)

data_name = "热力图地址全.xlsx"
sheet_names = "南山区其他街道C客资料"
save_name = "南山区其他街道C客资料.html"

heatmap(data_name, sheet_names, save_name)