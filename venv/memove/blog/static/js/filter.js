function getParams(url) {
	var params = {};
	var parser = document.createElement('a');
	parser.href = url;
	var query = parser.search.substring(1);
    var vars = query.split('&');
    
	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split('=');
		params[pair[0]] = decodeURIComponent(pair[1]);
	}
	return params;
}

function showFilters()
{
    var x = document.getElementById("filters");
    if(x.style.display=="none")
    {
        x.style.display="block"
    }

    else
    {
        x.style.display="none"
    }
}
function press_search(event) {
    console.log(event.keyCode)
    if (event.which == 13 || event.keyCode == 13) {
        filter()
        return false;
    }
    return true;
};
function filter()
{
    var min_price = document.getElementById('min_price').value;
    var max_price = document.getElementById('max_price').value;
    var min_beds = document.getElementById('min_beds').value;
    var max_beds = document.getElementById('max_beds').value;
    var min_baths = document.getElementById('min_baths').value;
    var max_baths = document.getElementById('max_baths').value;
    var house = document.getElementById('house').checked;
    var flat = document.getElementById('flat').checked;
    var boat = document.getElementById('boat').checked;
    var sle = document.getElementById('sortselect').value;
    var property_location = document.getElementById('location').value;
    var ad_type = document.getElementById('ad_type').value;
    if(property_location == ""){
        alert("Please enter a location")
    }
    location.replace
    (
        window.location.pathname
        + "list/"
        +"?" 
        + "min_price=" + min_price 
        + "&max_price=" + max_price 
        + "&min_beds=" + min_beds
        + "&max_beds=" + max_beds
        + "&min_baths=" + min_baths
        + "&max_baths=" + max_baths
        + "&house=" + house
        + "&flat=" + flat
        + "&boat=" + boat 
        + "&sort=" + sle
        + "&location=" + property_location
        + "&ad_type=" + ad_type
    )

}


//url i soru isaretine gore split 
function updateSortOrder(){
    // 1. sortselect icinde secili olani al
    var sle = document.getElementById('sortselect').value;

    // 2. url'e gergerger=XXXX selectten gelen sort orderi ekle.
    /*var loc = window.location.href;
    if (loc.indexOf('?') > -1)
        loc = loc + '&gergerger=' + sle;
    else    
        loc = loc + '?gergerger=' + sle;
    window.location.href=loc
    */
    
    var params = getParams(window.location.href);
    params['sort'] = sle;
    location.replace("?" + "agent=" + params['agent'] + "&" + "sort=" + params['sort']);

 //params = {'agent' : '17', 'gergerger':'id'}
}

/*{
    'gergerger': 'nume',
    'sort_order': 'date'
}*/


window.onload=updateselection;
updateselection()


function updateselection()
{
    if(!document.getElementById("sortselect")){return}
    if(!document.getElementById("ad_type")){return}

    var a = getParams(window.location.href);
    selectChange("min_price",a["min_price"])
    selectChange("max_price", a["max_price"])
    selectChange("min_beds", a["min_beds"])
    selectChange("max_beds", a["max_beds"])
    selectChange("min_baths", a["min_baths"])
    selectChange("max_baths", a["max_baths"])

    
    document.getElementById("house").checked = a['house']=="true";
    document.getElementById("flat").checked = a['flat']=="true"
    document.getElementById("boat").checked = a['boat']=="true";
    
    if(a["sort"]=="low_to_high_price")
    {
        document.getElementById('sortselect').selectedIndex = 0;
    }
    if(a["sort"]=="high_to_low_price")
    {
        document.getElementById('sortselect').selectedIndex = 1;
    }
    if(a["sort"]=="most_recent")
    {
        document.getElementById('sortselect').selectedIndex =2;
    }
    
    document.getElementById("ad_type").selectedIndex = a["ad_type"]=="sale"?0:1;

    if(a["ad_type"]=="rent")
    {
        document.getElementById("ad_type").selectedIndex = 1;
    }

    if(a["location"]!="undefined" && a["location"] != "" &&  a["location"] != undefined ){
        document.getElementById("sortselect").style.display = "block";
        document.getElementById("location").value = a["location"];
    }
    document.getElementById("sortselect").onchange=filter

    document.getElementById("location").onkeypress = press_search;

}

function selectChange(selectID, selectValue)
{
    var ID = document.getElementById(selectID);
    if(!ID){return}

    var selectoption = ID.options;
    for(var i = 0; i < selectoption.length; i++)
    {
        var newoption = selectoption[i]
        if(newoption.value==selectValue)
        {
            ID.selectedIndex = i;
            return 
        }
    }
}

