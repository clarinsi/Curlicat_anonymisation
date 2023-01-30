$('#anonButton').on('click', function(event) {
    let text = $('#mainText').val();
    document.getElementById('anonButtonSpin').style.visibility = 'visible';

    var lang = $('#langs').val();
    console.log(lang);
    
    $.ajax({
        url: '/anonymize',
        type: 'POST',
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({text: text, lang: lang}),
        success: function (response) {
            document.getElementById('anonButtonSpin').style.visibility = 'hidden';
            $('#mainOut').html(response['anonymized_text']);
        },
        error: function (jqXHR, textStatus, errorThrown) { 
            document.getElementById('anonButtonSpin').style.visibility = 'hidden';
            $('#mainOut').html(textStatus);
        }
    });
});
