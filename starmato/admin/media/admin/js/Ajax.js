function getAjsonax(url, callback)
{
    $('#ajsonax').fadeIn();
    $("#ajsonax").mouseover(function(e){
	$('#ajsonax img').css('top', e.clientY+$(window).scrollTop()).css('left', e.clientX);
    }).mousemove(function(e){
	$('#ajsonax img').css('top', e.clientY+$(window).scrollTop()).css('left', e.clientX);
    });

    var f = typeof callback == 'function' ? callback : null;
    jQuery.ajax({
        url: url,
        context: document.body,
        success: function(data) {
	    f(data);
	    $('#ajsonax').fadeOut();
	},
	error: function() {
	    $('#ajsonax').fadeOut();
	}
    });
}