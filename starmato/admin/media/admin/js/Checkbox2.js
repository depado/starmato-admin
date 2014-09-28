function categorized_checkbox_multiple_change(input) {
    var checked = $(input).is(':checked');
    $(input).parents("li").next("ul").find("input").prop('checked', checked);
}