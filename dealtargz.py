import tarfile
import os,collections

def get_files():
    for filepath, dirnames, filenames in os.walk(r'path/to/folder'):
        for filename in filenames:
            print(os.path.join(filepath, filename))
def untar(fname, new_tex):
    """
    解压tar.gz文件
    :param fname: 压缩文件名
    :param dirs: 解压后的存放路径
    :return: bool
    """
    file_name_list=[]
    if os.path.exists(new_tex):
        return False
    try:
        # t = tarfile.open(fname)
        with tarfile.open(fname, "r") as tar:
            for member in tar.getmembers():
                member_name=member.name.split('/')[-1]
                if  member.name.endswith(".tex") and(member_name not in file_name_list):#不够准确，应该是最后一个名字不重复出现
                    with tar.extractfile(member) as f:
                        tex_content = f.read().decode("utf-8")
                    with open(new_tex, "a+") as new_file:
                        new_file.write(tex_content)
                    file_name_list.append(member_name)
        # t.extractall(path = dirs)#解压提取
        print(f"{new_tex}写入完成")
        return True
    except Exception as e:
        print(e)
        return False

pdf_base='./arxiv_papers'
tex_base='./download_tex/tex_total'
idx=0
import time
start_time=time.time()
for filepath, dirnames, filenames in os.walk(pdf_base):
    for filename in filenames:
        real_path=os.path.join(filepath,filename)
        # print(real_path)
        file_name=os.path.splitext(os.path.splitext(filename)[0])[0]+'.tex'#获取文件后缀
        new_path=os.path.join(tex_base,file_name)
        untar(real_path,new_path)
        idx+=1
        if idx==200:
            break
    if idx==200:
        break
end_time=time.time()
cost_time=end_time-start_time
print(f'共处理了{idx}篇文章,用时{cost_time}分钟')