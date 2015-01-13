/**
 * Created by anna on 8/4/14.
 */
var selectedAssessment = null;
var selectedBankItems = [];
var wait=false;

$(document).ready(function () {
//    if ( window.location !== window.parent.location ) {
//            console.log("In iframe");
//        } else {
//            console.log('Not in iframe');
//        }


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
//                console.log(response);
//                $("#assess-finished-msg").html('Thank you for taking the assessment!');
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




//    $('.instruction').click(function(){
//        console.log("clicked on instruction");
//    });
//    $('.instruction').trigger("click");
//    $('#UnityPlayer').click();

//    $('#unityPlayer').focus();
//    $('#unityPlayer').focus(function(){
//        console.log("focused");
//        $(this).css('border',"1px solid red");
//    });

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
                    console.log(response);
                    //requestItems(selectedAssessment);
                }

            }).done(function () {
                changeAssessmentName(sub_id);

            });
        }else{
            changeAssessmentName(sub_id);
        }
    });
        function changeAssessmentName(sub_id){
            var oldName = selectedAssessment.text();
            var newName;
            var finalName = selectedAssessment.text();
            if ($('#assess-name-reorder').has('input').length) {
                //var inputElement = document.getElementById("change-assess-name");
                //console.log(inputElement.value);
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
                        // requestItems(selectedAssessment);
                    },
                    statusCode: {
                        200: function () {
                            selectAssessment(selectedAssessment);
                            requestItems(selectedAssessment);

                        }
                    }
                });
            }
            $('#assess-name-reorder').html('');

        }

    $('#btn-home').click(function () {

    });

    /* Handle the selection of the assessment */
    $('.assess-item').click(function () {
        console.log("before wait");
        if(wait==false){
//            wait=true;
//            console.log('waiting');
            clickAssessment($(this));
        }
        return false;
    });

    /* Delete an assessment */
    $('#btn-del-assess').click(function () {
        if (selectedAssessment != null) {
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

                    updateAssessmentList();

                },
                error: function (response) {
                    console.log(response);
                },
                statusCode: {
                    200: function () {


                    },
                    406: function () {

//
                    },
                    500: function () {


                    }

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
        $('#assess-name').focus();
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
         var sub_id = findSelectedAssessId();

         //check if any selected
         if (selectedAssessment != null) {
             $('#see-answer').attr('checked', true);
             $('#modal-get-offering').modal('show');

         }
     });

    $("#btn-get-offering").click(function () {
        var sub_id = findSelectedAssessId();

        //check if any selected
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


                    },
                    statusCodes: {
                        200: function () {
                        },
                        500: function (response) {
                            console.log(response);

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
    function selectText(element) {
        var doc = document;
        var text = doc.getElementById(element);

        if (doc.body.createTextRange) { // ms
            var range = doc.body.createTextRange();
            range.moveToElementText(text);
            range.select();
        } else if (window.getSelection) { // moz, opera, webkit
            var selection = window.getSelection();
            var range = doc.createRange();
            range.selectNodeContents(text);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    $('#btn-copy-offering').click(function () {
        var copied = $(this).attr('value');
        console.log(copied);
        // window.clipboardData.setData("Text", copied);
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
//    var el = document.getElementById('assess-list');
//    var children = el.childNodes;
    var sub_id = null;
//
//    var i;
//    for (i = 0; i < children.length; i++) {
//        console.log(children[i].classList);
//
//        if (hasclass(children[i], 'selected')) {
//            console.log("has class selected");
//
//            sub_id = children[i].getAttribute('id');
//        }
//    }
    if (selectedAssessment!=null){
        sub_id=$(selectedAssessment).attr("id");
    }
    return sub_id;

    /**
     * or could just check if selectedAssessment is null or not
     */
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
        console.log("unselecting bank item");
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


    /*if this assess already selected*/
    if ($(obj).hasClass('selected')) {
        console.log("this object is already selected");
        unselectSelectedAssessment();
        //now no assessment is selected
        $('.bank-item').draggable('disable');
    } else {
        /*if not yet selected*/
        if (isAnySelected()) {
            console.log("Need to unselect one first");
            unselectSelectedAssessment();
            $('.bank-item').draggable('disable');
        }

        selectAssessment(obj);//adds class and appends the #select-badge
        requestItems(obj);
        unselectAllBankItems();


        //Do we want to disable dragging when assessment not selected?
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
                ui.helper.width($("#bank-items-name").width()).css('z-index',200);

            }

        });
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
                    $('#assess-items').addClass('mylist').html(str);

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
                console.log(response);

                /* want to select the newly created assessment*/
                /* find the object with the new assessment name*/

                $.when(updateAssessmentList()).done(function(){
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
        //$("#modal-create-assessment").modal('show');
    }

}
/**
 * This function is called when in the reorder modal you click on the header
 * This allows you to change the name of the assessment
 * @param obj
 */
function clickAssessmentName() {
//    console.log($(obj));
    var inputElement=document.getElementById("inpt-change-assess-name");

    /*
     if input is active
     want to save the input
     */

//    if ($('#assess-name-reorder').has('input').length) { // has returns a list of objects
    if(inputElement!= null){
        console.log('Has input element');
//        inputElement = document.getElementById("inpt-change-assess-name");
        console.log(inputElement);
        var assessName = $('#assess-name-reorder').attr('value');
        var newName = inputElement.value;

        if (newName != null) {
            newName = newName.trim();
            if (newName.length > 0) {
                assessName = newName;
            }
        }
//        $('#assess-name-reorder').html('');
        $('#assess-name-reorder').html(assessName).attr('value', assessName);
            $('#assess-name-reorder').append('<button class="btn btn-dark-background rename-btn"><span class="glyphicon glyphicon-edit"></span></button>');


    } else {
        /*
         Want to add input element
         display old name as a placeholder
         */

//        $('#assess-name-reorder').html('');
        console.log($('#assess-name-reorder').attr('value'));
        $('#assess-name-reorder').html('<input type="text" id="inpt-change-assess-name">');
        inputElement = document.getElementById("inpt-change-assess-name");
        inputElement.setAttribute('placeholder', $('#assess-name-reorder').attr('value'));
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


function updateAssessmentList() {
    var text = "";
    $.ajax({
        url: 'update_assess',
        type: 'GET',
        async: false,
        success: function (response) {
            console.log(response);
            var data = response;
            $.each(response, function (key, value) {
                console.log(value['displayName']['text']);
                text += '<a href="#" class="mylist-item assess-item" id="' + value['id'] + '"><div class="mylist-item-text">' + value['displayName']['text'] + '</div></a>';

            });
            console.log(text);
            console.log("printing the assessment list");
            $('#assess-list').html(text);
            selectedAssessment = null;
            $('.assess-item').click(function () {
                console.log("before wait");
                if(wait==false){
                    wait=true;
                    console.log('waiting');
                    clickAssessment($(this));
                }
//                clickAssessment($(this));
                return false;
            });

        }
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




