function change_tab(formsets)
{
    $('.inline-tab').removeClass('current-tab');
    $('.inline-group').not('.main-bloc').css('display', 'none');
    
    formsets = formsets.split(",");
    for (formset in formsets)
    {     
        $('#'+formsets[formset]+'-group').css('display', 'block');
        $('#'+formsets[formset]+'-tab').addClass('current-tab');
    }
}

$('.auto_select').each(function() {
    var languages = "";
    $('#'+$(this).attr('id').replace('auto', 'id')+' option:selected').each(function() {
        languages += $(this).html()+" / ";
    });
    $(this).val(languages.substring(0, languages.length- 3));
});