from django.conf.urls import url, patterns, include
from django.utils import importlib


urlpatterns = patterns('',
    url(r'^$', 'ims_lti_py_sample.views.index', name='lti_index'),
    url(r'^/$', 'ims_lti_py_sample.views.index', name='lti_index'),
   # url(r'^add$', 'ims_lti_py_sample.views.add_problem', name='AddProblem'),

    url(r'^instructor$', 'ims_lti_py_sample.views.instructor', name='InstructorView'),
    url(r'^student$', 'ims_lti_py_sample.views.student', name='StudentView'),

    url(r'^create_assessment$', 'ims_lti_py_sample.views.create_assessment', name='Create'),
    url(r'^get_items$', 'ims_lti_py_sample.views.get_items',name="GetItems"),
     url(r'^get_offering_id$', 'ims_lti_py_sample.views.get_offering_id',name="GetOfferingID"),
    url(r'^add_item$', 'ims_lti_py_sample.views.add_item',name="AddItem"),
    url(r'^remove_item$', 'ims_lti_py_sample.views.remove_item',name="RemoveItem"),
    url(r'^del_assess$', 'ims_lti_py_sample.views.delete_assessment',name="DelAssessment"),
    url(r'^update_assess$', 'ims_lti_py_sample.views.update_assessments',name="UpdateAssessment"),

   # url(r'^items/(?P<sub_id>[-.:@%\d\w]+)/$', 'ims_lti_py_sample.views.assessment_items', name='AssessmentItems'),

   #############
   #For student
   #############
   url(r'^get_question$', 'ims_lti_py_sample.views.get_question', name='Question'),
   url(r'^display_question$', 'ims_lti_py_sample.views.display_question', name='DisplayQuestion'),
   url(r'^submit_answer$', 'ims_lti_py_sample.views.submit_answer', name='SubmitAnswer'),


   #for testing
   url(r'^UnityWebPlayer$', 'ims_lti_py_sample.views.d_question', name='DisplayQuestion'),



)
