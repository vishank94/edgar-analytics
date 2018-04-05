
# coding: utf-8

# In[3]:


#JGJ JSR


# In[4]:


#importing required libraries
import csv
import pandas as pd
from collections import deque
from datetime import datetime


# In[5]:


#reads a line (the stream) at a time as a df, returns that df
def read_line(line,stream):
    line = line.split(",")
    namedline = [line[n] for n in {0,1,2,4,5,6}] 
    for (c,word) in zip(stream.columns,namedline):
        stream.loc[0,c] = word
    return stream


# In[21]:


#computes the timespan between first and last request of the user to get the session duration in secs
def time_between(d2, d1):
    day_diff = (int(abs((d2 - d1).days)))
    sec_diff = (int(abs((d2 - d1).seconds)))
    if day_diff == 0: #same day or different day but within 24 hours
        return sec_diff
    else: #different day with 24 hours or more gap
        return (sec_diff+86400*day_diff)


# In[22]:


#concatenating date and time columns of the stream
def combine(stream):
    stream.loc[0,'DateTime'] = stream.loc[0,'date'] + " " + stream.loc[0,'time']
    return stream


# In[23]:


#converts DateTime string to datetime format
def extract(num):
    num = datetime.strptime(num, "%Y-%m-%d %H:%M:%S")
    return num


# In[24]:


#called only when end-of-file encountered to close all the running user sessions
def close_sessions(stream,pq,first,StreamedData,outputcols):
    #sorting queue wrt the session start time stored in hashmap
    prior = []
    for key, value in first.items():
        prior.append((key, value))
    prior = sorted(prior, key=lambda x: x[0]) #sort by ip

    listq = list(pq)
    listsort = sorted(listq, key=lambda x: x[0]) #sort by ip
    
    listqq = [(y[0],y[1][0],x[1]) for y,x in sorted(zip(prior,listsort))]
    listqqq = sorted(listqq, key=lambda x: x[1]) #sort by start time
    
    listqqqq = [(y,x) for y,_,x in listqqq]
    
    #closing all user sessions; queue and hashmap are empty at the end
    pq = deque(listqqqq)
    while len(pq) != 0:
        (usr_ip,tm_last) = pq[0]
        tm_first = first[usr_ip][0]
        num_of_docs = first[usr_ip][1] 
        qdval = (usr_ip,tm_first,tm_last,time_between(extract(tm_last),extract(tm_first))+1,num_of_docs) 
        dat = pd.Series(qdval, outputcols)
        StreamedData = StreamedData.append(dat, ignore_index=True)
        del first[usr_ip]
        pq.popleft()
    return (pq,first,StreamedData)


# In[25]:


#manages where to redirect the stream depending upon if it's end-of-file or not
def manager(stream,pq,first,inac,booval,StreamedData,outputcols):
    if booval is True:
        (pq,first,StreamedData) = close_sessions(stream,pq,first,StreamedData,outputcols)
    else:
        (pq,first,StreamedData) = process_curr(stream,pq,first,inac,booval,StreamedData,outputcols)
    return (pq,first,StreamedData)


# In[40]:


#adds/replaces the current/stream time request to queue; removes the expired sessions from queue/hashmap
def process_curr(stream,pq,first,inac,booval,StreamedData,outputcols):
    
    #remove the user from queue and hashmap if user session expires due to inactivity
    while(len(pq)):
        (usr_ip,tm_last) = pq[0] #peek
        if (time_between(extract(stream.loc[0,'DateTime']),extract(tm_last)) > inac[0][0]):
            tm_first = first[usr_ip][0]
            num_of_docs = first[usr_ip][1]
            qdval = (usr_ip,tm_first,tm_last,time_between(extract(tm_last),extract(tm_first))+1,num_of_docs)
            dat = pd.Series(qdval, outputcols)
            StreamedData = StreamedData.append(dat, ignore_index=True)
            del first[usr_ip]
            pq.popleft()
        else:
            break
    
    #add the stream to queue and hashmap; or update the queue if that user ip already exists
    if stream.loc[0,'ip'] in first.keys():
        listq = list(pq)
        index = 0
        for element in listq:
            (usr_ip,tm_last) = element
            if usr_ip == stream.loc[0,'ip']:
                listq.remove((usr_ip,tm_last))
                pq = deque(listq)
                pq.append((stream.loc[0,'ip'],stream.loc[0,'DateTime']))
                first[usr_ip][1] = first[usr_ip][1] + 1
    else:
        pq.append((stream.loc[0,'ip'],stream.loc[0,'DateTime']))
        first[stream.loc[0,'ip']] = [stream.loc[0,'DateTime'],1]
  
    return (pq,first,StreamedData)


# In[43]:


#driver function that reads log.csv and gives sessionization.txt; where all the streaming happens!
def analytics(file_path):
    cols = ['ip','date','time','cik','accession','extention']
    outputcols = ['ip','first_time','last_time','duration','number of doc requests']
    pq = deque()
    first = {}
    if ('StreamedData' in vars()) == False:
        StreamedData = pd.DataFrame(columns=outputcols)
        stream = pd.DataFrame(columns=cols)   
    inac = pd.read_csv('input/inactivity_period.txt',header=None)
    booval = False
    with open(file_path) as content:
        ctr = 0
        for x in content:
            if ctr == 0: #skips header line in .csv file
                ctr = ctr + 1
                continue
            ctr = ctr + 1
            line = read_line(x,stream)
            dt = combine(line)
            qd = manager(dt,pq,first,inac,booval,StreamedData,outputcols) #returns (pq,first,StreamedData)
            pq = qd[0]
            first = qd[1]
            StreamedData = qd[2]
        #executed when end-of-file reached
        else:
            booval = True
            qdd = manager(dt,pq,first,inac,booval,StreamedData,outputcols) #returns (pq,first,StreamedData)
            
    qdd[2].to_csv('output/sessionization.txt', sep=',',index=False,header=False)
    return qdd


# In[44]:


if __name__ == "__main__":
    lineInfo = analytics("input/log.csv")

