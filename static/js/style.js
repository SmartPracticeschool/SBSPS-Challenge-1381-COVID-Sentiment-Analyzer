function validatesign(){
    var p1 = document.getElementById("p1").value;
    var p2 = document.getElementById("p2").value;
    if(p1 != p2){
        alert("Password Confirmation Failed!!!");
        document.location.reload(true);
        return false;
    }
}

function validate(){
    var uname = document.getElementById("uname").value;
    var pass = document.getElementById("pass").value;
    if(uname.trim()=="" || pass.trim()==""){
        alert("BLANK VALUES NOT ALLOWED!!!");
        document.location.reload(true);
        return false;
    }
}
function fetch(){
    $.get("https://api.covid19api.com/summary",
    function(data){
        //console.log(data['Countries'].length);
        var tbval = document.getElementById('tbval');

        for(var i=1;i<=(data['Countries'].length);i++){
            var x = tbval.insertRow();
            x.insertCell(0);
            tbval.rows[i].cells[0].innerHTML = data['Countries'][i-1]['Country'];
            x.insertCell(1);
            tbval.rows[i].cells[1].innerHTML = data['Countries'][i-1]['TotalConfirmed'];
            x.insertCell(2);
            tbval.rows[i].cells[2].innerHTML = data['Countries'][i-1]['TotalRecovered'];
            x.insertCell(3);
            tbval.rows[i].cells[3].innerHTML = data['Countries'][i-1]['TotalDeaths'];
            x.insertCell(4);
            tbval.rows[i].cells[4].innerHTML = data['Countries'][i-1]['NewConfirmed'];
            x.insertCell(5);
            tbval.rows[i].cells[5].innerHTML = data['Countries'][i-1]['NewRecovered'];
        }
    }
    
    )
    $.get("https://api.covid19india.org/data.json",
    function(data){
        //console.log(data['Countries'].length);
        var tbval1 = document.getElementById('tbval1');

        for(var i=1;i<=(data['statewise'].length);i++){
            var x1 = tbval1.insertRow();
            x1.insertCell(0);
            tbval1.rows[i].cells[0].innerHTML = data['statewise'][i-1]['state'];
            x1.insertCell(1);
            tbval1.rows[i].cells[1].innerHTML = data['statewise'][i-1]['active'];
            x1.insertCell(2);
            tbval1.rows[i].cells[2].innerHTML = data['statewise'][i-1]['confirmed'];
            x1.insertCell(3);
            tbval1.rows[i].cells[3].innerHTML = data['statewise'][i-1]['recovered'];
            x1.insertCell(4);
            tbval1.rows[i].cells[4].innerHTML = data['statewise'][i-1]['deaths'];
        }
    }
    
    )
}
