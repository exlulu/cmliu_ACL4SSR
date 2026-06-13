import os
import glob
import shutil
import zipfile
import requests
import re

# 1. 明确下载地址（直接保存为固定的临时名字，不影响解压内容）
url = "https://github.com/ipverse/asn-ip/archive/refs/heads/master.zip"
r = requests.get(url)
temp_zip = "downloaded_temp.zip"
with open(temp_zip, "wb") as code:
  code.write(r.content)

# 2. 解压zip文件，并动态捕获解压出来的真实文件夹名称
with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
  # 压缩包内文件的第一个路径，其第一级目录就是解压后的真实根目录
  first_item = zip_ref.namelist()[0]
  extracted_dir = first_item.split('/')[0]
  zip_ref.extractall(".")

print(f"系统检测到实际解压出的文件夹名称为: {extracted_dir}")

# 将结果存储在这个列表中
ip_addresses = []
included_asns = ['209242', '13335', '149648', '132892', '139242', '202623', '203898', '394536']

# 3. 动态拼接路径并遍历
target_dir = os.path.join(extracted_dir, "as")
if os.path.exists(target_dir):
  for root, dirs, files in os.walk(target_dir):
    if 'ipv4-aggregated.txt' in files:
      # 跨平台自动提取最后一级文件夹名（即 ASN 号）
      asn = os.path.basename(root)
      if asn in included_asns:
        with open(os.path.join(root, 'ipv4-aggregated.txt'), 'r') as file:
          ips = file.read().splitlines()
          ip_addresses.extend(ips)

# 正则表达式用于匹配IPv4地址和子网掩码
ipv4_regex = re.compile(r'^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})$')

# 4. 确保输出目录存在
os.makedirs("Clash", exist_ok=True)

# 5. 将结果写入两个文件
with open('Clash/CloudflareCIDR.list', 'w') as clash_file, \
     open('CloudflareCIDR.txt', 'w') as cidr_file:
  cidr_file.write("payload:\n")
  for ip in ip_addresses:
    if ipv4_regex.match(ip):
      clash_file.write(f"IP-CIDR,{ip},no-resolve\n")
      cidr_file.write(f"{ip}\n")
    else:
      clash_file.write(f"{ip}\n")

# 6. 清理临时文件（使用通配符安全清理残留）
if os.path.exists(temp_zip):
  os.remove(temp_zip)

# 使用 glob 通配符寻找包含 "-blocks-" 或 "asn-ip-" 甚至是任何动态捕获到名字的解压文件夹并清理
for folder in glob.glob("*-blocks-*") + glob.glob("asn-ip-*") + [extracted_dir]:
  if os.path.exists(folder) and os.path.isdir(folder):
    shutil.rmtree(folder)
    print(f"成功清理临时文件夹: {folder}")
