/**
 * Created by anna on 8/4/14.
 */
var selectedAssessment = null;
var selectedBankItems=[];
$(document).ready(function () {


    /* Handle the selection of the assessment */
    $('.assess-item').click(function () {
        clickAssessment($(this));
    });


    /* Delete an assessment */

    $('#btn-del-assess').click(function () {
        var sub_id = findSelectedAssess();
        //check if any selected
        $.ajax({
            url: 'del_assess',
            type: 'GET',
            data: {'sub_id': sub_id},
            success: function (response) {
                console.log(response);
                unselectThisAssessment($(this));
                updateAssessmentList();


            }
        });
       // $('#assess-items').empty().removeClass('mylist');

    });
    $('.bank-item').click(function(){
        clickBankItem($(this));
    });
     /**
     * Click on bank item                           //change
     */


    $('#create').click(function() {

        var name= $("#assess-name").val();
        console.log("Name of the new assessment");

        console.log(name);

        if(selectedBankItems.length>0){
            $.ajax({
                url:"create_assessment",
                type:'POST',
                data:{'selected': selectedBankItems, 'name': name},
                success: function(response){
                    console.log(response);
                    updateAssessmentList();
                }
            });

        }else{
            console.log('No bank items are selected');
        }

    });

    $("#btn-new-assess").click(function () {
        $('#modal-create-assessment').modal('show');

        //if selectedBankItems list is not empty



    });
    $("#btn-get-offering").click(function () {
        var sub_id = findSelectedAssess();

        //check if any selected
        if(sub_id!=null) {
            $.ajax({
                url: 'get_offering_id',
                type: 'POST',
                data: {'sub_id': sub_id},
                success: function (response) {
                    console.log(response);
                    $('#display_offering_id').html(response);
                    $('#modal-offering-id').modal('show');
                }
            });
        }

    });

    /**
     * Adding item to assessment
     */
    $("#assess-box-droppable").droppable({


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
                            //
                            // console.log(response);
                            console.log("now we can append it to the #assess-items list");
                            $('#assess-items').append(buildListItem(ui.draggable.find('a').text(), ui.draggable.find('a').attr('value')));


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
                            for (var prop in response) {
                                console.log(prop);
                            }

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
 This function is used by assess-box-groppable
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

            console.log(items[i].childNodes[0].innerText);
            console.log(name);
            if (name === items[i].childNodes[0].innerText) {
                console.log("found a match");
                result = true;
            }
        }

    }
//    $('.item-in-assess').each(function () {
//        console.log($(this).text());
//        console.log(name);
//        //name=name.trim();
//        if (name === $(this).text()) {
//            result = true;
//        }
//    });
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
            sub_id = children[i].getAttribute('value');
        }
    }
    return sub_id;
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

        unselectThisAssessment($(obj));
        //now no assessment is selected

        $('.bank-item').draggable('disable');


    } else { //if not yet selected
        if (isAnySelected()) {
            console.log("Need to unselect one first");
            unselectThisAssessment(selectedAssessment);
            $('.bank-item').draggable('disable');
        }

        selectAssessment(obj);//adds class and appends the #select-badge
        requestItems(obj);


        //Do we want to disable dragging when assessment not selected
        if ($('.bank-item').hasClass("ui-draggable")) {
            $('.bank-item').draggable('enable');
        } else {
            $('.bank-item').draggable();
        }

        $('.bank-item').draggable("option", "revert", 'invalid');
        $('.bank-item').draggable("option", "helper", "clone");
        $('.bank-item').on("dragstart", function (event, ui) {
            ui.helper.addClass("mylist-item-div-clone");

        });
    }
}


/*
 Get Items of an assessment. Called each time an assessment is selected
 obj value contains the sub_id of the assessment


 */
function requestItems(obj) {
    var sub_id = $(obj).attr('value');
    $.ajax({
        url: 'get_items',
        type: 'GET',
        data: {'sub_id': sub_id},
        success: function (response) {
            if ('data' in response) {
                console.log('was found');
                var str = "";
                console.log(response['data'].length);
                if (response['data'].length > 0) { //if there are items in assessment
                    $.each(response['data'], function (key, value) {

                        str += buildListItem(value['displayName']['text'], value['id']);
                        console.log(value['id']);
                    });
                    removeHeader();
                    $('#assess-box-droppable').prepend('<p class="mylist-head" id="assess-items-name">'+$(obj).text()+'</p>');
                    $('#assess-items').addClass('mylist').html(str);

                    $('.item-in-assess').draggable();
                    $('.item-in-assess').draggable("option", "revert", 'invalid');
                    $('.item-in-assess').draggable("option", "helper", "clone");
                    $('.item-in-assess').on("dragstart", function (event, ui) {
                        ui.helper.addClass("mylist-item-div-clone");


                    });


                    $('#assess-items').sortable();
                }
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
function removeHeader(){
    var header=document.getElementById('assess-items-name');
                    if(header!=null) {
                        header.remove();
                    }
}

function buildListItem(value, id) {
    return  '<div class="mylist-item-div item-in-assess">' +
        '<a href="#" class="mylist-item" value="' + id + '">' + value + "</a></div>";


}
/*
 done
 */

function selectAssessment(obj) {
     selectedAssessment = obj;
    $(obj).addClass('selected').append('<span class="glyphicon glyphicon-chevron-right" id="select-badge" style="float:right"></span>');

}
/*
 Check if any assessment is selected
 Return true if there is one selected                  change
 */
function isAnySelected() {
    var selected = false;


//    $('.assess-item').each(function () {
//        if ($(this).hasClass('selected')) {
//            selected = true;
//        }
//    });
//    return selected;


    if(selectedAssessment==null){
        console.log("isAnySelected returned false");
        return false;
    }
    return true;



}
/*
 Find and Unselect a selected assessment               change


 */
//function unselectAnAssessment() {
////    $('.assess-item').each(function () {
////        if ($(this).hasClass('selected')) {
////            unselectThisAssessment($(this));
////        }
////    });
//    //new version
//    unselectThisAssessment(selectedAssessment);
//}

/*
 Unselect given assessment                  done

 */
function unselectThisAssessment(obj) {
    selectedAssessment = null;
    $(obj).removeClass('selected');
    console.log("Remove the select-badge");
    $(obj).children('#select-badge').remove();
    //document.getElementById('select-badge').remove();
    removeAssessItems();

}

function removeAssessItems(){
    console.log("removing the header");
    removeHeader();
    var itemsDiv = document.getElementById("assess-items");
    if (itemsDiv != null) {
        itemsDiv.innerHTML = "";
        itemsDiv.className = "";





    } else {
        console.log("Trying to unselect a not selected assessment");
        console.log($(obj));
    }

}
function updateAssessmentList() {
    // $('#assess-list').empty();
    var text = "";
    $.ajax({
        url: 'update_assess',
        type: 'GET',
        success: function (response) {
            console.log(response);
            var data = response;
            $.each(response, function (key, value) {
                console.log(value['displayName']['text']);
                text += '<a href="#" class="mylist-item assess-item" value="' + value['id'] + '">' + value['displayName']['text'] + '</a>';

            });
            console.log(text);
            $('#assess-list').html(text);
            selectedAssessment=null;
            $('.assess-item').click(function () {
                clickAssessment($(this))
            });

        }
    });


}




