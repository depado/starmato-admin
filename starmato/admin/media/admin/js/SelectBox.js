var SelectBox = {
    cache: new Object(),
    init: function(id) {
        var box = document.getElementById(id);
        var node;
        SelectBox.cache[id] = new Array();
	for (var i = 0; (node = box.getElementsByTagName("option")[i]); i++) {
	    if (node.parentNode.tagName == "OPTGROUP")
                SelectBox.add_to_cache(id, node, node.parentNode.label);
	    else
		SelectBox.add_to_cache(id, node, null);
        }
	var span = document.createElement('span');
	var h2 = box.parentNode.firstChild;
	h2.appendChild(span);
	h2.appendChild(h2.firstChild);

	if (typeof post_selectbox_init == 'function')
	    post_selectbox_init(id);
    },
    redisplay: function(id) {
        // Repopulate HTML select box from cache
        var box = document.getElementById(id);
	var st = box.scrollTop;
	if (box == null)
	    return;

        box.options.length = 0; // clear all options
	groups = box.getElementsByTagName("optgroup");
	for (var i= 0, j = groups.length; i < j; i++)
	    box.removeChild(groups[0]);
        for (var i = 0, j = SelectBox.cache[id].length; i < j; i++) {
            var node = SelectBox.cache[id][i];
            if (node.options) {
		var opt;
		group = document.createElement("optgroup");
		group.label = node.value;
		for (var k = 0; (opt = node.options[k]); k++) {
		    if (!opt.hidden)
			group.appendChild(new Option(opt.text, opt.value, false, false));
		}
		box.appendChild(group);
            } else {
		if (!node.hidden)
                    box.appendChild(new Option(node.text, node.value, false, false));
	    }
        }
	var span = box.parentNode.firstChild.firstChild;
	box.scrollTop = st;
	span.innerHTML = box.options.length+" ";
    },
    filter: function(id, text) {
        // Redisplay the HTML select box, displaying only the choices containing ALL
        // the words in text. (It's an AND search.)
        var tokens = text.toLowerCase().split(/\s+/);
        var node, token, opt;
        for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
            if (node.options) {
		for (cnt in node.options) {
		    opt = node.options[cnt];
		    opt.hidden = 0;
		    for (var j = 0; (token = tokens[j]); j++) {
			if (opt.text.toLowerCase().indexOf(token) == -1) {
			    opt.hidden = 1;
			}
		    }
		}
	    } else {
		node.hidden = 0;
		for (var j = 0; (token = tokens[j]); j++) {
		    if (node.text.toLowerCase().indexOf(token) == -1) {
			node.hidden = 1;
		    }
		}
	    }
        }
        SelectBox.redisplay(id);
    },
    delete_from_cache: function(id, value) {
        var node = null;
        for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
            if (node.value == value) {
		SelectBox.cache[id].splice(i, 1);
                break;
            } else if (node.options) {
		for (var j = 0; (option = node.options[j]); j++) {
		    if (option.value == value) {
			node.options.splice(j, 1);
			if (node.options.length == 0)
			    SelectBox.cache[id].splice(i, 1);
			break;
		    }
		}
	    }
        }
    },
    add_to_cache: function(id, option, optgroup) {
	if (optgroup == null) {
	    SelectBox.cache[id].push(option);
	} else {
            var node = null;
	    var inserted = 0;
            for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
		if (node.options && node.value == optgroup) {
		    node.options.push(option);
		    inserted = 1;
		    break;
		}
	    }
	    if (inserted == 0) {
		SelectBox.cache[id].push({value: optgroup, options: [option]});		
	    }
	}
    },
    cache_contains: function(id, value) {
        // Check if an item is contained in the cache
        var node;
        for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
            if (node.value == value) {
                return true;
            }
	    if (node.options) {
		for (var j = 0; (opt = node.options[j]); j++) {
		    if (opt.value == value) {
			return true;
		    }
		}
	    }
        }
        return false;
    },
    move: function(from, to) {
        var from_box = document.getElementById(from);
        var to_box = document.getElementById(to);
        var option;
        for (var i = 0; (option = from_box.options[i]); i++) {
            if (option.selected && SelectBox.cache_contains(from, option.value)) {
		if (option.parentNode.tagName == "OPTGROUP")
                    SelectBox.add_to_cache(to, option, option.parentNode.label);
		else {
                    SelectBox.add_to_cache(to, option, null);
		}
                SelectBox.delete_from_cache(from, option.value);
            }
        }
        SelectBox.redisplay(from);
        SelectBox.redisplay(to);
    },
    move_all: function(from, to) {
        var from_box = document.getElementById(from);
        var to_box = document.getElementById(to);
        var option;
        for (var i = 0; (option = from_box.options[i]); i++) {
            if (SelectBox.cache_contains(from, option.value)) {
                SelectBox.add_to_cache(to, {value: option.value, text: option.text, displayed: 1});
                SelectBox.delete_from_cache(from, option.value);
            }
        }
        SelectBox.redisplay(from);
        SelectBox.redisplay(to);
    },
    copy_all: function(from, to, check) {
        var from_box = document.getElementById(from);
        var to_box = document.getElementById(to);
        var check_box = document.getElementById(check);
        var option;
	var from_optgroups = new Array();
	var subcache;
	var from_optgroup;

	if (from_box != null)
	    from_optgroups = from_box.getElementsByTagName("optgroup");
	if (check_box != undefined)
	{
	    var check_options = check_box.getElementsByTagName("option");
	    for (option in check_options)
	    {
		option = check_options[option];
		if (!SelectBox.cache_contains(from, option.value)) {
		    SelectBox.delete_from_cache(check, option.value);
		}
	    }
            SelectBox.redisplay(check);
	}

        for (var cnt=0; cnt < from_optgroups.length; cnt++) 
	{
	    from_optgroup = from_optgroups[cnt];
	    subcache = [];
            for (var i = 0; (node = SelectBox.cache[to][i]); i++) 
	    {
		if (node.value == from_optgroup.label)
		    SelectBox.delete_from_cache(to, node.value);
	    }
	    for (var i = 0; (option = from_optgroup.getElementsByTagName("option")[i]); i++) 
	    {
		if (!SelectBox.cache_contains(check, option.value)) {
		    subcache.push({value: option.value, text: option.text});
		}
	    }
	    if (subcache.length)
		SelectBox.add_to_cache(to, {value: from_optgroup.label, options: subcache});
	}
        SelectBox.redisplay(from);
        SelectBox.redisplay(to);
    },
    sort: function(id) {
        SelectBox.cache[id].sort( function(a, b) {
            a = a.text.toLowerCase();
            b = b.text.toLowerCase();
            try {
                if (a > b) return 1;
                if (a < b) return -1;
            }
            catch (e) {
                // silently fail on IE 'unknown' exception
            }
            return 0;
        } );
    },
    select_all: function(id) {
        var box = document.getElementById(id);
	var groups = box.getElementsByTagName("optgroup");
	if (groups.length > 0) {
	  var group = null;
	  for (var i = 0; (group = groups[i]); i++) {
	    var options = group.getElementsByTagName("option");
	    for (var j = 0; j < options.length; j++) {
	      options[j].selected = 'selected';	  
	    }
	  }
	}
	else {
	  for (var i = 0; i < box.options.length; i++) {
            box.options[i].selected = 'selected';
	  }
	}
    },
}
