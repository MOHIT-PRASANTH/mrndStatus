from flask import Flask,render_template,request,redirect
import os
import json
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
cache = SimpleCache()

all_colleges = list(
    ('kiit', 'bharathuniv', 'methodist', 'mvsr', 'nitk', 'vit', 'mallareddy', 'mlr', 'bulleya', 'gnits', 'sreedatta',
     'snist', 'geethanjali', 'svecw', 'cmrit', 'jntuv', 'srkr', 'cmrtc', 'bhuvarnasi', 'svec', 'manoharbhai', 'vbit',
     'vignan', 'mvgr', 'mgit', 'anits', 'cvr', 'raghu', 'gitamh', 'klu', 'gitamv', 'gmrit', 'gvptech', 'smec', 'cmrcet',
     'bvritn', 'bvrith', 'griet', 'cmrec', 'au', 'vasavi', 'cbit', 'kitw', 'pragati', 'vardhaman', 'jntuh', 'gvp',
     'kmit', 'rguktnuzvid', 'gvpw'))

class Student():
    name = ""
    lessons = ""
    assignments = ""
    errors = ""

    def __init__(self,name,lessons,assignments,errors):
        self.name = name
        self.lessons = lessons
        self.assignments = assignments
        self.errors = errors

    def __str__(self):
        return "Name : "+self.name + "\n" + "Lessons : "+self.lessons + "\n" + "Assignements : "+self.assignments+"\n"+"Errors : "+self.errors

def getData(url,college):
    #os.environ["Path"] += os.getcwd().join("phantomjs.exe")
    from selenium import webdriver

    browser = webdriver.PhantomJS()
    browser.get(url)
    data = browser.page_source
    browser.quit()

    try:
        from bs4 import BeautifulSoup
        html = BeautifulSoup(data, 'html.parser')
        result = []
        for tr in html.findAll('tr'):
            td = tr.findAll('td')
            if (len(td) > 1):
                name = td[1].find('a').contents[0]
                name = str(name).lower()

                if (name.find(college) != -1):
                    studentData = Student(name=str(name)[str(name).find(college)+len(college)+1:],lessons=int(str(td[2].contents[0]).strip()),assignments=int(str(td[3].contents[0]).strip()),errors = str(td[4].contents[0]))
                    result.append(studentData)
    except Exception:
        print("ERROR")
        return redirect("/mrndStatus/?err=1")

    return result

@app.route("/mrndStatus/")
def index():
    err = request.args.get('err')
    if(err=='1'):
        return render_template("getUrl.html",err=1)
    return render_template("getUrl.html")

@app.route("/")
def homeIndex():
    return index()

@app.route("/mrndStatus/saveUrl/",methods=['GET', 'POST'])
def saveUrl():
    if(request.method=='POST' and 'url' in request.form):
        url = request.form['url']
        cache.set('url',url)
        return redirect("/mrndStatus/college/")
    return index()

@app.route("/mrndStatus/<college>/")
def getCollegeStatistics(college):
    if(not cache.has('url')):
        return redirect("/mrndStatus/")

    url = cache.get('url')

    college = str(college).lower()
    if(college not in all_colleges):
        return render_template('studentsList.html',title="Python Course",all_colleges=all_colleges)

    studentDetails = []
    if(cache.has(college)):
        studentDetails = json.loads(cache.get(college))
        for index in range(len(studentDetails)):
            studentDetails[index] = Student(**studentDetails[index])
    else:
        studentDetails = getData(url = url,college=college)
        jsonEncoded = json.dumps(studentDetails, default=lambda o: o.__dict__)
        cache.set(college, jsonEncoded)

    legend = college.upper()
    values = []
    labels = []
    count = {}
    for student in studentDetails:
        total_assignments = 0
        total_assignments = student.assignments+student.lessons
        values.append(total_assignments)
        labels.append(student.name)
        if((str(total_assignments)+' lessons') in count):
            count[(str(total_assignments)+' lessons')] += 1
        else:
            count[(str(total_assignments)+' lessons')] = 1

    countItems = list(count.items())
    countItems = sorted(countItems)
    color_keys = list(map(lambda x:x[0],countItems))
    color_values = list(map(lambda x:x[1],countItems))
    colorCodes = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA", "#ABCDEF", "#DDDDDD", "#ABCABC", "#3b5c78", "#28415f", '#3b5c78', '#28415f', '#cfcfea', '#d7fff1', '#b77575', '#a0db8e', '#c0d6e4', '#ffc0cb', '#d9efcb', '#e5ebc8',
     '#d2ddcd', '#d7ecc3', '#e2f1bb', '#cabbf1', '#c7c9ff', '#fffdc7', '#ffe1c7', '#ffdab9', '#d6e6da', '#eaba9d',
     '#faebd7', '#d4c1c5', '#da8709', '#90ba3e', '#ffb6b9', '#fff8e7', '#3a24aa', '#ca91de', '#d3ffce', '#e6e6fa',
     '#b0e0e6', '#f0f8ff', '#fa8072', '#faebd7', '#c9e0dc', '#4c988c', '#6ddac8', '#da6d7f', '#89d8be', '#d4c1c5',
     '#e9e0e2', '#3d9887']

    if(len(colorCodes) < len(count)):
        while(len(colorCodes) < len(count)):
            colorCodes += colorCodes

    return render_template('studentsList.html', values=values, labels=labels, legend=legend, title="Python Course " + college.upper() + " Status", max=20,all_colleges=all_colleges, set=zip(color_values , color_keys, colorCodes[:len(count)]))

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()