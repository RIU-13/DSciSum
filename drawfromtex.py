import time
import os,re,json
idx=0
start_time=time.time()
def draw_text_newcommand(text:str):
    #\newcommand{\⟨name⟩}[⟨num⟩]{⟨definition⟩}
    text=text.strip()
    pattern = r"\\newcommand\{(.+?)\}\{(.+?)\}"
    # 使用re.search()方法在字符串中搜索匹配
    match = re.search(pattern, text)
    key=None
    value=None
    # 如果找到匹配，打印出命令名和具体定义
    if match:
        # print("命令名:", match.group(1))
        key=match.group(1)
        newtxt_idx =text.find(key)+len(key)+2#从}{下一个快开始
        newtext = text[newtxt_idx:-1]
        newtext = re.sub(r'\\textcolor\{(.*?)\}',"",newtext)
        newtext= re.sub(r'\\text[a-zA-Z]{2}\{(.*?)\}', r'\1', newtext)#{2}表示匹配前面的两次，也就是两个英文字母
        newtext = re.sub(r'\$[^\$]*\$',"",newtext)#去掉$ $之间的
        newtext = re.sub(r'\\xspace',"",newtext)
        value=re.sub(r'\{(.*?)\}',r'\1',newtext)
        # print("具体定义:", value)
    return key,value

def remove_textbf(text):
    newtext= re.sub(r'\\text[a-zA-Z]{2}\{(.*?)\}', r'\1', text)
    newtext = re.sub(r'\$[^\$]*\$',"",newtext)#去掉$ $之间的
    newtext = re.sub(r"\\bf(series)?", "", newtext)
    newtext = re.sub(r"\\[a-zA-Z]*rule.*?[ \n]"," ",newtext)
    newtext = re.sub(r"\\[a-zA-Z]*font[a-zA-Z]*.*?[ \n]"," ",newtext)#去掉字体大小
    newtext = re.sub(r"\[-?[0-9a-zA-Z]+em\]", "", newtext)#[-1em]
    newtext = newtext.replace("\\small"," ")
    newtext = newtext.replace("\\centering"," ")
    newtext = re.sub(r'\\ref\{.*?\}',"",newtext)
    return newtext
def remove_latex_syntax(text: str) -> str:
    #去掉\xxx{}样式的句子
    # pattern = re.compile(r'\\[a-zA-Z]+\{[^\}]*\}')#[]匹配其中任意一个字符,^表示取反,*表示匹配前面的字符0次或多次。
    # #[^\}]表示匹配除了\}之外的任意字符0次或多次
    # p2=re.compile(r'\\[a-zA-Z]+ ')
    newtext = re.sub(r'\\cite[p]?\{.*?\}',"",text)
    newtext = re.sub(r'\\label\{.*?\}',"",newtext)
    newtext = re.sub(r'\\ref\{.*?\}',"",newtext)
    newtext = re.sub(r'\\url\{.*?\}',"",newtext)
    newtext = re.sub(r'\\foot[a-zA-Z]*\{(.*?)\}',"",newtext)
    newtext= re.sub(r'\\text[a-zA-Z]{2}\{(.*?)\}', r'\1', newtext)
    newtext = re.sub(r'\\text\{(.*?)\}',r'\1',newtext)
    newtext = re.sub(r'\\[a-zA-Z]+\{(.*?)\}',r'\1',newtext)
    # return p2.sub('',pattern.sub('', text))
    return newtext
def deal(paper:dict)->(dict,dict):
    newpaper={}
    newtable_paper={}
    newpaper["arxiv_id"]=paper["arxiv_id"]
    newtable_paper["arxiv_id"]=paper["arxiv_id"]
    newpaper["title"]=paper["title"].replace("\\\\","")
    introSen=""
    try:
        for sen in paper["introduction"]:
            introSen+=sen
            introSen+='\n'
    except:
        print("noIntro")
    newpaper["introduction"]=introSen
    conSen=""
    try:
        for sen in paper["conclusion"]:
            conSen+=sen
            conSen+='\n'
    except:
        print("noConclu")
    newpaper["conclusion"]=conSen
    resSen=""
    try:
        for sen in paper["results"]:
            resSen+=sen
            resSen+='\n'
    except:
        print("noRes")
    newpaper["results"]=resSen
    newpaper["table"]=[]
    newtable_paper["table"]=[]
    for table in paper["table"]:
        source_seq=table['content'][0]
        # if len(source_seq)>512:
        #     continue
        newpaper["table"].append(table)
        newtable_paper["table"].append(table)
    newpaper["abstract"]=paper["abstract"][0]
    newpaper["sources"]=paper["sources"]
    if resSen=="" and newpaper["table"]==0:#对数字化信息提取无意义
        return None,None
    return newpaper,newtable_paper

def getkeyInfoTable(real_path:str,source:dict)->dict:
    #获取需要的信息和表格信息
    paper={}
    paper["arxiv_id"]=real_path.split('/')[-1][:-4]
    paper["title"]=""
    paper["introduction"]=[]#一段话
    paper["conclusion"]=[]#一段话
    paper["results"]=[]
    paper["table"]=[]
    paper["abstract"]=[]#一段话
    paper["method"]=[]
    sources=""
    for page in source.values():
        sources+=page
    tableidx=0
    newcommand={}
    paper["sources"]=sources
    # import ipdb
    # ipdb.set_trace()
    
    with open(real_path,encoding="utf-8")as f:
        tableWrite=0
        beginsec=0
        secWrite=0
        beginFig=0
        beginTabular=0
        writeTabular=0
        total_lines=f.readlines()
        for line in total_lines:
            if line.startswith('\\newcommand{'):
                newkey,value=draw_text_newcommand(line)
                newcommand[newkey]=value#记录newcommand命令，之后处理
        # import ipdb
        # ipdb.set_trace()
        for line in total_lines:
            #%开头的是注释
            l=line.strip()
            #进行newcommand替换，应该是不需要管标点符号的
            for newkey,newvalue in newcommand.items():
                if newkey!=None:
                    l=l.replace(newkey,newvalue)
            if len(l)>0 and l[0]=='%':
                continue
            elif len(l)==0:
                continue
            elif l.startswith('\\title'):
                # import ipdb
                # ipdb.set_trace()
                l=remove_latex_syntax(l[7:-1])
                paper["title"]=l
            elif l.startswith('\\icmltitle'):
                paper["title"]=remove_latex_syntax(l[11:-1])  
            elif l.startswith('\\section')or l.startswith('\\subsection') or l.startswith('\\subsubsection') or l.startswith('\\appendix'):
                sec_name=l
                beginsec=1
                secWrite=1
                # import ipdb
                # ipdb.set_trace()
                if re.search(r"intro|purpose", sec_name.lower()):
                    key = "introduction"
                elif re.search(r"conclu|future",sec_name.lower()):
                    key = "conclusion"
                elif re.search(r"experiment|result|dataset|evalua",sec_name.lower()):
                    key = "results"
                elif re.search(r"method|tech"):
                    key="methods"
                elif re.search(r"acknow",sec_name.lower()):
                    break
                else:
                    secWrite=0
            elif re.search(r'\\begin{table',l):
                #表格
                tableWrite=1
                #新建一个表格list
                table={}
                table["head"]=tableidx
                table["caption"]=""
                table["content"]=[]
                total_sentences=""
                pattern = re.compile(r'\\cite+\{[^\}]*\}')
                sen_noCite=pattern.sub('', l)
                sen_noTB=remove_textbf(sen_noCite)
                sen_noTB+='\n'
                total_sentences+=sen_noTB
            elif re.search(r'\\end{table',l):
                # import ipdb
                # ipdb.set_trace()
                if writeTabular==1: 
                    try:
                        pattern = re.compile(r'\\cite+\{[^\}]*\}')
                        sen_noCite=pattern.sub('', line)
                        sen_noTB=remove_textbf(sen_noCite)
                        sen_noTB+='\n'
                        total_sentences+=sen_noTB
                        total_sentences=total_sentences.replace("\\\\", "TEMP").replace("\\", "").replace("TEMP", "\\\\")#去掉所有\, 保留所有\\
                        total_sentences=re.sub(r"\s+", " ", total_sentences)
                        table["content"].append(total_sentences)#一个list，一段话
                        # pattern = re.compile(r'\\cite+\{[^\}]*\}')
                        # table["content"].append(pattern.sub('', l))#在table的内容中加入结束符
                        paper['table'].append(table)#加入到table中
                    except:
                        print("error")
                tableWrite=0
                beginTabular=0
                tableidx+=1
                writeTabular=0
            # elif l.startswith('\\subsubsection'):
            #     l = l[14:-1]
            elif re.search(r'\\begin{abstract',l):
                key="abstract"
                beginsec=1
                secWrite=1
            elif re.search(r'\\end{abstract}',l):
                beginsec=0
                secWrite=0
            elif re.search(r'\\begin{figure',l) or re.search(r'\\begin{equat',l) or re.search(r'\\begin{thebibliograph',l):
                #去掉所有图的信息
                beginFig=1
            elif re.search(r'\\end{figure',l) or re.search(r'\\end{equa',l)or re.search(r'\\end{thebibliograph',l):
                beginFig=0
            elif re.search(r'\\begin{tabu',l) and tableWrite==1 and beginTabular==0:
                beginTabular=1
            elif re.search(r'begin{acknow',l.lower()) or re.search(r'section\*{acknow',l.lower()) or re.search(r'section{acknow',l.lower()) or re.search(r'\\appendix',l.lower()):
                break
            elif tableWrite!=1:
                beginsec=0
                l = remove_latex_syntax(l)
                l=l.replace("\\item "," ")
            #判断完成,下面是根据判断进行处理
            if tableWrite==1:#在读表格
                if re.search(r'\\caption{',l):
                    table["caption"]=remove_latex_syntax(l)
                    table["caption"]=re.sub(r'\\caption\{(.*?)\}',r'\1',table["caption"])
                elif beginTabular:
                    writeTabular=1
                    pattern = re.compile(r'\\cite+\{[^\}]*\}')
                    sen_noCite=pattern.sub('', line)
                    sen_noTB=remove_textbf(sen_noCite)
                    sen_noTB+='\n'
                    total_sentences+=sen_noTB
                    # pattern = re.compile(r'\\cite+\{[^\}]*\}')#去掉所有cite
                    # table["content"].append(pattern.sub('', l))#还没试验
                # table["content"].append(l)
                # elif l.startswith('\\begin{tabular}'):
                #     table["content"].append(l)
                #     tabularWrite=1
                # elif l.startswith('\\end{tabular}'):
                #     table["content"].append(l)
                #     tabularWrite=0
                # elif tabularWrite==1:
                #     table["content"].append(l)
            elif beginFig==1:
                continue
            elif beginsec!=1 and secWrite==1:#在写section
                # import ipdb
                # ipdb.set_trace()
                if l:
                    paper[key].append(l)
    results=paper["results"]
    # import ipdb
    # ipdb.set_trace()
    newresults=[]
    for sentence in results:
        if re.search(r"perform|than|evalu|gain|score", sentence.lower()):
            newresults.append(sentence.replace("\n"," "))
    if newresults==[]:
        for sentence in results:
            if re.search(r"dataset", sentence.lower()):
                newresults.append(sentence.replace("\n"," "))
    # import ipdb
    # ipdb.set_trace()
    # if newresults==[]:
    #     return None
    paper["results"]=newresults
    newabs=[]
    newsen=""
    for sen in paper["abstract"]:
        newsen+=sen
    newabs.append(newsen)
    paper["abstract"]=newabs#把abstract变成一句话
    #筛选table
    newtable=[]
    for table in paper["table"]:
        cap = table["caption"]
        if re.search(r"ablation|abaltion",cap.lower()):
            #消融实验和进行比较的表格暂时不要
            continue
        if re.search(r"perform|result|gain|score|dataset", cap.lower()):
            newtable.append(table)
    if len(newtable)==0 and len(newresults)==0:
        return None
    paper["table"]=newtable     
    if paper["title"]==[]:
        return None  
    return paper
if __name__ == '__main__':                   
    total_paper=[]
    total_table=[]#提取arxiv_id和table
    # txt_path = "./txt"
    # txt_files = os.listdir(txt_path)
    arxiv_total={}
    tex_base='./download_tex/tex_total'
    # for file in txt_files:
    #     paper_id=os.path.splitext(file)[0]
    #     print(paper_id)
    #     file_path = os.path.join(txt_path, file)
    #     arxiv_total[paper_id]=json.load(open(file_path,encoding='utf-8'))

    for filepath, dirnames, filenames in os.walk(tex_base):
        for filename in filenames:
            real_path=os.path.join(filepath,filename)
            paper_id=os.path.splitext(filename)[0]
            # print(real_path)
            # import ipdb
            # ipdb.set_trace()
            paper=getkeyInfoTable(real_path,arxiv_total[paper_id])
            if paper==None:
                continue
            paper,table_paper=deal(paper)
            if paper==None:
                continue
            idx+=1
            print(real_path)
            total_paper.append(paper)
            total_table.append(table_paper)
             
    with open('tex2json.json','a+',encoding='utf-8')as f:
        json.dump(total_paper,f) 
    # with open('test_tables.json','a+',encoding='utf-8')as f:
    #     json.dump(total_table,f)                   
    end_time=time.time()
    cost_time=end_time-start_time
    print(f'共处理了{idx}篇文章,用时{cost_time}分钟')#122