$(function() {
    $('#btnCompare').click(function() {

        var form_data = new FormData($('#uploadform')[0]);

        $.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,
            processData: false,
            dataType: 'json'
        }).done(function(data, textStatus, jqXHR){
            console.log(textStatus);
            console.log(jqXHR);
            console.log('Success!');
            //display comparison results in #showComparisonResults div
            $('#showComparisonResults').load('/showComparisonResults');
        }).fail(function(data){
            //alert when no files, only 1 file and unsupported
            alert('Please select 2(csv) files!');
        });
    });
    //display unmatched results in #showUnmatchedResults div
    $("#btnUnmatched").click(function(){
        $("#showUnmatchedResults").load("showUnmatchedReports");
    });
});
