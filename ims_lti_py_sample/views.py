import pickle

from django.http import HttpResponse
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from ims_lti_py.tool_provider import DjangoToolProvider

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import oauth2
from models import Post, Headers, Questions

from .utilities import *
import base64
from django.core.cache import cache


def flush():
    cache.clear()
    print "Cleared CACHE"

@csrf_exempt
def index(request):
    if settings.LTI_DEBUG:
        print "META"
        #print request.META
        print "PARAMS"

        flush()
        #print request.POST
        #print request.POST['user_id']
        #print request.user
    session = request.session
    session.clear()
    try:
        consumer_key = settings.CONSUMER_KEY
        secret = settings.LTI_SECRET

        tool = DjangoToolProvider(consumer_key, secret, request.POST)
        is_valid = tool.is_valid_request(request)
        session['message'] = "We are cool!"
    except oauth2.MissingSignature,e:
        is_valid = False
        session['message'] = "{}".format(e)
        pass
    except oauth2.Error,e:
        is_valid = False
        session['message'] = "{}".format(e)
        pass
    except KeyError,e:
        is_valid = False
        session['message'] = "{}".format(e)
        pass
    session['is_valid'] = is_valid
    # copy request to dictionary
    request_dict = dict()
    for r in request.POST.keys():
        request_dict[r] = request.POST[r]
    session['LTI_POST'] = pickle.dumps( request_dict )


    '''
    Saving parameters into Post model
    '''
    Post.objects.all().delete()
    for k in request.POST:
        p = Post(key=k, value=request.POST[k])
        p.save()
        #print str(k)+"   "+str(request.POST[k])
        #print k
    #print request.POST['lis_person_name_full']
    print request.POST['lis_person_name_given']
    #url = "https://assessments-dev.mit.edu/api/v1"

    '''
    Save the url, public_key, private_key
    '''
    #Headers(key='url',value=url).save()
    #Headers(key='public_key',value='E5IFLfKuxNdhLKh+tLRN').save()
    #Headers(key ='private_key',value='0/e10IAyBE1VkqtK+8PzPh2ViXVl5us1Zrj2rYQs').save()

    print request.POST['roles']
    if 'Instructor' in request.POST['roles']:
        return redirect('InstructorView')
    else:
        if "Learner" in request.POST['roles']:
            return redirect('StudentView')




@csrf_exempt
def student(request):
    print "Student View"



    try:
        student_req = AssessmentRequests('taaccct_student')
        '''
        get bank id and offering id
        request questions for this assessment
        '''
        params = {}
        for g in Post.objects.all():
            params[g.key]= g.value
            #print str(g.key) +str(g.value)
        bank_id= params['custom_bank_id']
        offering_id= params['custom_offering_id']
        name = params["lis_person_name_given"]


        print bank_id
        print offering_id

        '''
        create new taken
        and get the taken_id
        assessment/banks/<bank_id>/assessmentsoffered/<offering_id>/asessmentstaken/
        '''
        resp= student_req.post(student_req.url+bank_id+"/assessmentsoffered/"+offering_id+"/assessmentstaken/")  #/assessmentstaken/
        print resp

        if 'id'in resp:


            taken_id=resp['id']
            p = Post(key="taken_id", value=taken_id)
            p.save()
            print "Got Taken Id"
            print taken_id

            '''
            Get questions from this assessment
            assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/
            '''
            resp1 = student_req.get(student_req.url+bank_id+"/assessmentstaken/"+taken_id+"/questions/")
            resp1 = resp1.json()
            questions = resp1['data']# a list of questions

            return render_to_response("ims_lti_py_sample/student.html",
                                          RequestContext(request,{'userName': name, 'questions': questions}))
        else:
            return render_to_response(("ims_lti_py_sample/student.html"),RequestContext(request,{'userName':name,'questions' : []}))
    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def get_question(request):
   # try:
        print "Get Question"
        #print request.POST
        '''
        Data -> [files.manip, text.text], e.g [manip, question] add [question_name] add [question_id]
        '''
        data = request.POST.getlist('data[]')
        print data

        print "Size of data "+str(len(data))
        print "selected question"

        question = data[1]
        question_name = data[2]
        question_id=data[3]
        print question ## item object
        print question_name
        print question_id

        #make sure there isn't one in the database already
        Post.objects.filter(key='question_name').delete()
        Post.objects.filter(key="question").delete()
        Post.objects.filter(key="question_id").delete()

        p1=Post(key="question_name", value=question_name)
        p2=Post(key="question", value=question)
        p3=Post(key="question_id", value=question_id)
        p1.save()
        p2.save()
        p3.save()

        ########################################
        #Testing if key is unique
        #########################################
        # print "Testing Post for duplicates"
        # params = {}
        #
        # for g in Post.objects.all():
        #     params[g.key]= g.value
        #     #print str(g.key) +"      "+ str(g.value)

        ##########################################
        #end of testing

        manip = data[0]
        #print "manip for this question"
        #print manip

        decoded=base64.b64decode(manip)
        #print decoded
        text_file=open("static/Gaspard/"+question_name+".unity3d", "w")
        text_file.write(decoded)
        text_file.close()
       # return render_to_response("ims_lti_py_sample/question.html",
    #                                           RequestContext(request,{'userName':"Hannah"}))
    # except KeyError, e:
    #     return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))

        question= {'success': True, 'redirect': True, 'redirectURL': "display_question"}#d_question  display_question
        return HttpResponse(json.dumps(question), content_type='application/json')

@csrf_exempt
def display_question(request):
    try:
        print "Display question"
        #print request
        params = {}
        for g in Post.objects.all():
            params[g.key]= g.value

        questions = []
        question = "No Description"


        q_name =params['question_name']
        if len(params['question'])>0:
            question = params['question']
        print q_name



        bank_id=params['custom_bank_id']
        taken_id=params['taken_id']
        student_req=AssessmentRequests('taaccct_student')
        '''
        Get questions from this assessment
        assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/
        '''
        resp1 = student_req.get(student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/questions/")
        resp1 = resp1.json()
        #print resp1
        questions = resp1['data']  # a list of questions

        return render_to_response("ims_lti_py_sample/unity.html",
                              RequestContext(request,
                                             {'question_name': q_name, 'question': question, 'questions': questions}))

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))  ## Testin unity web player


@csrf_exempt
def submit_answer(request):
    print "Submit answer"

    answer = request.POST.getlist('answer')[0]
    print answer

    params = {}
    for g in Post.objects.all():
        params[g.key] = g.value

    bank_id = params['custom_bank_id']
    taken_id = params['taken_id']
    question_id = params['question_id']

    student_req = AssessmentRequests('taaccct_student')
    resp = student_req.post(
        student_req.url + bank_id + '/assessmentstaken/' + taken_id + '/questions/' + question_id + '/submit/',json.dumps(answer))
    print "Got answer back"
    print resp
    return HttpResponse(json.dumps(resp), content_type='application/json')


@csrf_exempt
def d_question(request):
    try:
        print "D question"


        return render_to_response("ims_lti_py_sample/UnityWebPlayer.html",
                                          RequestContext(request))
    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def instructor(request):
    print "Instructor View"


    try:

        req_assess=AssessmentRequests()

        eq = req_assess.get(req_assess.url)
        print "Request status code "
        print eq.status_code

        resp = eq.json()
        banks = resp['data']
        print "Number of banks: "+str(len(banks))
        found=False
        bank_id=""
        for a in  banks:
            if a['displayName']['text']=="Ortho 3D":
                print "Found Ortho 3D"
                found = True

                bank_id = a['id']

                Post.objects.filter(key="bank_id").delete()
                p = Post(key="bank_id", value=bank_id)
                p.save()

                #print bank_id
                #Bank.objects.all().delete()
                #Bank(key='bank_id', value=bank_id).save()

        if found:
                '''
                Get a list assessments in a bank
                assessment/banks/<bank_id>/assessments/

                '''
                print str(req_assess.url) + str(bank_id)+"/assessments/"

                eq2=req_assess.get(req_assess.url + bank_id +"/assessments/")

                print eq2.text
                print eq2.status_code

                assessments = eq2.json()['data']
                #print assessments
                print "Number of assessments: "+str(len(assessments))

                for a in assessments:
                    print a['displayName']['text']  # Assessment name

                '''
                Get a list of items in a bank
                assessment/banks/<bank_id>/items/
                '''
                eq3 = req_assess.get(req_assess.url + bank_id+"/items/")
                print "Status code getting items:  "+str(eq3.status_code)
                items = eq3.json()['data']

                for a in items:
                    print a['displayName']['text']

                return render_to_response("ims_lti_py_sample/instructor.html",
                                          RequestContext(request,{'assessments': assessments,'items': items}))
        else:
                print "No bank Ortho 3D found"

    except KeyError, e:
            return render_to_response("ims_lti_py_sample/error.html",  RequestContext(request))

@csrf_exempt
def create_assessment(request):
    print "Create new assessment"

    print request.POST
    try:

        req_assess=AssessmentRequests()
        items_ids=request.POST.getlist('selected[]')

        print "Selected bank items"
        print items_ids
        print request.POST.getlist('name')
        name = request.POST.getlist('name')[0]
        print "Name of new assessment"
        print name
        data = {'name': name,'description': "difficult", 'itemIds': items_ids}
        data=json.dumps(data)
        #bank_id= Bank.objects.get('bank_id')
        #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'

        bank_id = Post.objects.filter(key="bank_id")[0].value

        print "Print bank id"
        print bank_id
        print "sending items"
        '''
        Create new assessment
        url: assessment/bank/<bank_id>/assessments/
        '''
        resp = req_assess.post(req_assess.url+bank_id+"/assessments/", data)
        print 'Created new assess: response'
        if 'id' in resp.keys():
            print resp['id']
            sub_id=resp['id']
        else:
            print "Could not create an assessment"
            if 'detail' in resp.keys():
                print resp

        #Removed creation of assessment offering

        return HttpResponse(json.dumps(resp),content_type="application/json")
        ##need to update the asssessment table

    except KeyError, e:
            return render_to_response("ims_lti_py_sample/error.html",  RequestContext(request))

@csrf_exempt
def delete_assessment(request):
    print "Delete Assessment"

    print request.GET
    try:

        req_assess=AssessmentRequests()
        #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
        bank_id = Post.objects.filter(key="bank_id")[0].value
        sub_id = request.GET.getlist('sub_id')[0]
       # sub_id = sub_id


        ''''
        get list of offerings
        '''
        r1=req_assess.get(req_assess.url+bank_id+'/assessments/'+sub_id+"/assessmentsoffered/")
        print "response assessments offered"
        print r1
        if r1.status_code == 200:
            data = r1.json()['data']

            if len(data)>0:
                offering_id = data[0]['id']
                print "offering id"
                print offering_id

                '''
                Get a list of takens for this assessment
                url: /assessment/<bank_id>/assessmentsoffered/<sub_id>/assessmentstaken/
                '''
                r4=req_assess.get(req_assess.url+bank_id+'/assessmentsoffered/'+offering_id+"/assessmentstaken/")
                if r4.status_code==200:
                    print "takens"
                    print r4.json()
                    takensList=r4.json()['data']
                    print takensList
                    if len(takensList)>0:
                        for taken in takensList:
                            print "taken"
                            print taken
                            '''
                            delete assessment takens
                            url:assessment/<bank_id>/assessmentstaken/<taken_id>/
                            '''
                            r3=req_assess.delete(req_assess.url+bank_id+'/assessmentstaken/'+taken['id']+'/')
                else:
                    return HttpResponse(r4)



                '''
                delete an offering
                url:    assessment/<bank_id>/assessmentsoffered/<offering_id>/
                '''''
                r2=req_assess.delete(req_assess.url+bank_id+'/assessmentsoffered/'+offering_id+"/")
                print r2
                if r2.status_code!=200:
                    return HttpResponse(r2)

            '''
            Delete an assessment
            url:  assessment/<bank_id>/assessments/<sub_id>/
            '''

            req=req_assess.delete(req_assess.url+bank_id+"/assessments/"+sub_id+'/')
            print "del response"
            print req

            return HttpResponse(req)
        else:
            #r2=r2.json()
            #if r2['detail']=='There are still AssessmentTakens associated with this AssessmentOffered. Delete them first.':
            return HttpResponse(r1)


    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html",  RequestContext(request))


@csrf_exempt
def get_offering_id(request):

    print "Get offering id of an Assessment"
    print request.POST

    sub_id=request.POST.getlist('sub_id')[0]
    print sub_id
    req_assess=AssessmentRequests()
    #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    bank_id = Post.objects.filter(key="bank_id")[0].value
    '''
    Create new offering
    url: assessment/bank/assessements/<sub_id>/assessmentsoffered/
    '''

    eq4=req_assess.post(req_assess.url+bank_id+'/assessments/'+sub_id+'/assessmentsoffered/')
    print "Create offering:"
    print "offering id"
    print eq4['id']

    '''
    Get offerings of this assessment
    url:   assessment/<bank_id>/assessments/<sub_id>/assessmentsoffered/

    '''
    # resp=req_assess.get(req_assess.url+bank_id+'/assessments/'+sub_id+"/assessmentsoffered/")
    # data= resp.json()['data']
    # print data
    # if len(data)>0:
    #         offering_id=data[len(data)-1]['id'] #want to get the last offering id in case there is more than one
    #         print len(data)
    #         print "offering id"
    #         print offering_id
    #         return HttpResponse(json.dumps(offering_id))
    # else:
    #     return HttpResponse("no offering")


    return HttpResponse(json.dumps(eq4['id']))


@csrf_exempt
def get_items(request):
    print "Get Items of an Assessment"

    print request.GET
    sub_id = request.GET.getlist('sub_id')[0]
    #sub_id = urllib.unquote(sub_id)
    print sub_id

    try:

        req_assess=AssessmentRequests()
        #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
        bank_id = Post.objects.filter(key="bank_id")[0].value
        resp = req_assess.get(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/")

        items = resp.json()
        #print "Items"
        #print items
        #for a in items:
         #   print a['displayName']['text']


        return HttpResponse(json.dumps(items), content_type='application/json')

    except KeyError, e:
            return render_to_response("ims_lti_py_sample/error.html",  RequestContext(request))

'''
Maybe want  to check if there are any takens for this assessement
    if yes create a new assessments from the old one plus the new question
    else
        want to delete the takens and offerings

Question:  do I ever want to delete offerings?
Each time I add or delete item an offering is being created
Another way is to create offering only when the instructor is requesting it
'''
@csrf_exempt
def add_item(request):
    print 'Add Item to Assessment'
    print request.POST
    #check if request.Post is not empty
    print "Test"
    sub_id = request.POST.getlist('sub_id')[0]
    question_id=request.POST.getlist('question_id')[0]
    data={"itemIds": [question_id]}

    print sub_id
    print question_id

    req_assess = AssessmentRequests()
    #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    bank_id = Post.objects.filter(key="bank_id")[0].value
    '''
    Adding item to assessment
    url: assessment/bank/
    '''
    resp = req_assess.post(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/", json.dumps(data))
    print "Printing the response"
    print resp



    #deleteOfferings(bank_id, sub_id)
    # '''
    # Create new offering
    # url: assessment/bank/assessements/<sub_id>/assessmentsoffered/
    # '''
    #
    # eq4 = req_assess.post(req_assess.url + bank_id + '/assessments/' + sub_id + '/assessmentsoffered/')
    # print "Create offering:"
    # print "offering id"
    # print eq4['id']


    return HttpResponse(json.dumps(resp), content_type='application/json')


'''
Remove one item from the assessment

'''
@csrf_exempt
def remove_item(request):
    print 'Remove Item from Assessment'
    print request.POST

    sub_id=request.POST.getlist('sub_id')[0]
    question_id=request.POST.getlist('question_id')[0]

    print sub_id
    print question_id

    req_assess=AssessmentRequests()
    #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    bank_id = Post.objects.filter(key="bank_id")[0].value
    resp = req_assess.delete(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/"+question_id+"/",)

    print resp
    return HttpResponse(resp, content_type='application/json')


'''
Reorder Items in the assessment
Delete all offerings and takens
Delete all items
Add items in new (given) order

Question: do I need to create a new offering?
    probably the instructor will need to add a new link to this offering otherwise the old offerings will be lost

'''
@csrf_exempt
def arrange_items(request):
    print "Rearrange items in assessment"
    print request.POST
    #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    bank_id = Post.objects.filter(key="bank_id")[0].value

    items_ids=request.POST.getlist('data[]')
    print "Items to be added"
    print items_ids

    sub_id=request.POST.getlist('sub_id')[0]
    print sub_id

    data = {"itemIds": items_ids}
    print "Data"
    print data

    deleteOfferings(bank_id,sub_id)
    resp=replaceAllItems(bank_id,sub_id, data)
    #Create new offering?
    return HttpResponse(json.dumps(resp), content_type='application/json')


'''
Update list of assessments
'''''''''''''''''''''
@csrf_exempt
def update_assessments(request):
    print "Update assessments"
    print request.GET

    req_assess=AssessmentRequests()
    #bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    bank_id = Post.objects.filter(key="bank_id")[0].value

    eq2=req_assess.get(req_assess.url + bank_id +"/assessments/")
    assessments = eq2.json()['data']
    print assessments
    return HttpResponse(json.dumps(assessments), content_type='application/json')


'''''''''''''''''''''''''''''
'Helper functions'
'''''''''''''''''''''''''''''
'''
Replace old item list with the new one
Delete each item one by one, add new list of items
'''
def replaceAllItems(bank_id, sub_id, data):
    print "deleting all items in the assessment"

    req_assess=AssessmentRequests()

    print "get all items"

    items = getItems(bank_id,sub_id).json()
    for item in items:
        print item['id']
        question_id=item['id']
        resp = req_assess.delete(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/"+question_id+"/",)

        print resp

    #now the assessment should be empty
    #we can add new items

    resp = req_assess.post(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/", json.dumps(data))
    print "Printing the response"
    print resp
    return resp



def getItems(bank_id, sub_id):

    req_assess=AssessmentRequests()
    resp = req_assess.get(req_assess.url+ bank_id+"/assessments/"+sub_id+"/items/")
    return resp


def deleteOfferings(bank_id, sub_id):

    print "deleting offerings"

    req_assess=AssessmentRequests()
    '''
    Get list of offerings
    url: /assessment/<bank_id>/assessments/<sub_id>/assessmentsoffered/
    '''
    r1=req_assess.get(req_assess.url+bank_id+'/assessments/'+sub_id+"/assessmentsoffered/")
    print "response assessments offered"
    print r1
    if r1.status_code==200:
        data = r1.json()['data']

        if len(data)>0:
            '''
            Want to delete all offerings
            '''
            print "number of offerings: "+str(len(data))
            for offering in data:
                offering_id=offering['id']
                print offering['id']
                '''
                Get a list of takens for this assessment
                url: /assessment/<bank_id>/assessmentsoffered/<sub_id>/assessmentstaken/
                '''
                r4=req_assess.get(req_assess.url+bank_id+'/assessmentsoffered/'+offering_id+"/assessmentstaken/")
                if r4.status_code==200:
                    print "takens"
                    print r4.json()
                    takensList=r4.json()['data']
                    print takensList
                    if len(takensList)>0:
                        for taken in takensList:
                            print "taken"
                            print taken
                            print "delete this taken"
                            '''
                            delete assessment takens
                            url:assessment/<bank_id>/assessmentstaken/<taken_id>/
                            '''
                            r3=req_assess.delete(req_assess.url+bank_id+'/assessmentstaken/'+taken['id']+'/')

                            print r3
                    else:
                        print "no takens for this assessment"
                else:
                    print("Error: could not get list of takens")
                    print(r4)

                    #return HttpResponse(r4)
                '''
                Now we can delete this offering
                '''
                '''
                delete an offering
                url:    assessment/<bank_id>/assessmentsoffered/<offering_id>/
                '''''
                r2=req_assess.delete(req_assess.url+bank_id+'/assessmentsoffered/'+offering_id+"/")
                print r2


        else:
            print("Offerings list is empty")
        return True

    else:
        print("Error getting the offerings")
        print r1
        return False

