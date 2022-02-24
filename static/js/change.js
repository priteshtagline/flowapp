$(document).ready(function(){
  var count = 0;
     $("#pushnotificaton").click(function () {
       $("#pushnotificaton").html("send second notification");
         if (count >= 1) {
             $("#pushnotificaton").hide();
         } else count++
 
     });
  })(django.jquery);    