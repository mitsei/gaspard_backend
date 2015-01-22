/**
 * Created by anna on 8/4/14.
 */
var selectedAssessment = null;
var selectedBankItems = [];
var wait=false;

$(document).ready(function () {


    $("#see-answer").change(function(){
        console.log('changed');
        if($(this).prop('checked')){
            $('#max-attempts').prop("disabled", true).val('');
            $('#max-attempts-option-text').css('color', "#A9A9A9");

        }else{
            $('#max-attempts').prop("disabled", false);
            $('#max-attempts-option-text').css('color', "black");
        }
    });

    $('.question-link').click(function(){
            getProblem($(this));
            return false;
        });
    $('#btn-submit-grade').click(function(){

        if ( window.location !== window.parent.location ) {
            console.log("In iframe");
        } else {
            console.log('Not in iframe');
        }
        $('#modal-warn-submit-grade').modal('show');

    });
    $('#btn-finish-assessment').click(function(){
        console.log("Submit Grade");
        $.ajax({
            url:'submit_grade',
            type:'POST',
            success: function(response){
                $('.quest-item').unbind();
                $('#btn-submit-grade').unbind();

                 document.location.href = response['return_url'];

            }
        }).done(function(){

        });
    });

    $('#help-bank').popover('hide');
    $('#help-bank').click(function(){
        return false;
    });
    $('#help-assessment').click(function(){
        return false;
    });
    $('#help-assessment').popover('hide');
    $('#btn-submit-disabled-div').tooltip('hide');
    /* instructor view*/
    $('#btn-new-assess').tooltip('hide');
    $('#btn-del-assess').tooltip('hide');
    $('#btn-show-offering-option').tooltip('hide');
    $('#btn-reorder-items').tooltip('hide');
//
    $('#help').on('show.bs.popover', function () {
        console.log("show");
});


    $(".panel-title").click(function () {

        var id = $(this).attr('id');
        console.log(id);
        var types = {items_type1: "#collapseOne", items_type2: "#collapseTwo", items_type3: "#collapseThree", items_type4: "#collapseFour"};
        var spanElement = $(this).find('span');
        console.log(spanElement);

        if ($(types[id]).is(':hidden')) {
            console.log("Collapse one is hidden");
            $(types[id]).collapse('show');

            $(spanElement).removeClass("glyphicon-collapse-down");
            $(spanElement).addClass("glyphicon-collapse-up");


        } else {
            console.log("Collapse one is visible");
            $(types[id]).collapse('hide');
            $(spanElement).removeClass("glyphicon-collapse-up");
            $(spanElement).addClass("glyphicon-collapse-down");
        }
        return false;
    });


    /**
     * This is button in "modal-reorder-items"
     */
    $('#btn-submit-new-order').click(function () {
        /*Want to check if there are any items in the assessment*/

        var sub_id = selectedAssessment.attr('id');
        var idsArray = $('#reorder-items').sortable("toArray");
        console.log(idsArray);

        if(idsArray.length>1) {
            $.ajax({
                url: 'reorder_items',
                type: 'POST',
                data: {sub_id: sub_id, 'items': idsArray},
                success: function (response) {
//                    console.log(response);
                }
            }).done(function () {
                changeAssessmentName(sub_id);

            });
        }else{
            changeAssessmentName(sub_id);
        }
    });
    function changeAssessmentName(sub_id) {
        var oldName = selectedAssessment.text();
        var newName;
        var finalName = selectedAssessment.text();
        if ($('#assess-name-reorder').has('input').length) {
            newName = document.getElementById("inpt-change-assess-name").value;
        } else {
            newName = $(document.getElementById('assess-name-reorder')).attr('value');
        }
        if (newName != null) {
            newName = newName.trim();
            if (newName.length > 0) {
                finalName = newName;
            }
        }
        if (finalName != oldName) {
            $(selectedAssessment).find('div').text(finalName);
            $.ajax({
                url: 'rename_assessment',
                type: 'POST',
                data: {sub_id: sub_id, 'name': newName},
                success: function (response) {
                    console.log(response);
                }

            }).done(function(){
                requestItems(selectedAssessment);
            });
        }else{
            requestItems(selectedAssessment);

        }
        $('#assess-name-reorder').html('');

    }

    /* Handle the selection of the assessment */
    $('.assess-item').click(function () {
        console.log("before wait");
        if (wait == false) {
            clickAssessment($(this));
        }
        return false;
    });

    /* Delete an assessment */
    $('#btn-del-assess').click(function () {
        if (selectedAssessment != null && wait==false) {
            var sub_id = selectedAssessment.attr('id');
            unselectSelectedAssessment();

            $.ajax({
                url: 'del_assess',
                type: 'GET',
                data: {'sub_id': sub_id},
                success: function (response) {
                    response= JSON.parse(response);
                    console.log('success' in response);
                    if(response['success']) {
                          $("#modal-delete-assess-report .modal-body").html("Assessment successfully deleted!");
                        $("#modal-delete-assess-report").modal('show');
                    }else{
                         $("#modal-delete-assess-report .modal-body").html("This assessment has AssessmentTakens" +
                            " and cannot be deleted.");
                        $("#modal-delete-assess-report").modal('show');
                    }

                    updateAssessmentList(0);//0 stands for no page change

                }
            });
        }

    });
    $('.bank-item').click(function () {
        clickBankItem($(this));
        return false;
    });
    /**
     * Click on bank item                           //change
     */

    /**
     * Plus button -> show modal, ask for name
     */


    $("#btn-new-assess").click(function () {
        unselectSelectedAssessment();
        $("#assess-name").val('');
        document.getElementById("assess-name").focus();
        $('#warning').html('');
        $('#modal-create-assessment').modal('show');

    });

    /**
     * "Create" button inside the modal
     */

    $('#btn-create').click(function () {
        createNewAssessment();


    });


    $('#assess-name').keyup(function (e) {
        var key = e.which;
        if (key == 13) {
            $('#btn-create').click();
        }
    });

     $("#btn-show-offering-option").click(function () {
         //check if any selected
         if (selectedAssessment != null) {
             $('#see-answer').attr('checked', true);
             $('#max-attempts').prop("disabled", true).val('');
             $('#max-attempts-option-text').css('color', "#A9A9A9");
             $('#modal-get-offering').modal('show');

         }
     });

    $("#btn-get-offering").click(function () {
        var sub_id = findSelectedAssessId();
        if (selectedAssessment != null) {
            var seeAnswer= $('#see-answer').prop('checked');
            console.log("See Answer: "+ seeAnswer);

            var maxAttempts=document.getElementById("max-attempts").value;
            console.log(maxAttempts);

            console.log(sub_id);
            if (sub_id != null) {
                $.ajax({
                    url: 'get_offering_id',
                    type: 'POST',
                    data: {'sub_id': sub_id, 'seeAnswer': seeAnswer,'maxAttempts':maxAttempts},
                    success: function (response) {
                        console.log(response);
                        if (response['data']) {
                            console.log(response['data']);
                            var str = "<b>offering_id=" + response['data'][0]+'</b>';
                            $('#display-offering-id').html(str);
                            str = "<b>bank_id=" + response['data'][1]+'</b>';
                            $('#display-bank-id').html(str);

                            $('#modal-get-offering').modal('hide');
                            $('#modal-offering-id').modal('show');

                        } else if (response['detail']) {
                            console.log(response);
                            $('#help-title').html("Create offering");
                            $('#detail-div').html(response['detail']);
                            $('#help-text').html("Drag items from the bank into selected assessment area.");
                            $('#modal-display-detail').modal('show');
                        }


                    }
                });
            }
        } else {
            $('#help-title').html("Create offering for selected assessment");
            $('#help-text').html("No assessment is selected.");
            $('#modal-display-detail').modal('show');
        }
    });

    /**
     * Adding item to assessment
     */
    $("#assess-box-droppable").droppable({

        accept: ":not(.ui-sortable-helper)",

        drop: function (event, ui) {
            console.log("trying to drop bank item into assessment");
            console.log(ui.draggable.find('a').text());

            /*if this item is not in the list*/
            if (!isInAssessItems(ui.draggable.find('a').text())) {
                var question_id = ui.draggable.find('a').attr('value');

                console.log("Dropping element into the assessment box: ");
                console.log(question_id);

                var sub_id = findSelectedAssessId();
                if (sub_id != null && typeof question_id != 'undefined') {

                    console.log("question_id is defined ");
                    console.log("sending request to add item");
                    startWaiting();
                    $.ajax({
                        url: 'add_item',
                        type: "POST",
                        data: {'question_id': question_id, 'sub_id': sub_id},
                        success: function (response) {
                            console.log("success adding item to assessment");

                            requestItems(selectedAssessment);
                        }
                    }).done(function(){
                        stopWaiting();
                        console.log("Exiting add item to assessment.");
                    });

                } else {
                    console.log("Error:    sub_id or question_id is not found");
                }
            } else {
                console.log("This item is already in the assessment");
            }
        }
    });

    /**
     * Need to check if the item dropped is an item-in-assess
     */
    $("#bank-box-droppable").droppable({

        accept: function (dropElement) {
            return dropElement.hasClass('item-in-assess');
        },

        drop: function (event, ui) {

            console.log("Trying to drop an item into bank-box-droppable");

            if (ui.draggable.hasClass('bank-item')) {  /*do nothing*/
                console.log("this item belongs to the bank");
            } else {
                var question_id = ui.draggable.find('a').attr('value');
                var sub_id = findSelectedAssessId();

                if (sub_id != null && typeof question_id != 'undefined') {
                    startWaiting();
                    $.ajax({
                        url: 'remove_item',
                        type: "POST",
                        data: {'question_id': question_id, 'sub_id': sub_id},
                        success: function (response) {

                            console.log("success removing item");
                            requestItems(selectedAssessment);
                        }
                    }).done(function(){
                        stopWaiting();
                        console.log("Exiting remove item from assessment");
                    });
                } else {
                    console.log('Error:    sub_id or question_id is not found');
                }
            }
        }
    });


});//Closing Document.ready

/*
 Check if this item is already in the assessment
 This function is used by assess-box-droppable
 */


function isInAssessItems(name) {

//    var result = false;
    var itemsDiv = document.getElementById('assess-items');

    console.log("Iterating through assessment items ");
//    console.log(itemsDiv);

    if (itemsDiv != null) {
        var items = itemsDiv.childNodes;
//        console.log("Printing child nodes ");
//        console.log(items);
        for (var i = 0; i < items.length; i++) {
//            console.log(hasclass(items[i], 'item-in-assess'));
            if (hasclass(items[i], 'item-in-assess')) {
                console.log(items[i].childNodes[0].innerText);
                console.log(name);
                if(typeof items[i].childNodes[0].innerText == 'undefined'){//for Mozilla
                    if (name === items[i].childNodes[0].textContent) {
                        console.log("found a match");
                        return true;
                    }
                }else {
                    if (name === items[i].childNodes[0].innerText) {
                        console.log("found a match");
                        return true;
                    }
                }
            }
        }

    }
    return false;
}


/*
 Find an assessment that is selected
 Returns sub_id
 if none returns null                                    done
 */

function findSelectedAssessId() {

    if (selectedAssessment!=null){
        return $(selectedAssessment).attr("id");
    }
    return null;
}


function findAssessmentWithName(name) {
    var children= $('#assess-list').children();
    console.log(children);
    var obj = null;
    var i;
    for (i = 0; i < children.length; i++) {
        console.log("Print text");
        console.log($(children[i]).find('div').html().trim());
        if ($(children[i]).find('div').html().trim().indexOf(name)>-1) {
            console.log("This assessment has name "+ name );
            obj=children[i];
        }
    }
    console.log(obj);
    console.log('Exiting findAssessmentWithName');
    return obj;


}

function hasclass(element, cls) {
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}
function clickBankItem(obj) {
    console.log("clicked on bank item");
    var id = $(obj).find('a').attr('value');
    if ($(obj).hasClass('selected-bank-item')) {

        console.log("unselecting bank item");

        $(obj).removeClass('selected-bank-item');
        var i = selectedBankItems.indexOf(id);
        if (i != -1) {
            selectedBankItems.splice(i, 1);
        }
    } else {
        console.log("selecting new bank item");
        $(obj).addClass('selected-bank-item');
        selectedBankItems.push(id);
    }
}
function unselectAllBankItems() {
    $(".bank-item").each(function (i, obj) {
        if ($(obj).hasClass('selected-bank-item')) {
            $(obj).removeClass('selected-bank-item');
        }
        selectedBankItems = [];

    });
}
/*
 Handle a click on an assessment
 Selecting an element:
 add class selected
 update items of the assessment
 make the bank items draggable                  done
 */
function clickAssessment(obj) {
    console.log("clicked again");

    if (obj!=null) {
        /*if this assess already selected*/
        if ($(obj).hasClass('selected')) {
            unselectSelectedAssessment();

        }else {
            if (isAnySelected()) {
                unselectSelectedAssessment();
            }
            selectAssessment(obj);//adds class and appends the #select-badge
            requestItems(obj);
            unselectAllBankItems();

        }
    }
    console.log("Exiting clickAssessment")
}


/*
 Get Items of an assessment. Called each time an assessment is selected
 obj value contains the sub_id of the assessment


 */
function requestItems(obj) {
    console.log("Request Items");
    var sub_id = $(obj).attr('id');

    startWaiting();

    $.ajax({
        url: 'get_items',
        type: 'GET',
        data: {'sub_id': sub_id},
        success: function (response) {
            if ('detail' in response) {
                console.log(response['detail']);
                console.log('The assessment was not found');

            }else {
                var str = "";
                $('#assess-items').html('');
                $('#assess-items-name').html(getName(obj));

                if (response.length > 0) { //if there are items in assessment
                    $.each(response, function (key, value) {

                        str += buildListItem(value['displayName']['text'], value['id']);
                        console.log(value['id']);
                    });
                    $('#assess-items').html(str);

                    $('.item-in-assess').click(function () {
                        return false;
                    });

                    $('.item-in-assess').draggable();
                    $('.item-in-assess').draggable("option", "revert", 'invalid');
                    $('.item-in-assess').draggable("option", "helper", "clone");
                    $('.item-in-assess').on("dragstart", function (event, ui) {
                        ui.helper.addClass("mylist-item-div-clone").width(document.getElementById("assess-box-droppable").offsetWidth).css('z-index',200);

                    });
                } else {

                }
                $('#assess-items').addClass('mylist');
                $("#assess-items").append('<div class="mylist-item-div"><a href="#" class="assess-item-placeholder">-Drop items here-</a></div>');

                if ($("#assess-box-droppable").is(":hidden")) {
                    $('#assess-box-droppable').slideDown("slow");//.delay(800);
                }
                $('.assess-item-placeholder').click(function () {
                    return false;
                });

            }


        },
        error: function (xhr) {
            //Do Something to handle error
        }
    }).done(function(){
        stopWaiting();
        console.log('Exiting RequestItems');
    });

}
function showModalReorderItems() {

    var sub_id = $(selectedAssessment).attr('id');
    console.log("sub_id " + sub_id);

    $.ajax({
        url: 'get_items',
        type: 'GET',
        data: {'sub_id': sub_id},
        success: function (response) {
            if ('detail' in response) {
            }else{ //if successful response is a list of items
                var str = "";
                if (response.length > 0) { //if there are items in assessment
                    $.each(response, function (key, value) {

                        str += buildListItem(value['displayName']['text'], value['id']);
                        console.log(value['id']);
                    });
                }
                $('#assess-name-reorder').html(getName(selectedAssessment)+
                    ' <button class="btn btn-dark-background rename-btn"><span class="glyphicon glyphicon-edit">' +
                    '</span></button>').attr('value', getName(selectedAssessment));
                $('#reorder-items').addClass('mylist').html(str);
                $("#reorder-items").sortable();
                $("#assess-name-reorder").unbind().click(function () {
                    clickAssessmentName();
                });
                $("#modal-reorder-items").modal('show');
            }
        }
    });


}
function getName(obj) {
    return $(obj).find('div').text().trim();
}
function createNewAssessment() {
    var name = $("#assess-name").val();
    console.log("Name of the new assessment");
    console.log(name);

         /*  check if entered name is not empty*/

    if (name.length > 0) {
        startWaiting();
        $.ajax({
            url: "create_assessment",
            type: 'POST',
            data: {'selected': selectedBankItems, 'name': name},
            success: function (response) {
                /* want to select the newly created assessment*/
                /* find the object with the new assessment name*/

                $.when(updateAssessmentList(1)).done(function(){
                    clickAssessment(findAssessmentWithName(name));

                });
                unselectAllBankItems();
            }
        }).done(function(){
            stopWaiting();
            $('#modal-create-assessment').modal('hide')
        });

    } else {
        console.log("the name is empty");
        $("#warning").html("Assessment name cannot be empty.");
    }

}
/**
 * This function is called when in the reorder modal you click on the header
 * This allows you to change the name of the assessment
 * @param obj
 */
function clickAssessmentName() {
    var inputElement=document.getElementById("inpt-change-assess-name");

    /*
     if input is active
     want to save the input
     */

    if(inputElement!= null){
        console.log('Has input element');
        console.log(inputElement);
        var assessName = $('#assess-name-reorder').attr('value');
        var newName = inputElement.value;

        if (newName != null) {
            newName = newName.trim();
            if (newName.length > 0) {
                assessName = newName;
            }
        }
        $('#assess-name-reorder').html(assessName).attr('value', assessName);
        $('#assess-name-reorder').append('<button class="btn btn-dark-background rename-btn"><span class="glyphicon glyphicon-edit"></span></button>');


    } else {
        /*
         Want to add input element
         display old name as a placeholder
         */
        console.log($('#assess-name-reorder').attr('value'));
        $('#assess-name-reorder').html('<input type="text" id="inpt-change-assess-name">');
        inputElement = document.getElementById("inpt-change-assess-name");
        inputElement.setAttribute('placeholder', $('#assess-name-reorder').attr('value'));
        inputElement.focus();
        $('#inpt-change-assess-name').click(function () {

            return false;
        });
        $('#assess-name-reorder').append('<button class="btn btn-dark-background rename-btn"><span class="glyphicon glyphicon-edit"></span></button>');

    }


}

function removeHeader(idName) {
    var header = document.getElementById(idName);
    if (header != null) {
       // header.remove();
        header.removeChild(header.children[0]);
    }
}

//May want to change value of a and store the id in item-in-assess
function buildListItem(value, id) {
    return  '<div class="mylist-item-div item-in-assess" id="' + id + '">' +
        '<a href="#" class="mylist-item" value="' + id + '">' + value + "</a></div>";


}
/*
 done
 */


function selectAssessment(obj) {

    selectedAssessment = obj;
    $(obj).addClass('selected').append('<span class="glyphicon glyphicon-chevron-right" id="select-badge" style="position:absolute; right:10px;top:25%;"></span>');

    /*  Enable dragging of bank items  */
    if ($('.bank-item').hasClass("ui-draggable")) {
        $('.bank-item').draggable('enable');
    } else {
        $('.bank-item').draggable();
    }

    $('.bank-item').draggable("option", "revert", 'invalid');
    $('.bank-item').draggable("option", "helper", "clone");
    $('.bank-item').on("dragstart", function (event, ui) {
        if (!$('.bank-item').hasClass("ui-draggable-disabled")) {
            ui.helper.addClass("mylist-item-div-clone");
            ui.helper.width($("#bank-items-name").width()).css('z-index', 200);
        }
    });
}
/*
 Check if any assessment is selected
 Return true if there is one selected
 */
function isAnySelected() {
    if (selectedAssessment == null) {
        console.log("isAnySelected returned false");
        return false;
    }
    return true;


}

/*
 Unselect given assessment                  done

 */
function unselectSelectedAssessment() {
    if (selectedAssessment != null) {
        $(selectedAssessment).removeClass('selected');
        $(selectedAssessment).children('#select-badge').remove();
        selectedAssessment = null;
        $('.bank-item').draggable('disable');
    }
    hideAssessItems();

}

function hideAssessItems() {
    if (!$("#assess-box-droppable").is(":hidden")) {
        $('#assess-box-droppable').hide();


    }
//    stopWaiting();
}

function startWaiting(){
    console.log("Start waiting");
    wait = true;
    $("body").css("cursor", "progress");
    $(".assess-item").addClass("progress-cursor");
    $(".mylist-item").addClass("progress-cursor");
    $("#bank-box-droppable").addClass("progress-cursor");
}

function stopWaiting() {
    console.log("Stop waiting");
    wait = false;
    $("body").css("cursor", "default");
    $(".assess-item").removeClass("progress-cursor");
    $(".mylist-item").removeClass("progress-cursor");
    $("#bank-box-droppable").removeClass("progress-cursor");
}

/**
 * Request new assessment list for the given page number
 * Response has attributes: 'assessments', 'pages', 'page_num'
 * @param page_num
 */
function updateAssessmentList(page_num) {
    var text = "";
//    startWaiting();
    console.log(page_num);
    $.ajax({
        url: 'update_assess',
        type: 'GET',
        data: {'page_num' : page_num},
        async: false,
        success: function (response) {
            console.log(response);
            var assessments = response['assessments'];
            var pages=response['pages'];
            var page_num=response['page_num'];

            $.each(assessments, function (key, value) {
                console.log(value['displayName']['text']);
                text += '<a href="#" class="mylist-item assess-item" id="' + value['id'] + '"><div class="mylist-item-text">' + value['displayName']['text'] + '</div></a>';

            });
            $('#assess-list').html(text);
            selectedAssessment = null;
            $('.assess-item').click(function () {
                if (wait == false) {
                    clickAssessment($(this));
                }
                return false;
            });
            addAssessPageMenu(pages,page_num);


        }
    }).done(function(){

        console.log("Done updating assess list");
//        stopWaiting();

    });
    console.log('Exiting updateAssessmentList');


}

/**
 * In student view
 * displays the problem
 * @param obj is the quest-item clicked on
 */
function getProblem(obj) {
    console.log($(obj).attr('id'));
    $.ajax({
        url: 'get_question',
        type: 'POST',
        data: {data: [  $(obj).attr('id')]},//send the file.manip
        success: function (data) {
            console.log(data);
            if (data['redirect']) {
                window.location = data['redirectURL'];
            }
        }
    });
}
function printResponse(response){
                var reportDiv = document.getElementById("report-answer");
                var answer='';

                console.log("See answer "+ response['see_answer']);
                if('detail' in response){
                    answer="Could not submit answer!"
                }else if(response['see_answer']==true) {

                    if (response['correct'] === true) {
                        answer = '<span class="glyphicon glyphicon-ok badge-answer" style="" ></span>' + " Correct!";
                        reportDiv.style.color = "green";
                    } else {
                        answer = '<span class="glyphicon glyphicon-remove badge-answer" style=""></span>' + "Incorrect!";
                        reportDiv.style.color = "red";
                    }
                }else{

                    answer="Saved!";
                }
                reportDiv.innerHTML = answer;
            }

function addAssessPageMenu(pages, page_num){
    console.log("adding page menu");
    var str='<ul class="assess-page-menu-ul">';
    str+='<li class="assess-page-li"><a href="#" class="assess-page assess-page-a" name="'+pages[0]+'">&laquo;</li>';


    for(var i=1; i<pages.length-1; i++){
        if(pages[i]==page_num){
            str+='<li class="assess-page-li"><a href="#" class="assess-page cur-assess-page-a" name="'+pages[i]+'">'+pages[i]+'</a></li>';
        }else{
            str+='<li class="assess-page-li"><a href="#" class="assess-page assess-page-a" name="'+pages[i]+'">'+pages[i]+'</a></li>';
        }
    }
    str+='<li class="assess-page-li"><a href="#" class="assess-page assess-page-a" name="'+pages[pages.length-1]+'">&raquo;</a></li>';

    str+="</ul>";

    $("#assess-page-menu").html(str);
    $(".cur-assess-page-a").click(function(){
        return false;
    });

    $(".assess-page-a").click(function() {
        var page_num = $(this).attr('name');
        if (wait == false) {
            unselectSelectedAssessment();
            unselectAllBankItems();
            updateAssessmentList(page_num);
        }
        return false;

    });

}




