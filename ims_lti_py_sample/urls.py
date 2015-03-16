from django.conf.urls import url, patterns, include
from django.utils import importlib


urlpatterns = patterns('',
                       url(r'^$', 'ims_lti_py_sample.views.index', name='lti_index'),
                       url(r'^/$', 'ims_lti_py_sample.views.index', name='lti_index'),

                       url(r'^instructor$', 'ims_lti_py_sample.views.instructor', name='InstructorView'),
                       url(r'^student$', 'ims_lti_py_sample.views.student', name='StudentView'),

                       url(r'^create_assessment$', 'ims_lti_py_sample.views.create_assessment', name='Create'),
                       url(r'^get_items$', 'ims_lti_py_sample.views.get_items', name="GetItems"),
                       url(r'^get_offering_id$', 'ims_lti_py_sample.views.get_offering_id', name="GetOfferingID"),
                       url(r'^add_item$', 'ims_lti_py_sample.views.add_item', name="AddItem"),
                       url(r'^remove_item$', 'ims_lti_py_sample.views.remove_item', name="RemoveItem"),
                       url(r'^del_assess$', 'ims_lti_py_sample.views.delete_assessment', name="DelAssessment"),
                       url(r'^update_assess$', 'ims_lti_py_sample.views.update_assessments', name="UpdateAssessment"),
                       url(r'^reorder_items$', 'ims_lti_py_sample.views.reorder_items', name="ReorderItems"),
                       url(r'^rename_assessment$', 'ims_lti_py_sample.views.rename_assessment',
                           name="RenameAssessment"),

                       url(r'^responses$', 'ims_lti_py_sample.views.get_student_response', name='GetResponse'),


                       # url(r'^items/(?P<sub_id>[-.:@%\d\w]+)/$', 'ims_lti_py_sample.views.assessment_items', name='AssessmentItems'),

                       # ############
                       # For student
                       #############
                       url(r'^get_question$', 'ims_lti_py_sample.views.get_question', name='Question'),
                       url(r'^display_question$', 'ims_lti_py_sample.views.display_question', name='DisplayQuestion'),
                       url(r'^submit_answer$', 'ims_lti_py_sample.views.submit_answer', name='SubmitAnswer'),
                       url(r'^submit_multi_answer$', 'ims_lti_py_sample.views.submit_multi_answer',
                           name='SubmitAnswer'),
                       url(r'^student_home$', 'ims_lti_py_sample.views.student_home', name='Home'),
                       url(r'^submit_grade$', 'ims_lti_py_sample.views.submit_grade', name='SubmitGrade'),
                       url(r'^update_questions_menu$', 'ims_lti_py_sample.views.update_questions_menu', name='UpdateMenu'),


                       #for testing
                       # url(r'^UnityWebPlayer$', 'ims_lti_py_sample.views.d_question', name='DisplayQuestion'),



)
