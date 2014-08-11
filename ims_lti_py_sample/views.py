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



@csrf_exempt
def index(request):
    if settings.LTI_DEBUG:
        print "META"
        #print request.META
        print "PARAMS"

        print request.POST
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
            print str(g.key) +str(g.value)
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


            taken_id=urllib.unquote(resp['id'])
            print "Got Taken Id"
            print taken_id

            '''
            Get questions from this assessment
            assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/

            '''

            resp1 = student_req.get(student_req.url+bank_id+"/assessmentstaken/"+taken_id+"/questions/")
            print resp1
            resp1=resp1.json()
            print resp1
            questions = resp1['data']# a list of wuestions
            Questions.objects.all().delete()
            for a in questions:
                print a['text']['text']
                q=Questions(value=a)
                q.save()

            print "Questions"
            #print questions
            print "Request status code "
            #print resp.status_code
            #print resp

            return render_to_response("ims_lti_py_sample/student.html",
                                          RequestContext(request,{'userName':name, 'questions': questions}))
        else:
            return render_to_response(("ims_lti_py_sample/student"),RequestContext(request,{'userName':name,'questions':[]}))
    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def get_question(request):
   # try:
        print "Get Question"
        #print request.POST
        data=request.POST.getlist('data[]')
        question=data[1]
        print question
        p=Post(key="question", value=question)
        p.save()
        manip=data[0]
        #print manip
        decoded=base64.b64decode(manip)
        #print decoded
        text_file=open("manip.unity3d","w")
        text_file.write(decoded)
        text_file.close()
    #     return render_to_response("ims_lti_py_sample/question.html",
    #                                           RequestContext(request,{'userName':"Hannah"}))
    # except KeyError, e:
    #     return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))
        question= {'success': True, 'redirect': True, 'redirectURL': "question"}
        return HttpResponse(json.dumps(question), content_type='application/json')

@csrf_exempt
def display_question(request):
    try:
        print "Display question"
        #print request
        #q=Post.objects.filter(key='question')
        params = {}
        for g in Post.objects.all():
            params[g.key]= g.value
            print g.key
        q=params['question']
        #print q
        quest=Questions.objects.all()
        questions=[]
        for a in quest:
            questions.append(a)
            print a
        #print quest

        return render_to_response("ims_lti_py_sample/question.html",
                                          RequestContext(request,{'question':q,'questions':questions}))
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

                bank_id=urllib.unquote(a['id'])
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
        name=request.POST.getlist('name')[0]
        print "Name of new assessment"
        print name
        data = {'name': name,'description': "difficult", 'itemIds': items_ids}
        data=json.dumps(data)
        #bank_id= Bank.objects.get('bank_id')
        bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
        print "sending items"
        resp = req_assess.post(req_assess.url+bank_id+"/assessments/", data)
        print 'Created new assess: response'
        print resp['id']
        sub_id=urllib.unquote(resp['id'])

        eq4=req_assess.post(req_assess.url+bank_id+'/assessments/'+sub_id+'/assessmentsoffered/')
        print "Create offering:"
        print "offering id"
        print eq4['id']

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
        bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
        sub_id = request.GET.getlist('sub_id')[0]
        sub_id = urllib.unquote(sub_id)


        ''''
        get list of offerings
        '''
        r1=req_assess.get(req_assess.url+bank_id+'/assessments/'+sub_id+"/assessmentsoffered/")
        print "response assessments offered"
        print r1
        if r1.status_code==200:
            data = r1.json()['data']

            if len(data)>0:
                offering_id=data[0]['id']
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
    bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'

    '''
    Get offerings of this assessment
    url:   assessment/<bank_id>/assessments/<sub_id>/assessmentsoffered/

    '''
    resp=req_assess.get(req_assess.url+bank_id+'/assessments/'+sub_id+"/assessmentsoffered/")
    data= resp.json()['data']
    print data
    if len(data)>0:
            offering_id=data[0]['id']
            print "offering id"
            print offering_id
            return HttpResponse(json.dumps(offering_id))
    else:
        return HttpResponse("no offering")


@csrf_exempt
def get_items(request):
    print "Get Items of an Assessment"

    print request.GET
    sub_id = request.GET.getlist('sub_id')[0]
    sub_id = urllib.unquote(sub_id)
    print sub_id

    try:

        req_assess=AssessmentRequests()
        bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
        resp = req_assess.get(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/")
        '''
        Retrieving offerings for this assessment
        '''
        eq4=req_assess.get(req_assess.url+bank_id+'/assessments/'+sub_id+'/assessmentoffered/')
        print 'offerings'
        #print eq4.text
        #print eq4.status_code
        #print resp.text
        items = resp.json()
        #print "Items"
        #print items
        #for a in items:
         #   print a['displayName']['text']


        return HttpResponse(json.dumps(items), content_type='application/json')

    except KeyError, e:
            return render_to_response("ims_lti_py_sample/error.html",  RequestContext(request))

@csrf_exempt
def add_item(request):
    print 'Add Item to Assessment'
    print request.POST
    #check if request.Post is not empty
    print "Test"
    print request.POST._getitem_('sub_id')
    sub_id=request.POST.getlist('sub_id')[0]
    question_id=request.POST.getlist('question_id')[0]
    data={"itemIds": [question_id]}

    print sub_id
    print question_id

    req_assess=AssessmentRequests()
    bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    resp = req_assess.post(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/",json.dumps(data))
    print "Printing the response"
    print resp
    return HttpResponse(resp ,content_type='application/json')



@csrf_exempt
def remove_item(request):
    print 'Remove Item from Assessment'
    print request.POST

    sub_id=request.POST.getlist('sub_id')[0]
    question_id=request.POST.getlist('question_id')[0]

    print sub_id
    print question_id

    req_assess=AssessmentRequests()
    bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'
    resp = req_assess.delete(req_assess.url+bank_id+"/assessments/"+sub_id+"/items/"+question_id+"/",)

    print resp
    return HttpResponse(resp,content_type='application/json')

'''
Update list of assessments
'''''''''''''''''''''
@csrf_exempt
def update_assessments(request):
    print "Update assessments"
    print request.GET

    req_assess=AssessmentRequests()
    bank_id = 'assessment.Bank:53d671bc33bb72de9183ce2d@birdland.mit.edu'

    eq2=req_assess.get(req_assess.url + bank_id +"/assessments/")
    assessments = eq2.json()['data']
    print assessments
    return HttpResponse(json.dumps(assessments), content_type='application/json')


