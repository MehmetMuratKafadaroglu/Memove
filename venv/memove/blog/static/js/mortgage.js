function power(x,y){
    var a =0;
    if(y == 2){
        return x*x;
    }
    else if(y==1){
        return x;
    }
    else if(y==0){
        return 1;
    }
    else
    {
        for(var i=2;i <= y ;i++)
        {  
            if(a==0)
            { 
                a = x *x;
            }

            else
            {
                a= a*x
            }
            
        }
        return a;
    }
    
}
//document.getElementById("property-price").value = Number(document.getElementById("property-price").value)*0.9
document.getElementById("deposit").value = Number(document.getElementById("deposit").value)*0.1

function mortgage_calculate(){
    var P= Number(document.getElementById("property-price").value)-Number(document.getElementById("deposit").value);
    var r = (document.getElementById("interest-rate").value/12/100);
    var t = (document.getElementById("number-of-years").value);
    var n = 12;

    var v1 = power((1 +r), n*t)
    var payment = P *r * v1 / (v1 - 1);

    document.getElementById("payments-per-month").value=payment
}
