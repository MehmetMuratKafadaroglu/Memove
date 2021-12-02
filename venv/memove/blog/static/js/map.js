if(window.location.hash == '#map'){showMap()}
else{exitMap()}

window.onpopstate = map_history;
function showMap(){
    document.getElementById('map').style.display = "block";
    document.getElementById('exit_button').style.display = "block";
    document.getElementById('map').src = "map_list_view/?" + window.location.search;
    if(window.location.hash !== '#map')
    {
        history.pushState(null, null, window.location.href + '#map');
    }
}

function map_history()
{
    if(window.location.hash == '#map'){showMap()}
    else{exitMap()}    
}

function exitMap(){
    try{
    document.getElementById('map').style.display = "none";
    document.getElementById('exit_button').style.display = "none";
    }
    catch(err){console.dir(err)}
}