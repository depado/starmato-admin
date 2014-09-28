var need_confirm = false;
var already_ready = false;
$(document).ready(function() {
    if (already_ready == false) {
	already_ready = true;
	$(".top-menu a").each(function() {
	    $(this).attr("rel", $(this).attr("href"));
	    $(this).attr("href", "#");
	    $(this).click(function() {
		$("#id_post_url_save").val($(this).attr("rel"));
		createChoicePopup("Enregistrer et quitter", "Annuler", "Quitter", "jQuery('input[name=_continue]').click();", "return false;", "location.href = '"+$(this).attr("rel")+"';", "QUITTER SANS ENREGISTRER ?");
	    });
	});
	
	$(document).keydown(function(e) {
	    if (e.which == 13 && e.target.tagName.toUpperCase() != "TEXTAREA")
		return false;
	});
	$('form').each(function() { 
	    $(this).change(function() {
		need_confirm = true;
	    });
	});
	setTimeout("$('iframe').each(function() {$(this).mouseover(function() { need_confirm = true; });});", 1000);
    }
});

function hidePopup()
{
    popup = $('#confirm_popup');
    document.body.removeChild(popup[0]);
}
function createWarningPopup(confirm_val, confirm_func, text)
{
    createConfirmPopup(confirm_val, undefined, confirm_func, undefined, text);
}

function createConfirmPopup(confirm_val, cancel_val, confirm_func, cancel_func, text)
{
    if (need_confirm == false)
	eval(confirm_func)();
    else
    {
	popup = document.createElement('div');
	popup.setAttribute('id', 'confirm_popup');

	confirm_btn = document.createElement('input');
	confirm_btn.type = "button";
	confirm_btn.setAttribute('class', 'confirm_btn');
	confirm_btn.setAttribute('onClick', 'javascript:hidePopup();'+confirm_func+';');
	confirm_btn.value = confirm_val;
	
	if (cancel_val != undefined)
	{
	    cancel_btn = document.createElement('input');
	    cancel_btn.type = 'button';
	    cancel_btn.setAttribute('class', 'cancel_btn');
	    cancel_btn.setAttribute('onClick', 'javascript:hidePopup();'+cancel_func+';');
	    cancel_btn.value = cancel_val;
	}
	
	question_div = document.createElement('div');
	question_div.setAttribute('class', 'question_div');
	question = document.createTextNode(text);
	question_div.appendChild(question);

	popup.appendChild(question_div);
	popup.appendChild(confirm_btn);
	if (cancel_val != undefined)
	{
	    popup.appendChild(cancel_btn);
	}
	document.body.appendChild(popup);

	var x = (window.innerWidth - popup.offsetWidth) / 2;
	var y = (window.innerHeight - popup.offsetHeight) / 2 + document.documentElement.scrollTop;
	popup.style.top = y+"px";
	popup.style.left = x+"px";
	popus.focus();
	$('.confirm_btn').focus().css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
	$('.cancel_btn').css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
    }
}

function createChoicePopup(confirm_val, cancel_val, option_val, confirm_func, cancel_func, option_func, text)
{
    if (need_confirm == false)
	eval(option_func);
    else
    {
	popup = document.createElement('div');
	popup.setAttribute('id', 'confirm_popup');

	confirm_btn = document.createElement('input');
	confirm_btn.type = "button";
	confirm_btn.setAttribute('class', 'confirm_btn');
	confirm_btn.setAttribute('onClick', 'javascript:hidePopup();'+confirm_func+';');
	confirm_btn.value = confirm_val;
		
	if (cancel_val != undefined)
	{
	    cancel_btn = document.createElement('input');
	    cancel_btn.type = 'button';
	    cancel_btn.setAttribute('class', 'cancel_btn');
	    cancel_btn.setAttribute('onClick', 'javascript:hidePopup();'+cancel_func+';');
	    cancel_btn.value = cancel_val;
	}

	if (option_val != undefined)
	{
	    option_btn = document.createElement('input');
	    option_btn.type = 'button';
	    option_btn.setAttribute('class', 'option_btn');
	    option_btn.setAttribute('onClick', 'javascript:hidePopup();'+option_func+';');
	    option_btn.value = option_val;
	}
	
	question_div = document.createElement('div');
	question_div.setAttribute('class', 'question_div');
	question = document.createTextNode(text);
	question_div.appendChild(question);

	popup.appendChild(question_div);
	popup.appendChild(confirm_btn);
	if (cancel_val != undefined)
	{
	    popup.appendChild(cancel_btn);
	}
	if (option_val != undefined)
	{
	    popup.appendChild(option_btn);
	}
	document.body.appendChild(popup);

	var x = (window.innerWidth - popup.offsetWidth) / 2;
	var y = (window.innerHeight - popup.offsetHeight) / 2 + document.documentElement.scrollTop;
	popup.style.top = y+"px";
	popup.style.left = x+"px";
	$('.confirm_btn').focus().css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
	$('.cancel_btn').css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
	$('.option_btn').css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
    }
}

function pdfCheckbox(form, name, label)
{
    tick = document.createElement('input');
    tick.setAttribute('type', 'checkbox');
    tick.setAttribute('name', name);
    tick.setAttribute('value', name);
    tick.setAttribute('checked', 'checked');
    label = document.createTextNode(label);
    form.appendChild(tick);
    form.appendChild(label);
}

function setAddresses()
{
    var addresses = $('#addresses');
    $('#address option:selected').each(function() {
	addresses.val($(this).val()+";" + addresses.val());
    });
    $("#confirm_popup form").submit();
}

function createMessagePopup(confirm_val, cancel_val, confirm_func, cancel_func, docs, contact_id, client_id)
{
    popup = document.createElement('div');
    popup.setAttribute('id', 'confirm_popup');

    confirm_btn = document.createElement('input');
    confirm_btn.type = "button";
    confirm_btn.setAttribute('class', 'confirm_btn');
    confirm_btn.setAttribute('onClick', 'javascript:setAddresses();hidePopup();');
    confirm_btn.value = confirm_val;
    
    if (cancel_val != undefined)
    {
	cancel_btn = document.createElement('input');
	cancel_btn.type = 'button';
	cancel_btn.setAttribute('class', 'cancel_btn');
	cancel_btn.setAttribute('onClick', 'javascript:hidePopup();'+cancel_func+';');
	cancel_btn.value = cancel_val;
    }

    question_div = document.createElement('div');
    question_div.setAttribute('class', 'question_div');

    message_form = document.createElement('form');
    message_form.setAttribute('action', confirm_func);
    message_form.setAttribute('method', 'GET');

    question = document.createTextNode("Choisissez les documents à envoyer");
    message_form.appendChild(question);
    br = document.createElement('br');
    message_form.appendChild(br);

    if (docs == "bs")
    {
	pdfCheckbox(message_form, 'make_bs', " Bon de Sortie | ");
	pdfCheckbox(message_form, 'make_list', " Non-retours | ");
	pdfCheckbox(message_form, 'make_devis', " Devis | ");
	pdfCheckbox(message_form, 'make_assurance', " Assurance");
    }
    else if (docs == "facture")
	pdfCheckbox(message_form, 'make_facture', " Facture");
    else if (docs == "pl")
	pdfCheckbox(message_form, 'make_prestation_libre', " Facture");
	
    br = document.createElement('br');
    message_form.appendChild(br);
    br = document.createElement('br');
    message_form.appendChild(br);
    question = document.createTextNode("Insérez un message personnalisé");
    message_form.appendChild(question);

    message_area = document.createElement('textarea');
    message_area.setAttribute('id', 'message');
    message_area.setAttribute('name', 'message');
    question = document.createTextNode("Bonjour,\r\n\r\nVoici le document consécutif à votre visite au Souk.\r\n\r\nCordialement,");
    message_area.appendChild(question);
    message_form.appendChild(message_area);

    br = document.createElement('br');
    message_form.appendChild(br);
    br = document.createElement('br');
    message_form.appendChild(br);

    question = document.createTextNode("Indiquez et/ou sélectionnez des destinataires");
    message_form.appendChild(question);

    br = document.createElement('br');
    message_form.appendChild(br);

    addresses = document.createElement('input');
    addresses.setAttribute('type', 'text');
    addresses.setAttribute('id', 'addresses');
    addresses.setAttribute('name', 'addresses');
    message_form.appendChild(addresses);

    br = document.createElement('br');
    message_form.appendChild(br);

    address_select = document.createElement('select');
    address_select.setAttribute('id', 'address');
    address_select.setAttribute('size', '4');
    address_select.setAttribute('multiple', 'multiple');
    address_select.setAttribute('name', 'address');

    jQuery.ajax({
	url: "/argamato/json/emails/"+contact_id+"/"+client_id+"/",
	context: document.body,
	success: function(data, textStatus, jqXHR) {
	    values = eval(data);
	    for (cnt = 0; cnt < values.length; cnt++)
	    {
		option = document.createElement('option');
		option.setAttribute('value', values[cnt].email);
		label = document.createTextNode(values[cnt].email+" ("+values[cnt].label+")");
		option.appendChild(label);
		address_select.appendChild(option);
	    }
	}
    });

    message_form.appendChild(address_select);
   
    br = document.createElement('br');
    message_form.appendChild(br);

    message_form.appendChild(confirm_btn);
    message_form.appendChild(cancel_btn);
    question_div.appendChild(message_form);

    popup.appendChild(question_div);
   
    document.body.appendChild(popup);

    var x = (window.innerWidth - popup.offsetWidth) / 2;
    var y = (window.innerHeight - 420) / 2 + document.documentElement.scrollTop;
    popup.style.top = y+"px";
    popup.style.left = x+"px";
    $('#confirm_popup').css('height', '420px');
    $('.confirm_btn').focus().css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
    $('.cancel_btn').css('margin-top', $('#confirm_popup').height() - $('.question_div').height() - 55);
}