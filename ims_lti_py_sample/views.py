import pickle

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ims_lti_py.tool_provider import DjangoToolProvider

from django.conf import settings
from django.http import Http404

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import oauth2

from .utilities import *
import base64
import ast
from django.core.cache import cache


def flush():
    cache.clear()
    print "Cleared CACHE"


'''
If the 'tool_consumer_instance_guid' LTI parameter is not passed want to get
the IP address
'''
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
def index(request):
    if settings.LTI_DEBUG:
        print "META"
        print request.META
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
    params = {}
    Post.objects.all().delete()
    for k in request.POST:
        params[k] = request.POST[k]
        p = Post(key=k, value=request.POST[k])
        p.save()
        # print str(k)+"   "+str(request.POST[k])
        #print k

    '''
    Make sure there is 'tool_consumer_instance_guid' in POST
    '''
    if 'tool_consumer_instance_guid' not in params:
        print 'tool_consumer_instance_guid not in params'
        params['tool_consumer_instance_guid'] = get_client_ip(request)


    '''Creating a unique identifier for the user'''
    unique_id = params['user_id']+params['tool_consumer_instance_guid']

    ''' make sure we delete the previous session'''
    Parameters.objects.filter(key=unique_id).delete()

    '''Saving parameters for each user'''
    Parameters(key=unique_id, value=json.dumps(params)).save()

    '''save unique identifier to session'''
    session['unique_id'] = unique_id


    '''
    Save the url, public_key, private_key
    '''
    print request.POST['roles']
    if 'Instructor' in request.POST['roles']:
        return redirect('InstructorView')
    elif 'Administrator' in request.POST['roles']:
        return redirect('InstructorView')
    elif "Learner" or 'student' in request.POST['roles']:
        return redirect('StudentView')
    else:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def student(request):
    print "Student View"
    params = {}
    unique_id = request.session.get('unique_id')

    try:
        '''old'''
        for g in Post.objects.all():
            params[g.key] = g.value
        '''new'''
        user_obj=Parameters.objects.filter(key=unique_id)[0]
        params = ast.literal_eval(user_obj.value)

        ###############
        # Remove this when done with Post
        ##############
        if 'tool_consumer_instance_guid' not in params:
            print 'tool_consumer_instance_guid not in params'
            # params['tool_consumer_instance_guid'] = get_client_ip(request)

            '''old'''
            p = Post(key='tool_consumer_instance_guid', value=params['tool_consumer_instance_guid'])
            p.save()
            '''new
            will save params later
            '''



        student_req = AssessmentRequests('taaccct_student')

        '''
        get bank id and offering id
        request questions for this assessment
        '''
        bank_id = params['custom_bank_id']
        offering_id = params['custom_offering_id']
        name = 'none'
        if 'lis_person_name_given' in params:
            name = params["lis_person_name_given"]
            print name
            name = name.replace("-", "")

        print bank_id
        print offering_id

        '''
        create new taken
        and get the taken_id
        assessment/banks/<bank_id>/assessmentsoffered/<offering_id>/asessmentstaken/
        '''
        resp = student_req.post(
            student_req.url + bank_id + "/assessmentsoffered/" + offering_id + "/assessmentstaken/")  # /assessmentstaken/
        print "Create or request a taken"
        print resp


        if 'id' in resp:
            taken_id = resp['id']

            '''old'''
            Post.objects.filter(key="taken_id").delete()
            p = Post(key="taken_id", value=taken_id)
            p.save()
            '''new'''
            params['taken_id']=taken_id


            print "Got Taken Id"
            print taken_id
            print resp['reviewWhetherCorrect']

            '''
            This is the attribute that controls whether the answers should be visible to the student or not
            '''
            review_whether_correct= resp['reviewWhetherCorrect']
            # review_whether_correct = False
            grade='none'
            '''old'''
            Post.objects.filter(key="see_answer").delete()
            Post(key="see_answer", value=review_whether_correct).save()
            '''new'''
            params['see_answer']=review_whether_correct


            questions = getQuestions(bank_id, taken_id)
            if review_whether_correct:
                grade = int(getOverallGrade(bank_id,taken_id)*1000)/float(10)


            '''
            Want to check if the student answered all questions
            '''
            answered_all_questions=answeredAllQuestions(questions)

            #Want to get name of the assessment, but there is not name in the details
            '''
            Get details of an assessment taken
            url: assessment/banks/<bank_id>/assessmentstaken/<taken_id>/
            type: "GET"
            '''
            print student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/"
            # resp2 = student_req.post(
            #     student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/")
            #End

            '''
            Saving a smaller list for calculating the question menu faster
            '''
            sm_questions=[]
            for i,a in enumerate(questions):
                sm_questions.append({
                    'number': a['number'],
                    'id': a['id'],
                    'responded': a['responded']
                })

            params['sm_questions'] = sm_questions

            '''
            Need to save params before leaving
            '''

            print user_obj.value
            user_obj.value = params
            user_obj.save()

            if 'detail' in questions:
                return render_to_response("ims_lti_py_sample/error.html", RequestContext(request,{'error':'Could not get questions'}))
            return render_to_response("ims_lti_py_sample/home_student.html",
                                          RequestContext(request, {'userName': name, 'questions': questions, 'grade': grade,
                                                                   'consumer':params['tool_consumer_info_product_family_code'],
                                                                   'answered_all_questions': answered_all_questions,
                                                                   'welcome': True,
                                                                    # 'return_url':params['launch_presentation_return_url'],
                                                                    'seeAnswer': review_whether_correct}))

        else:
            detail= resp['detail']
            print resp['detail']
            return render_to_response("ims_lti_py_sample/student_error.html",
                                      RequestContext(request, {'userName': name,
                                                               'consumer':params['tool_consumer_info_product_family_code'],
                                                               'error': detail,
                                                               'location': "Getting AssessmentTaken"
                                                               }))
    except KeyError, e:
        return render_to_response("ims_lti_py_sample/errorNew.html", RequestContext(request, {'error': e,
                                                                                              'params': params}))
    except Exception, e:
        # return render_to_response("ims_lti_py_sample/error.html", RequestContext(request, {'error': e}))
        return render_to_response("ims_lti_py_sample/student_error.html",
                                  RequestContext(request, {
                                      'consumer': params['tool_consumer_info_product_family_code'],
                                      'error': e,
                                      'location': "Inside Student"
                                  }))

        # raise Http404




@csrf_exempt
def student_home(request):
    try:
        '''
        get bank id and offering id
        request questions for this assessment
        '''
        unique_id= request.session.get('unique_id')
        '''old'''
        params = {}
        for g in Post.objects.all():
            params[g.key] = g.value
        ''' new'''

        # user_obj=Parameters.objects.filter(key=unique_id)[0]
        # params = ast.literal_eval(user_obj.value)
        params = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)


        bank_id = params['custom_bank_id']
        taken_id = params['taken_id']
        print type(params['see_answer'])
        review_whether_correct = params['see_answer']
        print "REview weather correct"
        print review_whether_correct

        name = 'none'
        grade = 'none'
        if 'lis_person_name_given' in params:
            name = params["lis_person_name_given"]

        questions = getQuestions(bank_id, taken_id)


        # print user_obj.value
        # user_obj.value = params
        # user_obj.save()

        answered_all_questions = answeredAllQuestions(questions)

        if review_whether_correct:
            grade = int(getOverallGrade(bank_id,taken_id)*1000)/float(10)






        print "all questions: "
        print answered_all_questions

        if 'detail' in questions:
                return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))

        return render_to_response("ims_lti_py_sample/home_student.html",
                                      RequestContext(request, {'userName': name, 'questions': questions,'grade':grade,
                                                               'consumer':params['tool_consumer_info_product_family_code'],
                                                               'answered_all_questions': answered_all_questions,
                                                               'seeAnswer': review_whether_correct}))

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request,{'error': e}))

@csrf_exempt
def submit_grade(request):
    print "Sumbit Grade"
    unique_id = request.session.get('unique_id')

    try:
        '''
        get bank id and offering id
        request questions for this assessment
        '''
        params = {}
        for g in Post.objects.all():
            params[g.key] = g.value
        '''new'''
        params = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)


        bank_id = params['custom_bank_id']
        taken_id = params['taken_id']

        submitGradeToConsumer(bank_id, taken_id, params)
        if not params['see_answer']:
            finishAssessment(bank_id,taken_id)

        return HttpResponse(json.dumps({'return_url': params['launch_presentation_return_url']}), content_type='application/json')

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request,{'error': e}))

'''
Get questions for this taken
add status to each question
'''
def getQuestions(bank_id, taken_id):
    print "Get Questions"

    student_req = AssessmentRequests('taaccct_student')

    '''
    Get questions from this assessment
    assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/

    '''
    print student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/questions/"
    resp1 = student_req.get(student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/questions/")
    resp1 = resp1.json()
    # print resp1
    if 'detail' in resp1:
        return resp1
    questions = resp1['data']['results']  # a list of questions
    for i, a in enumerate(questions):
        print a['displayName']['text']
        a['number'] = i+1
        '''
        Get status of the question
        url: assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/status/
        type: 'GET'
        '''
        resp2 = student_req.get(student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/questions/" + a['id']
                                + '/status/')
        resp2 = resp2.json()
        print resp2
        # print resp2['responded']
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
    unique_id = request.session.get('unique_id')
    # print request.POST
    '''
    Data -> [ text.text, innerText, id], e.g [ question, question_name, question_id]
    '''
    data = request.POST.getlist('data[]')
    #print data

    print "Size of data " + str(len(data))
    print "selected question"

    question_id = data[0]

    print question_id



    #make sure there isn't one in the database already
    '''old'''
    Post.objects.filter(key="question_id").delete()
    '''new'''
    user_obj=Parameters.objects.filter(key=unique_id)[0]
    params = ast.literal_eval(user_obj.value)


    '''old'''
    Post(key="question_id", value=question_id).save()
    '''new'''
    params['question_id']=question_id

    '''Save params'''
    # print user_obj.value
    user_obj.value = params
    user_obj.save()


    question = {'success': True, 'redirect': True, 'redirectURL': "display_question"}  #d_question  display_question
    return HttpResponse(json.dumps(question), content_type='application/json')


@csrf_exempt
def display_question(request):

    unique_id = request.session.get('unique_id')

    try:
        print "Display question"
        # print request
        params = {}
        for g in Post.objects.all():
            params[g.key] = g.value

        '''new'''
        params = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)


        bank_id = params['custom_bank_id']
        taken_id = params['taken_id']
        question_id = params['question_id']
        review_whether_correct = params['see_answer']
        student_req = AssessmentRequests('taaccct_student')

        questions = getQuestions(bank_id, taken_id)
        if 'detail' in questions:
                # return render_to_response("ims_lti_py_sample/error.html", RequestContext(request,{'error': questions['detail']}))

                return render_to_response(("ims_lti_py_sample/student_error.html"),
                                      RequestContext(request, {
                                                               'consumer': params['tool_consumer_info_product_family_code'],
                                                               'error': questions['detail'],
                                                               'location': "Getting questions"
                                                               }))


        '''
        It would have been much easier if the questions in assessmentTaken were numbered already
        '''
        '''
        Have to identify what is the number of the current question
        '''
        question_number = 0

        next_quest_id = "home"
        prev_quest_id = "home"
        for i, a in enumerate(questions):
            if a['id'] == question_id:
                question_number = a['number']
                if i <len(questions)-1:
                    next_quest_id = questions[i + 1]['id']
                if i != 0:
                    prev_quest_id = questions[i-1]['id']



        '''
        Want to modify the list of questions to have at most five questions around the current question
        '''
        questions_to_right=0
        questions_to_left=0
        print "question number is " + str(question_number)
        sm_list = [questions[question_number-1]]
        if len(questions) > 5:
            if question_number==1:
                questions_to_right=4
            elif question_number==2:
                questions_to_right=3
                questions_to_left=1
            elif question_number == len(questions):
                print "this is the last question"
                questions_to_left=4
            elif question_number == len(questions)-1:
                questions_to_right=1
                questions_to_left=3

            else:
                questions_to_left = 2
                questions_to_right = 2

            for i in range(1, questions_to_left+1, 1):
                print 'adding question ' + str(questions[question_number-i-1]['number'])
                sm_list.insert(0, questions[question_number-i-1])


            for i in range(1, questions_to_right+1, 1):
                print 'adding question ' + str(questions[question_number+i-1]['number'])
                sm_list.append(questions[question_number+i-1])

            if question_number > 3:
                print " add ...789"
                sm_list.insert(0, {'number': -1})
            if len(questions)-question_number > 2:
                print "add 789..."
                sm_list.append({'number': 0})

            questions = sm_list
            print "Question number " + str(question_number)
            for a in sm_list:
                print a['number']





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

        q_name = resp2.json()['displayName']['text']
        '''
        Writing the manip file
        '''
        if 'detail' in resp2.json():
            print 'has detail'
        print resp2.json()
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
        question = resp2.json()['text']['text']


        # next_quest_id = getNextQuestionId('next', questions, question_id)
        # prev_quest_id = getNextQuestionId('prev', questions, question_id)

        print "small list"
        print type(sm_list)
        print sm_list[0]
        print len(sm_list)


        if "label-ortho-faces" in question_record_type:

            return render_to_response("ims_lti_py_sample/unity.html", RequestContext(request,
                                                     {'question_name': q_name, 'question': question,

                                                      'question_number': question_number,
                                                      'small_list': questions,
                                                      'question_type': question_type,
                                                      'next_quest_id': next_quest_id,
                                                      'prev_quest_id': prev_quest_id,
                                                      'seeAnswer': review_whether_correct}))
        else:
            if "choose-viewset" in question_type:
                list_choices = resp2.json()['choices']
                for i, c in enumerate(list_choices):
                    # print c['name']
                    # print c['id']
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
                                                          'questions': questions, 'question_number': question_number,
                                                          'small_list': sm_list,
                                                          'question_type': question_type, "choices": list_choices,
                                                          'next_quest_id': next_quest_id,
                                                          'prev_quest_id': prev_quest_id,
                                                          'seeAnswer': review_whether_correct}))
            else:
                return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))




    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request,{'error': e}))  # # Testin unity web player


def getNextQuestionId(next,questions,question_id):
    new_id = ''
    for i, a in enumerate(questions):
        if a['id'] == question_id:
            if 'next' in next:
                new_id = questions[i + 1]['id']
            else:
                new_id = questions[i-1]['id']

    return new_id



'''
This function computes the requested set of questions
Expectes 2 parameters: last_number,
'''
@csrf_exempt
def update_questions_menu(request):
    print "Update Questions Menu"
    unique_id = request.session.get('unique_id')

    last_num = int(request.POST.getlist('last_number')[0])
    print request.POST.getlist('next')
    next_bool = 'true' in request.POST.getlist('next')[0]  # can be 'next' or 'prev'
    print type(next_bool)
    print last_num
    params = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)

    # questions = getQuestions(params['custom_bank_id'],params['taken_id'])
    questions = params['sm_questions']
    print type(questions)
    # questions = ast.literal_eval(questions)
    # print type(questions)

    length =len(questions)
    sm_list =[]
    print "Next"
    print next_bool
    if next_bool:
        if length-last_num >= 4:
            sm_list.append({'number': -1})
            sm_list.append(questions[last_num-1])   # append first the last number in the old list, to be the first now
            for i in range(last_num, last_num+4):   # then append the next 4 questions to the list
                sm_list.append(questions[i])
            if length-last_num>4:
                sm_list.append({'number': 0})
        else:
            for i in range(1,6):
                sm_list.insert(0,questions[length-i])
            sm_list.insert(0, {'number': -1})
    else:
        #  in this case the last_number will be the last on the left, meaning the smallest question number
        if last_num>5:
            sm_list.append({'number': -1})
            for i in range(last_num-6,last_num):
                sm_list.append(questions[i])
            sm_list.append({'number': 0})
        else:
            for i in range(0, 5):
                sm_list.append(questions[i])
            sm_list.append({'number': 0})







    return HttpResponse(json.dumps(sm_list), content_type='application/json')





@csrf_exempt
def submit_answer(request):
    print "Submit answer"

    unique_id = request.session.get('unique_id')

    answer = request.POST.getlist('answer')[0]
    print answer

    params = {}
    for g in Post.objects.all():
        params[g.key] = g.value

    params = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)

    bank_id = params['custom_bank_id']
    taken_id = params['taken_id']
    question_id = params['question_id']

    student_req = AssessmentRequests('taaccct_student')
    resp = student_req.post(
        student_req.url + bank_id + '/assessmentstaken/' + taken_id + '/questions/' + question_id + '/submit/',
        json.dumps(answer))
    print "Got answer back"
    resp['see_answer']=params['see_answer']
    print resp
    # if params['see_answer']=='True':
    #     resp['overall_grade'] = submitGrade(bank_id, taken_id, params)


    return HttpResponse(json.dumps(resp), content_type='application/json')


@csrf_exempt
def submit_multi_answer(request):
    print "Submit multi choice answer"
    unique_id = request.session.get('unique_id')

    answer = request.POST.getlist('answer')[0]
    print answer

    params = {}
    for g in Post.objects.all():
        params[g.key] = g.value

    params = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)

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

    resp2['see_answer']=params['see_answer']

    request_post = params["lis_outcome_service_url"] #???
    print request_post

    # if params['see_answers'] == 'True':
    #     submitGrade(bank_id, taken_id, params)

    return HttpResponse(json.dumps(resp2), content_type='application/json')



@csrf_exempt
def instructor(request):
    print "Instructor View"
    # print key
    print request.session.get('unique_id')


    try:
        #getting the unique identifier of the user
        unique_id = request.session.get('unique_id')
        #getting parameters for the user
        params={}

        params = Parameters.objects.filter(key=unique_id).values()[0]['value']
        params= ast.literal_eval(params)
        # params = params.json()
        print type(params)
        print params['user_id']

        req_assess = AssessmentRequests()
        '''
        Get list of banks
        url: assessment/banks
        '''
        eq = req_assess.get(req_assess.url)
        banks = eq.json()['data']['results']

        print "Number of banks: " + str(len(banks))
        found = False
        bank_id = ""
        for a in banks:
            if a['displayName']['text'] == "Ortho 3D":
                print "Found Ortho 3D"
                found = True

                bank_id = a['id']
                '''
                old version
                '''
                Post.objects.filter(key="bank_id").delete()
                p = Post(key="bank_id", value=bank_id)
                p.save()
                '''
                new
                '''
                # print type(params)
                params['bank_id']=bank_id
                # print bank_id

        if found:
            '''
            Get a list of assessments in a bank
            assessment/banks/<bank_id>/assessments/

            '''
            # print str(req_assess.url) + str(bank_id)+"/assessments/"

            eq2 = req_assess.get(req_assess.url + bank_id + "/assessments/")

            assessments = eq2.json()['data']['results']
            print "Number of assessments: " + str(len(assessments))

            for a in assessments:
                print a['displayName']['text']  # Assessment name

            '''
            Get a list of items in a bank
            assessment/banks/<bank_id>/items/
            '''
            eq3 = req_assess.get(req_assess.url + bank_id + "/items/")
            print "Status code getting items:  " + str(eq3.status_code)
            items = eq3.json()['data']['results']
            count = eq3.json()['data']['count']
            print "Number of items: " + str(count)
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
            name = 'none'
            print "counting number of keys"

            '''
            old version
            '''
            print Post.objects.filter(key='lis_person_name_given').count()
            if Post.objects.filter(key='lis_person_name_given').count() > 0:
                name = Post.objects.filter(key='lis_person_name_given')[0].value
                print name
                name = name.replace("-", "")

            '''
            new version
            '''
            if params['lis_person_name_given']:
                name = name.replace("-", "")
                print name

            '''
            save updated parameters
            '''
            # Parameters(key=unique_id,value=params).save()
            user_obj=Parameters.objects.filter(key=unique_id)[0]
            print "User Params"
            print user_obj
            user_obj.value = params
            user_obj.save()

            # request.COOKIES['unique_id'] = unique_id

            return render_to_response("ims_lti_py_sample/instructor.html",
                                      RequestContext(request,
                                                     {'user_name': name,
                                                      'assessments': assessments, 'items': items,
                                                      'items_type1': items_type1, 'items_type2': items_type2,
                                                      'items_type3': items_type3, 'items_type4': items_type4}))
        else:
            print "No bank Ortho 3D found"

    except KeyError, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext(request))


@csrf_exempt
def create_assessment(request):
    print "Create new assessment"

    print request.session.get('unique_id')
    unique_id = request.session.get('unique_id')


    # print request.POST
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

        '''old'''
        bank_id = Post.objects.filter(key="bank_id")[0].value
        '''new'''
        bank_id=ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']

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

'''
If the assessment has takens it will not be deleted
'''
@csrf_exempt
def delete_assessment(request):
    print "Delete Assessment"

    print request.GET
    unique_id = request.session.get('unique_id')

    try:

        req_assess = AssessmentRequests()

        '''old'''
        bank_id = Post.objects.filter(key="bank_id")[0].value
        '''new'''
        bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']

        sub_id = request.GET.getlist('sub_id')[0]


        ''''
        get list of offerings
        '''
        r1 = req_assess.get(req_assess.url + bank_id + '/assessments/' + sub_id + "/assessmentsoffered/")

        if r1.status_code == 200:
            offeringList = r1.json()['data']['results']

            if len(offeringList) > 0:
                for offering in offeringList:
                    offering_id = offering['id']
                    print "offering id"
                    print offering_id

                    #The following code checks if an offering has a taken
                    #
                    '''
                    Get a list of takens for this offering
                    url: /assessment/<bank_id>/assessmentsoffered/<sub_id>/assessmentstaken/
                    '''
                    # r4 = req_assess.get(
                    #     req_assess.url + bank_id + '/assessmentsoffered/' + offering_id + "/assessmentstaken/")
                    # if r4.status_code == 200:
                    #     print "takens"
                    #     print r4.json()
                    #     takensList = r4.json()['data']['results']
                    #     print takensList
                    #     if len(takensList) > 0:
                    #         return HttpResponse(
                    #             json.dumps({'detail': "This offering has tekens and cannot be deleted"}))
                    #         '''
                    #         This is deleting all the takens
                    #         '''
                            # for taken in takensList:
                            # print "taken"
                            #     print taken
                            #     '''
                            #     delete assessment takens
                            #     url:assessment/<bank_id>/assessmentstaken/<taken_id>/
                            #     '''
                            #     r3 = req_assess.delete(req_assess.url+bank_id+'/assessmentstaken/'+taken['id']+'/')
                    # else:
                    #     return HttpResponse(r4)

                    '''
                    delete an offering
                    url:    assessment/<bank_id>/assessmentsoffered/<offering_id>/
                    '''''
                    r2 = req_assess.delete(req_assess.url + bank_id + '/assessmentsoffered/' + offering_id + "/")
                    print "Delete offering"
                    print r2
                    if r2.status_code != 200:
                        # r = {'detail': 'Could not delete the offering, id= ' + offering_id}
                        return HttpResponse(r2)

            '''
            Delete an assessment
            url:  assessment/<bank_id>/assessments/<sub_id>/
            '''

            req = req_assess.delete(req_assess.url + bank_id + "/assessments/" + sub_id + '/')
            print "delete assessment"
            print req
            if req.status_code == 200:
                return HttpResponse(json.dumps({'success': 'Assessment deleted successfully'}))
            else:
                #req = {'detail': 'Could not delete an assessment ' + str(req.status_code)}
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

    unique_id=request.session.get('unique_id')

    sub_id = request.POST.getlist('sub_id')[0]
    see_answer = request.POST.getlist('see_answer')[0]
    see_answer = see_answer == 'true'

    '''old'''
    bank_id = Post.objects.filter(key="bank_id")[0].value
    '''new'''
    bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']


    req_assess = AssessmentRequests()
    print "See Answer"
    print see_answer
    data={"reviewOptions" : {
        "whetherCorrect" : {
                "duringAttempt" : see_answer
        }
    }}
    data = json.dumps(data)

    '''
    Create new offering
    url: assessment/bank/assessements/<sub_id>/assessmentsoffered/
    '''

    eq4 = req_assess.post(req_assess.url + bank_id + '/assessments/' + sub_id + '/assessmentsoffered/', data)
    if 'id' in eq4:
        print "offering id"
        print eq4['id']

        return HttpResponse(json.dumps({'data': [eq4['id'], bank_id]}), content_type='application/json')
    else:
        print eq4
        return HttpResponse(json.dumps(eq4), content_type='application/json')

@csrf_exempt
def rename_assessment(request):
    print "Rename Assessment"
    print request.POST
    unique_id = request.session.get('unique_id')

    try:

        req_assess = AssessmentRequests()

        '''old'''
        bank_id = Post.objects.filter(key="bank_id")[0].value
        '''new'''
        bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']

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

    unique_id = request.session.get("unique_id")

    # print request.GET
    sub_id = request.GET.getlist('sub_id')[0]
    print sub_id

    try:

        req_assess = AssessmentRequests()
        '''old'''
        bank_id = Post.objects.filter(key="bank_id")[0].value
        '''new'''
        bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']
        '''
        Get items of an assessment
        url: assessment/bank/<bank_id>/assessments/<sub_id>/items/
        type: 'GET'
        returns: {'data':[]}   OLD
        returns: {'data': { count:'',results:[]}}
        '''
        resp = req_assess.get(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/")
        items = resp.json()
        if 'data' in items.keys():
            items = resp.json()['data']['results']
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
    unique_id=request.session.get("unique_id")

    sub_id = request.POST.getlist('sub_id')[0]
    question_id = request.POST.getlist('question_id')[0]

    '''old'''
    bank_id = Post.objects.filter(key="bank_id")[0].value
    '''new'''
    bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']



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
    unique_id=request.session.get("unique_id")

    sub_id = request.POST.getlist('sub_id')[0]
    question_id = request.POST.getlist('question_id')[0]

    bank_id = Post.objects.filter(key="bank_id")[0].value
    bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']



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
    unique_id=request.session.get("unique_id")

    bank_id = Post.objects.filter(key="bank_id")[0].value
    bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']

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
    unique_id=request.session.get("unique_id")

    req_assess = AssessmentRequests()
    bank_id = Post.objects.filter(key="bank_id")[0].value
    bank_id = ast.literal_eval(Parameters.objects.filter(key=unique_id)[0].value)['bank_id']

    eq2 = req_assess.get(req_assess.url + bank_id + "/assessments/")
    assessments = eq2.json()['data']['results']
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

    items = getItems(bank_id, sub_id) #returns a list of items
    # items = items['data']
    # print "Number of items in this assessment: " + str(len(items))
    for item in items:
        print item['id']
        question_id = item['id']
        print "Delete item"
        resp = req_assess.delete(req_assess.url + bank_id + "/assessments/" + sub_id + "/items/" + question_id + "/", )
        # print resp

    '''
    Add new list of items only if the assessment is empty
    '''
    resp1 = getItems(bank_id, sub_id)
    if len(resp1) < 1:
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
    return resp.json()['data']['results']


'''
Get the list of all offerings
for each offering find the takens
    for each taken
        delete taken
    delete offering
'''

#this is not used
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

def getOverallGrade(bank_id, taken_id):
    questions = getQuestions(bank_id, taken_id)
    num_questions = len(questions)
    grade=0
    if num_questions > 0:
        print "Num of questions "+str(num_questions)
        count_correct_ans = 0
        for a in questions:
            if a['responded'] == 'Correct':
                count_correct_ans += 1

        grade=count_correct_ans/float(num_questions)

    return grade

def submitGradeToConsumer(bank_id, taken_id, params):

    grade=getOverallGrade(bank_id,taken_id)
    print grade
    consumer_key = settings.CONSUMER_KEY
    secret = settings.LTI_SECRET
    tool = DjangoToolProvider(consumer_key, secret, params)
    try:
        post_result = tool.post_replace_result(grade)
    except Exception, e:
        return render_to_response("ims_lti_py_sample/error.html", RequestContext({'error':' Could not report grades to the consumer'}))
    print post_result.is_success()
    # print "See Answer"
    # print type(params['see_answer'])

def finishAssessment(bank_id, taken_id):
    student_req = AssessmentRequests('taaccct_student')

    '''
    Finish this assessment
    assessment/banks/<bank_id>/assessmentstaken/<taken_id>/finish/

    '''
    print "Finish Assessment"
    print student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/finish/"
    resp1 = student_req.post(student_req.url + bank_id + "/assessmentstaken/" + taken_id + "/finish/")
    # resp1 = resp1.json()
    print resp1

def answeredAllQuestions(questions):
    # all_answered=True
    for a in questions:
        # print "Type: "
        # print type(a['responded'])
        if 'None' in a['responded']:
            return False

    return True

def readyToSubmit():
    return True


