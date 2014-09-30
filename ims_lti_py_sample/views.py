import pickle

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ims_lti_py.tool_provider import DjangoToolProvider

from django.conf import settings

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
        # print request.META
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
    except oauth2.MissingSignature, e:
        is_valid = False
        session['message'] = "{}".format(e)
        pass
    except oauth2.Error, e:
        is_valid = False
        session['message'] = "{}".format(e)
        pass
    except KeyError, e:
        is_valid = False
        session['message'] = "{}".format(e)
        pass
    session['is_valid'] = is_valid
    # copy request to dictionary
    request_dict = dict()
    for r in request.POST.keys():
        request_dict[r] = request.POST[r]
    session['LTI_POST'] = pickle.dumps(request_dict)

    '''
    Saving parameters into Post model
    '''
    Post.objects.all().delete()
    for k in request.POST:
        p = Post(key=k, value=request.POST[k])
        p.save()
        # print str(k)+"   "+str(request.POST[k])
        #print k
    # print request.POST['lis_person_name_full']
    print request.POST['lis_person_name_given']
    print request.POST['lis_outcome_service_url']
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
            params[g.key] = g.value
            # print str(g.key) +str(g.value)
        bank_id = params['custom_bank_id']
        offering_id = params['custom_offering_id']
        name = params["lis_person_name_given"]

        print bank_id
        print offering_id

        '''
        create new taken
        and get the taken_id
        assessment/banks/<bank_id>/assessmentsoffered/<offering_id>/asessmentstaken/
        '''
        resp = student_req.post(
            student_req.url + bank_id + "/assessmentsoffered/" + offering_id + "/assessmentstaken/")  # /assessmentstaken/
        # print resp

        if 'id' in resp:
            taken_id = resp['id']
            p = Post(key="taken_id", value=taken_id)
            p.save()
            print "Got Taken Id"
            print taken_id

            questions = getQuestions(bank_id, taken_id)

            return render_to_response("ims_lti_py_sample/student.html",
                                          RequestContext(request, {'userName': name, 'questions': questions}))

        else:
            return render_to_response(("ims_lti_py_sample/student.html"),
                                      RequestContext(request, {'userName': name, 'questions': []}))
    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))




@csrf_exempt
def student_home(request):
    try:
        '''
        get bank id and offering id
        request questions for this assessment
        '''
        params = {}
        for g in Post.objects.all():
            params[g.key] = g.value
        bank_id = params['custom_bank_id']
        taken_id = params['taken_id']
        name = params["lis_person_name_given"]

        questions = getQuestions(bank_id, taken_id)

        return render_to_response("ims_lti_py_sample/student.html",
                                      RequestContext(request, {'userName': name, 'questions': questions}))

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))

'''
Get questions for this taken
add status to each question
'''
def getQuestions(bank_id, taken_id):

    student_req = AssessmentRequests('taaccct_student')
    '''
    Get questions from this assessment
    assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/
    '''
    resp1 = student_req.get(student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/questions/")
    resp1 = resp1.json()
    questions = resp1['data']  # a list of questions
    for a in questions:
        print a['displayName']['text']
        '''
        Get status of the question
        url: assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/status/
        type: 'GET'
        '''
        resp2 = student_req.get(student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/questions/" + a['id']
                                + '/status/')
        resp2 = resp2.json()
        print resp2
        print resp2['responded']
        if resp2['responded'] == True:
            if resp2['correct'] == True:
                a['responded'] = 'Correct'
            else:
                a['responded'] = 'Incorrect'
        else:
            a['responded'] = 'None'
    return questions

@csrf_exempt
def get_question(request):
    # try:
    print "Get Question"
    # print request.POST
    '''
    Data -> [ text.text, innerText, id], e.g [ question, question_name, question_id]
    '''
    data = request.POST.getlist('data[]')
    #print data

    print "Size of data " + str(len(data))
    print "selected question"

    question = data[0]
    question_name = data[1].strip()
    question_id = data[2]
    print question  ## item object
    print question_name
    print question_id

    #make sure there isn't one in the database already
    Post.objects.filter(key='question_name').delete()
    Post.objects.filter(key="question").delete()
    Post.objects.filter(key="question_id").delete()

    p1 = Post(key="question_name", value=question_name)
    p2 = Post(key="question", value=question)
    p3 = Post(key="question_id", value=question_id)
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


    # return render_to_response("ims_lti_py_sample/question.html",
    #                                           RequestContext(request,{'userName':"Hannah"}))
    # except KeyError, e:
    #     return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))

    question = {'success': True, 'redirect': True, 'redirectURL': "display_question"}  #d_question  display_question
    return HttpResponse(json.dumps(question), content_type='application/json')


@csrf_exempt
def display_question(request):
    try:
        print "Display question"
        # print request
        params = {}
        for g in Post.objects.all():
            params[g.key] = g.value


        question = "No Description"

        q_name = params['question_name']
        question_id = params['question_id']
        if len(params['question']) > 0:
            question = params['question']
        print q_name

        bank_id = params['custom_bank_id']
        taken_id = params['taken_id']
        student_req = AssessmentRequests('taaccct_student')

        questions = getQuestions(bank_id, taken_id)

        '''
        Get information about the question
        url: assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/

        {files:{}, displayName:{text:""},description:{}, recordTypeIds:[],text:{}, responded:True,....}
        '''
        resp2 = student_req.get(student_req.url + bank_id + '/assessmentstaken/' + taken_id +
                                "/questions/" + question_id + "/")


        static_folder = settings.STATIC_ROOT
        if static_folder == '':
            static_folder = 'static/'
        '''
        Writing the manip file
        '''
        manip = resp2.json()['files']['manip']
        decoded = base64.b64decode(manip)
        text_file = open(static_folder+"Gaspard/" + q_name + ".unity3d", "w")
        text_file.write(decoded)
        text_file.close()

        '''
        Identifying type of the question
        '''
        question_record_type = resp2.json()['recordTypeIds'][0]
        question_type = resp2.json()['genusTypeId']

        if "label-ortho-faces" in question_record_type:

            return render_to_response("ims_lti_py_sample/unity.html", RequestContext(request,
                                                     {'question_name': q_name, 'question': question,
                                                      'questions': questions,
                                                      'question_type': question_type}))
        else:
            if "choose-viewset" in question_type:
                list_choices = resp2.json()['choices']
                for i, c in enumerate(list_choices):
                    print c['name']
                    print c['id']
                    smallView = c['smallOrthoViewSet']
                    largeView = c['largeOrthoViewSet']
                    decoded1 = base64.b64decode(smallView)
                    decoded2 = base64.b64decode(largeView)

                    small_view_file = open(static_folder + "MultichoiceLayouts/smallOrthoViewSet" + str(i) + ".jpg", "w")
                    large_view_file = open(static_folder + "MultichoiceLayouts/largeOrthoViewSet" + str(i) + ".jpg", "w")
                    small_view_file.write(decoded1)
                    large_view_file.write(decoded2)

                    small_view_file.close()
                    large_view_file.close()

                return render_to_response("ims_lti_py_sample/multichoice.html",
                                          RequestContext(request,
                                                         {'question_name': q_name, 'question': question,
                                                          'questions': questions,
                                                          'question_type': question_type, "choices": list_choices}))
            else:
                return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))




    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))  # # Testin unity web player


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
        student_req.url + bank_id + '/assessmentstaken/' + taken_id + '/questions/' + question_id + '/submit/',
        json.dumps(answer))
    print "Got answer back"
    print resp
    if readyToSubmit():
        submitGrade(bank_id, taken_id, params)

    return HttpResponse(json.dumps(resp), content_type='application/json')


@csrf_exempt
def submit_multi_answer(request):
    print "Submit multi choice answer"

    answer = request.POST.getlist('answer')[0]
    print answer

    params = {}
    for g in Post.objects.all():
        params[g.key] = g.value

    bank_id = params['custom_bank_id']
    taken_id = params['taken_id']
    question_id = params['question_id']

    student_req = AssessmentRequests('taaccct_student')

    '''
    Get information about the question
    url: assessment/bank/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/
    type: 'GET'
    '''
    print student_req.url + bank_id + '/assessmentstaken/' + taken_id + '/questions/' + question_id + '/'
    resp1 = student_req.get(
        student_req.url + bank_id + '/assessmentstaken/' + taken_id + '/questions/' + question_id + '/')
    '''
    Find the id of the chosen answer
    '''
    print resp1.json()['choices'][int(answer)]['name']

    choice_id = resp1.json()['choices'][int(answer)]['id']
    print choice_id
    answer = {"choiceIds": [choice_id]}

    '''
    Submit answer to Multi Choice question
    url: assessment/bank/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/submit/
    type: POST
    data: {"choiceIds": [<choices_id>,...]
    '''
    resp2 = student_req.post(
        student_req.url + bank_id + '/assessmentstaken/' + taken_id + '/questions/' + question_id + '/submit/',
        json.dumps(answer))
    print "Got answer back"
    print resp2


    request_post = params["lis_outcome_service_url"]
    print request_post

    if readyToSubmit():
        submitGrade(bank_id, taken_id, params)

    return HttpResponse(json.dumps(resp2), content_type='application/json')



@csrf_exempt
def instructor(request):
    print "Instructor View"

    try:

        req_assess = AssessmentRequests()
        '''
        Get list of banks
        url: assessment/banks
        '''
        eq = req_assess.get(req_assess.url)
        banks = eq.json()['data']

        print "Number of banks: " + str(len(banks))
        found = False
        bank_id = ""
        for a in banks:
            if a['displayName']['text'] == "Ortho 3D":
                print "Found Ortho 3D"
                found = True

                bank_id = a['id']

                Post.objects.filter(key="bank_id").delete()
                p = Post(key="bank_id", value=bank_id)
                p.save()
                # print bank_id

        if found:
            '''
            Get a list of assessments in a bank
            assessment/banks/<bank_id>/assessments/

            '''
            # print str(req_assess.url) + str(bank_id)+"/assessments/"

            eq2 = req_assess.get(req_assess.url + bank_id + "/assessments/")

            assessments = eq2.json()['data']
            print "Number of assessments: " + str(len(assessments))

            for a in assessments:
                print a['displayName']['text']  # Assessment name

            '''
                Get a list of items in a bank
                assessment/banks/<bank_id>/items/
                '''
            eq3 = req_assess.get(req_assess.url + bank_id + "/items/")
            print "Status code getting items:  " + str(eq3.status_code)
            items = eq3.json()['data']
            items_type1 = []
            items_type2 = []
            items_type3 = []
            items_type4 = []

            for a in items:
                print a['displayName']['text']
                print "    "
                print a['question']['genusTypeId']
                print a['question']['recordTypeIds'][0]
                if "match-ortho-faces" in a['question']['genusTypeId']:
                    '''
                        question%3Amatch-ortho-faces%40ODL.MIT.EDU
                        'recordTypeIds': [question-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU]
                        '''
                    items_type1.append(a)
                elif "choose-viewset" in a['question']['genusTypeId']:
                    '''
                        choose-viewset
                        'recordTypeIds': [question-record-type%3Amulti-choice-ortho%40ODL.MIT.EDU]
                        '''
                    items_type2.append(a)
                elif "define-ortho-faces" in a['question']['genusTypeId']:
                    '''
                        define-ortho-faces
                        question-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU
                        '''
                    items_type3.append(a)
                else:
                    items_type4.append(a)

            name = Post.objects.filter(key='lis_person_name_given')[0].value
            print name
            name = name.replace("-", "")
            return render_to_response("ims_lti_py_sample/instructor.html",
                                      RequestContext(request,
                                                     {'user_name': name, 'assessments': assessments, 'items': items,
                                                      'items_type1': items_type1, 'items_type2': items_type2,
                                                      'items_type3': items_type3, 'items_type4': items_type4}))
        else:
            print "No bank Ortho 3D found"

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def create_assessment(request):
    print "Create new assessment"

    print request.POST
    try:

        req_assess = AssessmentRequests()
        items_ids = request.POST.getlist('selected[]')

        # print "Selected bank items"
        # print items_ids
        # print request.POST.getlist('name')
        name = request.POST.getlist('name')[0]
        print "Name of new assessment"
        print name
        data = {'name': name, 'description': "difficult", 'itemIds': items_ids}
        data = json.dumps(data)

        bank_id = Post.objects.filter(key="bank_id")[0].value

        print "Print bank id"
        print bank_id

        '''
        Create new assessment
        url: assessment/bank/<bank_id>/assessments/
        '''
        resp = req_assess.post(req_assess.url + bank_id + "/assessments/", data)
        print resp
        '''
        This part is not necessary
        '''
        if 'id' in resp.keys():
            print resp['id']
            # sub_id=resp['id']
        else:
            print "Could not create an assessment"
            if 'detail' in resp.keys():
                print resp

        return HttpResponse(json.dumps(resp), content_type="application/json")
    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def delete_assessment(request):
    print "Delete Assessment"

    print request.GET
    try:

        req_assess = AssessmentRequests()
        bank_id = Post.objects.filter(key="bank_id")[0].value
        sub_id = request.GET.getlist('sub_id')[0]

        ''''
        get list of offerings
        '''
        r1 = req_assess.get(req_assess.url + bank_id + '/assessments/' + sub_id + "/assessmentsoffered/")

        if r1.status_code == 200:
            offeringList = r1.json()['data']

            if len(offeringList) > 0:
                for offering in offeringList:
                    offering_id = offering['id']
                    print "offering id"
                    print offering_id

                    '''
                    Get a list of takens for this offering
                    url: /assessment/<bank_id>/assessmentsoffered/<sub_id>/assessmentstaken/
                    '''
                    r4 = req_assess.get(
                        req_assess.url + bank_id + '/assessmentsoffered/' + offering_id + "/assessmentstaken/")
                    if r4.status_code == 200:
                        print "takens"
                        print r4.json()
                        takensList = r4.json()['data']
                        print takensList
                        if len(takensList) > 0:
                            return HttpResponse(
                                json.dumps({'detail': "This offering has tekens and cannot be deleted"}))
                            '''
                            This is deleting all the takens
                            '''
                            # for taken in takensList:
                            # print "taken"
                            #     print taken
                            #     '''
                            #     delete assessment takens
                            #     url:assessment/<bank_id>/assessmentstaken/<taken_id>/
                            #     '''
                            #     r3 = req_assess.delete(req_assess.url+bank_id+'/assessmentstaken/'+taken['id']+'/')
                    else:
                        return HttpResponse(r4)

                    '''
                    delete an offering
                    url:    assessment/<bank_id>/assessmentsoffered/<offering_id>/
                    '''''
                    r2 = req_assess.delete(req_assess.url + bank_id + '/assessmentsoffered/' + offering_id + "/")
                    print r2
                    if r2.status_code != 200:
                        r = {'detail': 'Could not delete the offering, id= ' + offering_id}
                        return HttpResponse(json.dumps(r))

            '''
            Delete an assessment
            url:  assessment/<bank_id>/assessments/<sub_id>/
            '''

            req = req_assess.delete(req_assess.url + bank_id + "/assessments/" + sub_id + '/')
            print "del response"
            print req
            if req.status_code == 200:
                return HttpResponse(json.dumps({'success': 'Assessment deleted successfully'}))
            else:
                req = {'detail': 'Could not delete an assessment ' + str(req.status_code)}
                return HttpResponse(json.dumps(req))
                # return HttpResponse(req)
        else:

            return HttpResponse(r1)

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


'''
Creates new offering for this assessment
'''


@csrf_exempt
def get_offering_id(request):
    print "Get offering id of an Assessment"
    print request.POST

    sub_id = request.POST.getlist('sub_id')[0]
    bank_id = Post.objects.filter(key="bank_id")[0].value

    req_assess = AssessmentRequests()

    '''
    Create new offering
    url: assessment/bank/assessements/<sub_id>/assessmentsoffered/
    '''

    eq4 = req_assess.post(req_assess.url + bank_id + '/assessments/' + sub_id + '/assessmentsoffered/')
    if 'id' in eq4:
        print "offering id"
        print eq4['id']

        return HttpResponse(json.dumps([eq4['id'], bank_id]), content_type='application/json')
    else:
        print eq4
        return HttpResponse(json.dumps(eq4), content_type='application/json')

@csrf_exempt
def rename_assessment(request):
    print "Rename Assessment"
    print request.POST

    try:

        req_assess = AssessmentRequests()
        bank_id = Post.objects.filter(key="bank_id")[0].value
        sub_id = request.POST.getlist('sub_id')[0]
        new_name = request.POST.getlist('name')[0]

        print new_name

        data = {'name': new_name}

        '''
        Change name of assessment
        url: assessment/bank/<bank_id>/assessments/<sub_id>/
        type:'PUT'
        '''
        resp = req_assess.put(req_assess.url + bank_id + "/assessments/" + sub_id + "/", json.dumps(data))
        print resp
        print resp.json()
        return HttpResponse(resp, content_type='application/json')

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def get_items(request):
    print "Get Items of an Assessment"

    # print request.GET
    sub_id = request.GET.getlist('sub_id')[0]
    print sub_id

    try:

        req_assess = AssessmentRequests()
        bank_id = Post.objects.filter(key="bank_id")[0].value
        '''
        Get items of an assessment
        url: assessment/bank/<bank_id>/assessments/<sub_id>/items/
        type: 'GET'
        returns: {'data':[]}
        '''
        resp = req_assess.get(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/")
        items = resp.json()
        # print items
        print "Number of items: " + str(len(items))
        return HttpResponse(json.dumps(items), content_type='application/json')

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


'''
Add item to assessment
'''


@csrf_exempt
def add_item(request):
    print 'Add Item to Assessment'
    print request.POST

    sub_id = request.POST.getlist('sub_id')[0]
    question_id = request.POST.getlist('question_id')[0]
    bank_id = Post.objects.filter(key="bank_id")[0].value

    print sub_id
    print question_id

    data = {"itemIds": [question_id]}

    req_assess = AssessmentRequests()
    '''
    Adding item to assessment
    url: assessment/bank/<bank_id>/assessments/<sub_id>/items/
    data: {"itemIds": [<question_id>]}
    type:POST
    '''
    resp = req_assess.post(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/", json.dumps(data))

    return HttpResponse(json.dumps(resp), content_type='application/json')


'''
Remove one item from the assessment
'''


@csrf_exempt
def remove_item(request):
    print 'Remove Item from Assessment'

    sub_id = request.POST.getlist('sub_id')[0]
    question_id = request.POST.getlist('question_id')[0]
    bank_id = Post.objects.filter(key="bank_id")[0].value

    print sub_id
    print question_id

    req_assess = AssessmentRequests()

    '''
    Delete item form assessment
    url: assessment/bank/<bank_id>/assessments/<sub_id>/items/<question_id>/
    type: DELETE
    '''
    resp = req_assess.delete(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/" + question_id + "/", )

    print resp
    # print resp.json()
    return HttpResponse(resp)


'''
Reorder Items in the assessment
Delete all items
Add items in new (given) order

Question: do I need to create a new offering?
    probably the instructor will need to add a new link to this offering otherwise the old offerings will be lost

Update: The offering is created only when the instructor requests it
All offerings are preserved
At some moment, for example, when reordering items or when requesting new offering, check if
 there are any offerings for this assessment that do not have takens

'''


@csrf_exempt
def reorder_items(request):
    print "Rearrange items in assessment"
    print request.POST
    bank_id = Post.objects.filter(key="bank_id")[0].value

    items_ids = request.POST.getlist('items[]')
    # print "Items to be added"
    #print items_ids

    sub_id = request.POST.getlist('sub_id')[0]
    print "<sub_id>"
    print sub_id

    data = {"itemIds": items_ids}

    #  deleteOfferings(bank_id,sub_id) #returns true, can put in if statement
    resp = replaceAllItems(bank_id, sub_id, data)
    return HttpResponse(json.dumps(resp), content_type='application/json')


'''
Update list of assessments
'''''''''''''''''''''


@csrf_exempt
def update_assessments(request):
    print "Update assessments"
    print request.GET

    req_assess = AssessmentRequests()
    bank_id = Post.objects.filter(key="bank_id")[0].value

    eq2 = req_assess.get(req_assess.url + bank_id + "/assessments/")
    assessments = eq2.json()['data']
    # print assessments
    return HttpResponse(json.dumps(assessments), content_type='application/json')


'''''''''''''''''''''''''''''
'Helper functions'
'''''''''''''''''''''''''''''
'''
Replace old item list with the new one
Delete each item one by one, add new list of items
'''


def replaceAllItems(bank_id, sub_id, data):
    print "ReplaceAllItems"

    req_assess = AssessmentRequests()

    items = getItems(bank_id, sub_id).json()
    items = items['data']
    print "Number of items in this assessment: " + str(len(items))
    for item in items:
        print item['id']
        question_id = item['id']
        print "Delete item"
        resp = req_assess.delete(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/" + question_id + "/", )
        # print resp

    '''
    Add new list of items only if the assessment is empty
    '''
    resp1 = getItems(bank_id, sub_id).json()
    if len(resp1['data']) < 1:
        resp = req_assess.post(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/", json.dumps(data))
        return resp
    else:
        return '{"detail":"Could not replace items"}'


'''
Get a list of items in this assessment
'''


def getItems(bank_id, sub_id):
    print "Get Items"
    req_assess = AssessmentRequests()
    resp = req_assess.get(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/")
    return resp


'''
Get the list of all offerings
for each offering find the takens
    for each taken
        delete taken
    delete offering
'''


def deleteOfferings(bank_id, sub_id):
    print "Deleting Offerings"

    req_assess = AssessmentRequests()
    '''
    Get list of offerings
    url: /assessment/<bank_id>/assessments/<sub_id>/assessmentsoffered/
    '''
    r1 = req_assess.get(req_assess.url + bank_id + '/assessments/' + sub_id + "/assessmentsoffered/")
    # print "response assessments offered"
    # print r1
    if r1.status_code == 200:
        data = r1.json()['data']

        if len(data) > 0:
            '''
            Want to delete all offerings
            '''
            print "number of offerings: " + str(len(data))
            for offering in data:
                offering_id = offering['id']
                print offering['id']
                '''
                Get a list of takens for this assessment
                url: /assessment/<bank_id>/assessmentsoffered/<sub_id>/assessmentstaken/
                '''
                r4 = req_assess.get(
                    req_assess.url + bank_id + '/assessmentsoffered/' + offering_id + "/assessmentstaken/")
                if r4.status_code == 200:
                    print "takens"
                    print r4.json()
                    takensList = r4.json()['data']
                    print takensList
                    if len(takensList) > 0:
                        for taken in takensList:
                            print "taken"
                            print taken
                            print "delete this taken"
                            '''
                            delete assessment takens
                            url:assessment/<bank_id>/assessmentstaken/<taken_id>/
                            '''
                            r3 = req_assess.delete(req_assess.url + bank_id + '/assessmentstaken/' + taken['id'] + '/')

                            print r3
                    else:
                        print "no takens for this assessment"
                else:
                    print("Error: could not get list of takens")
                    print(r4)

                    # return HttpResponse(r4)
                '''
                Now we can delete this offering
                '''
                '''
                delete an offering
                url:    assessment/<bank_id>/assessmentsoffered/<offering_id>/
                '''''
                r2 = req_assess.delete(req_assess.url + bank_id + '/assessmentsoffered/' + offering_id + "/")
                print r2


        else:
            print("Offerings list is empty")
        return True

    else:
        print("Error getting the offerings")
        print r1
        return False


def submitGrade(bank_id, taken_id, params):

    questions = getQuestions(bank_id, taken_id)
    num_questions = len(questions)
    if num_questions > 0:
        print "Num of questions "+str(num_questions)
        count_correct_ans = 0
        for a in questions:
            if a['responded'] == 'Correct':
                count_correct_ans += 1

        consumer_key = settings.CONSUMER_KEY
        secret = settings.LTI_SECRET
        print consumer_key
        print secret
        tool = DjangoToolProvider(consumer_key, secret, params)
        post_result = tool.post_replace_result(count_correct_ans/float(num_questions))
        print post_result.is_success()


def readyToSubmit():
    return True


