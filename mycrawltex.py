import os
import requests
# hd={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
hd={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
def download_pdf(paper_id,save_dir_pdf):
    api_url = f'http://export.arxiv.org/api/query?id_list={paper_id}'
    response = requests.get(api_url)
    xml_content = response.text
    start_idx = xml_content.find('<link title="pdf" href="') + len('<link title="pdf" href="')
    end_idx = xml_content.find('" type="application/pdf"/>', start_idx)
    url = xml_content[start_idx:end_idx]
    pdf_url = url.replace("abs", "pdf") + ".pdf"
    print(pdf_url)
    page = requests.get(pdf_url)
    save_path_pdf = os.path.join(save_dir_pdf,f'{paper_id}.pdf')
    with open(save_path_pdf,'wb')as f:
        f.write(page.content)
    print(f'Successfully downloaded PDF source for paper {paper_id}.')
    
def download_arxiv_latex(paper_ids, save_dir='./arxiv_papers',save_dir_pdf='./download_pdf'):
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(save_dir_pdf,exist_ok=True)
    # paper_id=str(paper_id).replace("[","\"").replace("]","\"")
    # 构建 arXiv API 请求 URL
    idx=0
    for paper_id in paper_ids:
        idx+=1
        lex_file_path=paper_id+".tar.gz"
        pdf_file_path=paper_id+".pdf"
        if os.path.exists(os.path.join(save_dir,lex_file_path)):
            #只要下载pdf
            # if os.path.exists(os.path.join(save_dir_pdf,pdf_file_path)):
            #     continue
            # download_pdf(paper_id,save_dir_pdf)
            continue
    
        api_url = f'http://export.arxiv.org/api/query?id_list={paper_id}'#http://export.arxiv.org/api/query?id_list=2006.03265v2 
    
        # 发送 API 请求
    #  for entry in response.text.split("<entry>"):
    #     if "<id>" in entry and "<link title=\"pdf\"" in entry:
    #         pdf_url = entry.split("<id>")[1].split("</id>")[0]
    #         pdf_url = pdf_url.replace("abs", "pdf") + ".pdf"
    #         pdf_urls.append(pdf_url)

    # # Download the PDFs
    # for pdf_url in pdf_urls:
    #     response = requests.get(pdf_url)
    #     with open(pdf_url.split("/")[-1], "wb") as f:
    #         f.write(response.content)
        response = requests.get(api_url,headers=hd)
        if response.status_code == 200:
            
            # 解析 API 响应，获取 LaTeX 源代码链接
            xml_content = response.text
            start_idx = xml_content.find('<link title="pdf" href="') + len('<link title="pdf" href="')
            end_idx = xml_content.find('" rel="related" type="application/pdf"/>', start_idx)
            url = xml_content[start_idx:end_idx]
            # 构建 LaTeX 源代码链接
            # latex_url = url.replace('/pdf/', '/e-print/')# + '.tar.gz'
            latex_url=url.replace('/pdf/','/src/')
            # pdf_url = url.replace("abs", "pdf")# + ".pdf"
           
            # print(pdf_url)#http://arxiv.org/pdf/2004.01972v2" rel="related.pdf   
            print(latex_url)#http://arxiv.org/e-print/2004.01972v2" rel="related.tar.gz  
            # page = requests.get(pdf_url)
            # save_path_pdf = os.path.join(save_dir_pdf,f'{paper_id}.pdf')
            # with open(save_path_pdf,'wb')as f:
            #     f.write(page.content)
            # print(f'Successfully downloaded PDF source for paper {paper_id}.')

            # 下载 LaTeX 源代码-------------------------------------
            latex_response = requests.get(latex_url,headers=hd)
            # import ipdb
            # ipdb.set_trace()
            if latex_response.status_code == 200:
                # 保存 LaTeX 源代码到文件
                save_path = os.path.join(save_dir, f'{paper_id}.tar.gz')
                with open(save_path, 'wb') as file:
                    file.write(latex_response.content)
                print(f'Successfully downloaded LaTeX source for paper {paper_id}.')
                # page = requests.get(pdf_url,headers=hd)
                # save_path_pdf = os.path.join(save_dir_pdf,f'{paper_id}.pdf')
                # with open(save_path_pdf,'wb')as f:
                #     f.write(page.content)
                # print(f'Successfully downloaded PDF source for paper {paper_id}.')
            else:
                print(f'Failed to download LaTeX source for paper {paper_id}.')
        else:
            print(response)
            print(f'Failed to fetch paper details for {paper_id} from arXiv API.')
        #-----------------------------------------------------------------------------
        

# 示例使用：下载论文 ID 为 "2101.00123" 的 LaTeX 源代码

import urllib, urllib.request
# url = 'https://export.arxiv.org/api/query?search_query=cat:cs.CL+AND+submittedDate:[20210101+TO+20231110]&start=500&max_results=500
url='https://export.arxiv.org/api/query?search_query=submittedDate:[20220101+TO+20241110]&start=0&max_results=5000'

#60000 max_results是本次会下载的论文数量
# import http.client
# http.client.HTTPConnection._http_vsn = 10
# http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
#url应该是list
data = urllib.request.urlopen(url)

# print(data.read().decode('utf-8'))#是atom1.0格式的数据
import feedparser
import json
import time
import threading
from collections import defaultdict
import random
d = feedparser.parse(data)
idlist=[]
taglist=defaultdict(int)
random.shuffle(d['entries'])
print('length of entries',len(d['entries']))
for paper in d['entries'][:1000]:
    id = paper['id'][21:]#id就是网址
    tags=paper['arxiv_primary_category']['term']
    idlist.append(id)
    taglist[tags]+=1
    
print('len of idlist',len(idlist))
import logging


def write_dict_to_log(dictionary):
    # 配置日志记录器
    logging.basicConfig(filename='taglist.log', level=logging.INFO, format='%(message)s')
    # 将字典内容转换为字符串
    dict_str = str(dictionary)
    # 写入日志
    logging.info(dict_str)


write_dict_to_log(taglist)
start_time=time.time()
idx=0
# idlist=["2107.08929v2","2211.10247v2","2005.00513v2","2106.00130v2","2303.16634v3"]
part1,part2,part3,part4=[],[],[],[]
length = len(idlist)
for file in idlist:
    # file_path = os.path.join(path, file)
    idx+=1
    if idx<=0.25*length:
        part1.append(file)
    elif idx<=0.5*length:
        part2.append(file)
    elif idx<=0.75*length:
        part3.append(file)
    elif idx<=length:
        part4.append(file)
    else:
        break
all_part=[part1,part2,part3,part4]
threads = []
for file_list in all_part:
    thread = threading.Thread(target=download_arxiv_latex, args=([file_list]))#不加[]会显示有25个文件
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
# download_arxiv_latex(idlist)
end_time=time.time()
cost_time=end_time-start_time
print(len(idlist))
print(f'耗时{cost_time/60}分钟')
