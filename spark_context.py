import pyspark
import json
import os
import socket
import netifaces as ni
from pyspark.sql import SparkSession

with open("package.json") as fin:
    package_data = fin.read()
    package_data = json.loads(package_data)

spark_config = package_data["config"]["spark"]

sc = None
def get_spark_context():
    global sc
    if sc != None: return sc

    # get socket matches
    matches = [i[1] for i in socket.if_nameindex() if i[1]==spark_config["local-interface"]]
    if len(matches) != 1:
        raise "No interface called..." + spark_config["local-interface"]
    match = matches[0]
    ip = ni.ifaddresses(match)[ni.AF_INET][0]['addr']

    sc = SparkSession.builder.master(spark_config["master"]).appName("Calibration")\
        .config("spark.executor.instances", "4")\
        .config("spark.executor.cores", "4")\
        .getOrCreate().sparkContext

    os.environ["SPARK_LOCAL_IP"] = ip# "10.0.0.109"

    for dep_file_path in spark_config["project_file_dependencies"]:
        sc.addFile(dep_file_path)
    return sc

print("sc context imported")