/**
 * Created by anna on 8/4/14.
 */
var selectedAssessment = null;
var selectedBankItems=[];

$(document).ready(function () {

    $(".panel-title").click(function(){

        var id=$(this).attr('id');
        console.log(id);
        var types={items_type1:"#collapseOne", items_type2: "#collapseTwo",items_type3:"#collapseThree", items_type4:"#collapseFour"};
        var spanElement=$(this).find('span');
           console.log(spanElement);

       if($(types[id]).is(':hidden')){
           console.log("Collapse one is hidden");
           $(types[id]).collapse('show');

           $(spanElement).removeClass("glyphicon-collapse-down");
           $(spanElement).addClass("glyphicon-collapse-up");


       }else{
           console.log("Collapse one is visible");
           $(types[id]).collapse('hide');
           $(spanElement).removeClass("glyphicon-collapse-up");
           $(spanElement).addClass("glyphicon-collapse-down");
       }
    });

    $('#btn-submit-new-order').click(function () {
        /*Want to check if there are any items in the assessment*/

        var sub_id=selectedAssessment.attr('id');
        var idsArray = $('#reorder-items').sortable("toArray");
        console.log(idsArray);



        $.ajax({
            url: 'reorder_items',
            type: 'POST',
            data: {sub_id: sub_id, 'items': idsArray},
            success: function (response) {
                console.log(response);
                //requestItems(selectedAssessment);
            }

        }).done(function () {
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
        });
    });

    $(".submit-answer").click(function () {
        u.getUnity().SendMessage("Question", "RequestRespone", "");
    });
    $('#btn-home').click(function(){

    });


    /* Handle the selection of the assessment */
    $('.assess-item').click(function () {
        clickAssessment($(this));
        return false;
    });

    /* Delete an assessment */

    $('#btn-del-assess').click(function () {
        if(selectedAssessment!=null) {
            var sub_id=selectedAssessment.attr('id');
            unselectThisAssessment();

            $.ajax({
                url: 'del_assess',
                type: 'GET',
                data: {'sub_id': sub_id},
                success: function (response) {
                    console.log(response);

                    updateAssessmentList();

                },
                error: function (response) {
                    console.log(response);
                },
                statusCode: {
                    200: function () {
                        $("#modal-delete-assess-report .modal-body").html("Assessment successfully deleted!");
                        $("#modal-delete-assess-report").modal('show');

                    },
                    406: function () {
                        $("#modal-delete-assess-report .modal-body").html("This assessment has AssessmentTakens" +
                            "and cannot be deleted.");
                        $("#modal-delete-assess-report").modal('show');
//
                    },
                    500: function () {

                    }

                }
            });
        }

    });
    $('.bank-item').click(function(){
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
          unselectThisAssessment();
//          if (selectedBankItems.length > 0) {
              $("#assess-name").val('');
               $('#assess-name').focus();
              $('#modal-create-assessment').modal('show');
//          }else{
//              //show modal : Please select bank items to make an assessment
//              $('#modal-select-bank-items').modal('show');
//          }

    });

    /**
     * "Create" button inside the modal
     *  check if entered name is not empty
     */

    $('#btn-create').click(function() {
        createNewAssessment();


    });


    $('#assess-name').keyup(function(e){
        var key = e.which;
        if(key==13) {
            $('#btn-create').click();
        }
    });


    $("#btn-get-offering").click(function () {
        var sub_id = findSelectedAssess();

        //check if any selected
        if(selectedAssessment!= null) {
            //check if assessment is empty or not
            console.log(sub_id);
            if (sub_id != null) {
                $.ajax({
                    url: 'get_offering_id',
                    type: 'POST',
                    data: {'sub_id': sub_id},
                    success: function (response) {
                        console.log(response[0]);

                        var str="offering_id="+ response[0];
                        $('#display-offering-id').html(str);
                        str="bank_id="+response[1];
                        $('#display-bank-id').html(str);



                        str="offering_id="+ response[0]+'/n'+"bank_id="+response[1];
                         $('#btn-copy-offering').attr('value',str).focus();

                        $('#modal-offering-id').modal('show');
                        selectText('display-bank-id');

                    },
                    statusCodes: {
                        200: function(){},
                        500: function (response) {
                            console.log(response);

                }
            }
                });
            }
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
    $('#btn-copy-offering').click(function(){
        var copied= $(this).attr('value');
        console.log(copied);
       // window.clipboardData.setData("Text", copied);
    });

    /**
     * Adding item to assessment
     */
    $("#assess-box-droppable").droppable({

        accept: ":not(.ui-sortable-helper)",

        drop: function (event, ui) {



            //if this item is not in the list
            console.log("trying to drop bank item into assessment");
            console.log(ui.draggable.find('a').text());

            if (!isInAssessItems(ui.draggable.find('a').text())) {
                var question_id = ui.draggable.find('a').attr('value');

                console.log("Dropping element into the assessment box: ");
                console.log(question_id);

                var sub_id = findSelectedAssess();
                if (sub_id != null && typeof question_id != 'undefined') {

                    console.log("question_id is defined ");
                    console.log("sending request to add item");

                    $.ajax({
                        url: 'add_item',
                        type: "POST",
                        data: {'question_id': question_id, 'sub_id': sub_id},
                        success: function (response) {
                            console.log("success adding item to assessment");

                            requestItems(selectedAssessment);
                        }
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

            if (ui.draggable.hasClass('bank-item')) {

                console.log("this item belongs to the bank");

            } else {

                var question_id = ui.draggable.find('a').attr('value');
                var sub_id = findSelectedAssess();
                if (sub_id != null && typeof question_id != 'undefined') {

                    console.log("sending request to remove item");

                    $.ajax({
                        url: 'remove_item',
                        type: "POST",
                        data: {'question_id': question_id, 'sub_id': sub_id},
                        success: function (response) {

                            console.log("success removing item");
                            requestItems(selectedAssessment);
                        }
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

    var result = false;
    var itemsDiv = document.getElementById('assess-items');

    console.log("Iterating through assessment items ");
    console.log(itemsDiv);

    if (itemsDiv != null) {
        var items = itemsDiv.childNodes;
        console.log("Printing child nodes ");
        console.log(items);
        for (var i = 0; i < items.length; i++) {
            console.log(hasclass(items[i],'item-in-assess'));
            if(hasclass(items[i],'item-in-assess')) {
                console.log(items[i].childNodes[0].innerText);
                console.log(name);
                if (name === items[i].childNodes[0].innerText) {
                    console.log("found a match");
                    result = true;
                }
            }
        }

    }
    return result;
}


/*
 Find an assessment that is selected
 Returns sub_id
 if none returns null                                    done
 */

function findSelectedAssess() {
    var el = document.getElementById('assess-list');
    var children = el.childNodes;
    var sub_id = null;

    var i;
    for (i = 0; i < children.length; i++) {
        console.log(children[i].classList);

        if (hasclass(children[i], 'selected')) {
            console.log("has class selected");

            sub_id = children[i].getAttribute('id');
        }
    }
    return sub_id;

    /**
     * or could just check if selectedAssessment is null or not
     */
}
function hasclass(element, cls) {
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}
function clickBankItem(obj){
         console.log("clicked on bank item");
         var id=$(obj).find('a').attr('value');
        if($(obj).hasClass('selected-bank-item')){

            console.log("unselecting bank item");

            $(obj).removeClass('selected-bank-item');
            var i=selectedBankItems.indexOf(id);
            if(i!=-1){

                selectedBankItems.splice(i,1);
            }

        }else{
            console.log("selecting new bank item");
            $(obj).addClass('selected-bank-item');

            selectedBankItems.push(id);
        }
    }
function unselectAllBankItems(){
    $(".bank-item").each(function(i,obj){
         console.log("unselecting bank item");
        if($(obj).hasClass('selected-bank-item')){

            $(obj).removeClass('selected-bank-item');


        }
         selectedBankItems=[];

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

    if ($(obj).hasClass('selected')) {  //if this assess already selected
        console.log("this object is already selected");

        unselectThisAssessment();
        //now no assessment is selected
        $('.bank-item').draggable('disable');


    } else { //if not yet selected
        if (isAnySelected()) {
            console.log("Need to unselect one first");
            unselectThisAssessment();
            $('.bank-item').draggable('disable');
        }

        selectAssessment(obj);//adds class and appends the #select-badge
        requestItems(obj);
        unselectAllBankItems();


        //Do we want to disable dragging when assessment not selected
        if ($('.bank-item').hasClass("ui-draggable")) {
            $('.bank-item').draggable('enable');
        } else {
            $('.bank-item').draggable();
        }

        $('.bank-item').draggable("option", "revert", 'invalid');
        $('.bank-item').draggable("option", "helper", "clone");
        $('.bank-item').on("dragstart", function (event, ui) {

            if(!$('.bank-item').hasClass("ui-draggable-disabled")){
//                if(ui.helper.hasClass("mylist-item-div-clone"))
                ui.helper.addClass("mylist-item-div-clone");
                ui.helper.width($("#bank-items-name").width());
                console.log($("#bank-items-name").width());

            }

        });
    }
}


/*
 Get Items of an assessment. Called each time an assessment is selected
 obj value contains the sub_id of the assessment


 */
function requestItems(obj) {
    console.log("Request Items");
    var sub_id = $(obj).attr('id');
    console.log("sub_id "+sub_id);
    console.log(obj);


    $.ajax({
        url: 'get_items',
        type: 'GET',
        data: {'sub_id': sub_id},
        success: function (response) {
            if ('data' in response) {
                //console.log('was found');
                var str = "";
                console.log("Number of items: "+ response['data'].length);


                removeHeader('assess-items-name');
                $('#assess-items').html('');
                    console.log($(obj).find('div').text().trim() );
                    $('#assess-box-droppable').prepend('<div class="mylist-header " id="assess-items-name">' +
                        '<div class="mylist-item-text">'+getName(obj) +"</div>"+
                        '<button class="manage-assess-btn btn" id="btn-reorder-items" onclick="showModalReorderItems()">' +
                        '<span class="glyphicon glyphicon-sort" ></span></button></div>');


                if (response['data'].length > 0) { //if there are items in assessment
                    $.each(response['data'], function (key, value) {

                        str += buildListItem(value['displayName']['text'], value['id']);
                        console.log(value['id']);
                    });

                    $('#assess-items').addClass('mylist').html(str);


                    $('.item-in-assess').click(function(){
                        return false;
                    });


                    $('.item-in-assess').draggable();
                    $('.item-in-assess').draggable("option", "revert", 'invalid');
                    $('.item-in-assess').draggable("option", "helper", "clone");
                    $('.item-in-assess').on("dragstart", function (event, ui) {
                        ui.helper.addClass("mylist-item-div-clone").width(document.getElementById("assess-items-name").offsetWidth);

                    });
//                    $('#assess-items').sortable();
                }else{

                }
                $("#assess-items").append('<div class="mylist-item-div"><a href="#" class="assess-item-placeholder">-Drop items here-</a></div>');

                if ($("#assess-box-droppable").is(":hidden")) {
                        $('#assess-box-droppable').slideDown("slow").delay(800);
                }
                $('.assess-item-placeholder').click(function(){
                    return false;
                });

            } else {
                if ('detail' in response) {
                    console.log(response['detail']);
                    console.log('The assessment was not found');
                }
                console.log('The assessment was not found');
            }
        },
        error: function (xhr) {
            //Do Something to handle error
        }
    });

}
function showModalReorderItems(){
   // var obj=selectedAssessment;

    var sub_id = $(selectedAssessment).attr('id');
    console.log("sub_id "+sub_id);

    $.ajax({
        url: 'get_items',
        type: 'GET',
        data: {'sub_id': sub_id},
        success: function (response) {
            if ('data' in response) {
                var str = "";
                removeHeader('assess-name-reorder');
                if (response['data'].length > 0) { //if there are items in assessment
                    $.each(response['data'], function (key, value) {

                        str += buildListItem(value['displayName']['text'], value['id']);
                        console.log(value['id']);
                    });
                   // console.log();
                    $('#reorder-items-div').prepend('<p class="mylist-header" id="assess-name-reorder" value="'+getName(selectedAssessment)+'">' +
                        getName(selectedAssessment)+'<span class="glyphicon glyphicon-edit" style="float:right;"></span>' + '</p>');
                    $('#reorder-items').addClass('mylist').html(str);
                    $("#reorder-items").sortable();
                    $("#assess-name-reorder").click(function(){
                        clickAssessmentName($(this));
                    });


                }
                $("#modal-reorder-items").modal('show');
            }
        }
    });


}
function getName(obj){
    return $(obj).find('div').text().trim();
}
function createNewAssessment(){
         var name= $("#assess-name").val();
        console.log("Name of the new assessment");
        console.log(name);


        if(name.length>0) {
          //  if (selectedBankItems.length > 0) {
                $.ajax({
                    url: "create_assessment",
                    type: 'POST',
                    data: {'selected': selectedBankItems, 'name': name},
                    success: function (response) {
                        console.log(response);
                        updateAssessmentList();
                        unselectAllBankItems();
                    }
                });

//            } else {
//                console.log('No bank items are selected');
//            }
        }else{
            console.log("the name is empty");
            //$("#modal-create-assessment").modal('show');
        }

    }

function clickAssessmentName(obj){
    console.log($(obj));
    var inputElement;

    /*
    if input is active
        want to save the input
     */
    if($(obj).has('input').length) {
        inputElement=document.getElementById("inpt-change-assess-name");
        console.log(inputElement.value);
        var assessName=$(obj).attr('value');
        var newName=inputElement.value;

        if(newName!=null){
            newName=newName.trim();
            if(newName.length>0){
                assessName=newName;
            }
        }
        $(obj).html('');
        $(obj).append(assessName).attr('value', assessName);

    }else{
        /*
        Want to add input element
            display old name as a placeholder
         */

        $(obj).html('');
        console.log($(obj).attr('value'));
        $(obj).append('<input type="text" id="inpt-change-assess-name">');
        inputElement=document.getElementById("inpt-change-assess-name");
        inputElement.setAttribute('placeholder',$(obj).attr('value'));
        $('#inpt-change-assess-name').click(function(){
            return false;
        });

    }
    $(obj).append('<span class="glyphicon glyphicon-edit" style="float:right;"></span>');


}

function removeHeader(idName){
    var header=document.getElementById(idName);
                    if(header!=null) {
                        header.remove();
                    }
}

//May want to change value of a and store the id in item-in-assess
function buildListItem(value, id) {
    return  '<div class="mylist-item-div item-in-assess" id="'+id+'">' +
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
    if(selectedAssessment==null){
        console.log("isAnySelected returned false");
        return false;
    }
    return true;



}

/*
 Unselect given assessment                  done

 */
function unselectThisAssessment(obj) {
    if(selectedAssessment!=null) {
        $(selectedAssessment).removeClass('selected');
        console.log("Remove the select-badge");
        $(selectedAssessment).children('#select-badge').remove();
        selectedAssessment = null;
    }
    removeAssessItems();

}

function removeAssessItems(){
    console.log("removing the header");
    if(!$("#assess-box-droppable").is(":hidden")){
        $('#assess-box-droppable').hide();

    }
 //  removeHeader('assess-items-name');
//    var itemsDiv = document.getElementById("assess-items");
//    if (itemsDiv != null) {
//        itemsDiv.innerHTML = "";
//        itemsDiv.className = "";
//    } else {
//        console.log("Trying to unselect a not selected assessment");
//        console.log($(obj));
//    }

}
function updateAssessmentList() {
    var text = "";
    $.ajax({
        url: 'update_assess',
        type: 'GET',
        success: function (response) {
            console.log(response);
            var data = response;
            $.each(response, function (key, value) {
                console.log(value['displayName']['text']);
                text += '<a href="#" class="mylist-item assess-item" id="' + value['id'] + '"><div class="mylist-item-text">' + value['displayName']['text'] + '</div></a>';

            });
            console.log(text);
            $('#assess-list').html(text);
            selectedAssessment=null;
            $('.assess-item').click(function () {
                clickAssessment($(this));
                return false;
            });

        }
    });


}

/**
 * In student view
 * displays the problem
 * @param obj is the quest-item clicked on
 */
function getProblem(obj){
    console.log($(obj).text());
            $.ajax({
                url:'get_question',
                type:'POST',
//                $(obj).attr('value')
                data:{data:[ $(obj).attr('name'), $(obj).text(), $(obj).attr('id')]},//send the file.manip
                success: function(data){
                    console.log(data);
                    //window.location.href = response.redirect;
                    if(data['redirect']) {
                         window.location = data['redirectURL'];
                     }
                }
            });
        }




