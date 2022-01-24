function Save()
{
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && this.status == 200) 
        {
            var save_result = JSON.parse(xhttp.responseText);
            if (save_result.code == 0)
            {
                document.getElementById("save_button").innerHTML = "Unsave" ;
            }
            else
            {
                document.getElementById("warning_button").style.display = "block";
            }
        }
           
    };
    var current_url = window.location.pathname.split("/");
    var slug_and_id = current_url[2].split("-");

    xhttp.open("GET", '/property_save/'+slug_and_id[0]+'/', true);
    xhttp.send();
}