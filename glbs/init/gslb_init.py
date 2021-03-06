# -*- coding: utf-8 -*-
from glbs.models import tb_fact_nameid_info

from glbs.utils.download import urllib_get
from glbs.policy.detect_device_availability_policy import detect_device_availability
from glbs.detect.vipdevice_availability_data import load_device_availability_cache
from glbs.detect.vipdevice_availability_data import load_detect_vipdevice_cache
from glbs.detect.vipdevice_availability_data import load_device_switch_cache

#from glbs.config import config.conf

from glbs.qdns.nameid import ViewClass
from glbs.qdns.nameid import NameidClass

from glbs.utils.glbscache import read_from_cache,write_to_cache


from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


import logging
logger = logging.getLogger('dj')
import json

def serialize_instance(obj):
     d = {}
     d.update(vars(obj))
     return d


#初始化加载nameid
def load_data(url):
    logger.info(url)
    data = urllib_get(url)
    if data is None:
        return
    datastr = str(data,encoding = "utf8")
    obj = json.loads(datastr)
    logger.info(data)
    return obj
@register_job(scheduler, "interval", seconds=10)
def load_confignameid_from_table():
    objs = tb_fact_nameid_info.objects.all()
    for obj in objs:
        if obj.nameid_name is not None and obj.nameid_policy is not None and obj.nameid_status == 'enable':
            #这个是获取所有view信息的，会以view的id为key,view的元信息为value.是从dimension_view表中取得的信息
            url = "{}/{}/".format("http://10.224.10.63:8000/getitembynameid_inner",obj.id)
            nameid_view_data = load_data(url)
            if nameid_view_data is None or nameid_view_data.get("results") is None:
                continue
            obj_list = nameid_view_data["results"]
            nameid_view_dict = {}
            for item in obj_list:
                viewobj = ViewClass().genobj(item)
                nameid_view_dict[item["nameid_view_id"]] = viewobj
            logger.info(json.dumps(nameid_view_dict,default=serialize_instance))
            #这个是获取所有view和device信息的，是通过 diomension_view_device表中取得的，这里会有详细的nameid_name,device_name，也有view_id,这里会用上面的view_id进行替换。形成最终的信息。
            url = "{}/{}/".format("http://10.224.10.63:8000/getnamedevinfo/",obj.id)
            nameid_device_data = load_data(url)
            if nameid_device_data is None or nameid_device_data.get("results") is None:
                continue
            obj_list = nameid_device_data["results"]
            nameidobj = NameidClass()            
            nameid_name = nameidobj.genobj(obj_list,nameid_view_dict)
            logger.info(json.dumps(nameidobj.nameid_data_dict,default=serialize_instance))   
            logger.info(nameid_name)
            #这个是获取所有view和cname信息的，是通过dimension_view_cname表中取得的，这里会有详细的cname信息，同样是去填充上面的类中的cname信息。
            url = "{}/{}/".format("http://10.224.10.63:8000/getnamecnameinfo/",obj.id)
            nameid_cname_data = load_data(url)
            if nameid_cname_data is None or nameid_cname_data.get("results") is None:
                continue
            obj_list = nameid_cname_data["results"]
            nameid_name = nameidobj.genobj(obj_list,nameid_view_dict)
            logger.info(json.dumps(nameidobj.nameid_data_dict,default=serialize_instance))
            logger.info(nameid_name)
            #最终nameidobj中存储的就是配置的view和每个view中对应的设备或者cname信息。后面的都是基于此来做解析的。会以nameid_name为key,它的元信息为value存入到cache中
    
            default_nameidobj = NameidClass()
#            default_nameidobj.gen_default(nameidobj)
#            logger.info(json.dumps(default_nameidobj.nameid_data_dict,default=serialize_instance))
#            logger.info(nameidobj)
#            write_to_cache(nameid_name,nameidobj)
#            logger.info("read from cache!!!!!!!!!!!!!")
#            logger.info(read_from_cache(nameid_name))
#设备可用性策略
@register_job(scheduler, "interval", seconds=10)
def update_nameid_from_disablepolciy():
    objs = tb_fact_nameid_info.objects.all()
    for obj in objs:
        if obj.nameid_name is not None and obj.nameid_policy is not None and obj.nameid_status == 'enable':
            detect_device_availability(obj.id)
#        load_config(obj.id)

#定时加载系统外部数据
@register_job(scheduler, "interval", seconds=10)
def load_extradata_device_availability():
    load_device_availability_cache() 


#定时加载探测外部数据
@register_job(scheduler, "interval", seconds=10)
def load_extradata_device_detect():
    load_detect_vipdevice_cache()

#定时加载设备开关
@register_job(scheduler, "interval", seconds=10)
def load_extradata_device_switch():
    load_device_switch_cache()

register_events(scheduler)
