function edited(id) {
    $(".old").find("label[for="+id+"]").removeClass("needmerge refusedmerge acceptedmerge").addClass("edited");
}


function acceptMerge(id) {
    var $old = $(".old").find("#"+id);
    var $pend = $(".modified").find("#"+id);

    if ($pend.attr("type") == "checkbox") {
	$old.prop("checked", !$pend.prop("checked"));
    } else {
	$old.val($old.attr("data-copy"));
    }
    $(".old").find("label[for="+id+"]").removeClass("needmerge refusedmerge edited").addClass("acceptedmerge");
}

function refuseMerge(id) {
    var $old = $(".old").find("#"+id);
    var $pend = $(".modified").find("#"+id);

    if ($pend.attr("type") == "checkbox") {
	$old.prop("checked", $pend.prop("checked"));
    } else {
	$old.val($pend.val());
    }
    $(".old").find("label[for="+id+"]").removeClass("needmerge acceptedmerge edited").addClass("refusedmerge");
}

function addMergeButtons($label, id) {
    $label.removeClass("required").addClass("needmerge")
    $label.parent().append("<input type='button' class='mergebutton' value='OK' onClick='acceptMerge(\""+id+"\");'><input type='button' class='mergebutton' value='KO' onClick='refuseMerge(\""+id+"\");'>");
}

$(document).ready(function() {
    $(".old input, .old select, .old textarea").not("input[type=hidden]").each(function() {
	var $old = $(this);
	var id = $old.attr("id");
	var $pend = $(".modified").find("#"+id);
	$old.click(function() { edited(id); });
	if ($pend.find("option").length > 0) {
	    var modified = $pend.find("option").length != $old.find("option").length;
	    if (!modified) {
		$old.find("option").each(function() {
		    var $cmp = $pend.find("option[value='"+$(this).val()+"']");
		    if ($cmp.length == 0 || $cmp.attr("selected") != $(this).attr("selected")) {
			modified = true;
		    }
		});			
	    }
	    if (modified) {
		var $cpy = $old.children().clone();
		$old.find("option").each(function() {
		    if ($pend.find("option[value='"+$(this).val()+"']").length == 0)
			$pend.append($(this).removeAttr("selected"));
		});
		$old.empty().append($pend.find(":not(option:selected)")).append($pend.children());
		$pend.empty().append($cpy);
		$label = $(".old").find("label[for="+id+"]");
		addMergeButtons($label, id);
	    }
	} else if ($pend.attr("type") == "checkbox") {
	    var tmp = $pend.prop("checked");
	    $pend.removeAttr("name").prop("checked", $old.prop("checked"));
	    $old.prop("checked", tmp);
	    if ($pend.is(":checked") != $old.is(":checked")) {
		$label = $(".old").find("label[for="+id+"]");
		addMergeButtons($label, id);
	    }

	} else {
	    $old.attr("data-copy", $pend.val());
	    $pend.val($old.val()).attr("disabled", "disabled");
	    $old.val($old.attr("data-copy"));
	    if ($pend.val() != $old.val()) {
		$label = $(".old").find("label[for="+id+"]");
		addMergeButtons($label, id);
	    }
	}
    });
    var h1 = $(".old h1").html();
    $(".old h1").html($(".modified h1").html());
    $(".modified h1").html(h1);
});
