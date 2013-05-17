/**
 * jQuery printPage Plugin
 * @version: 1.0
 * @author: Cedric Dugas, http://www.position-absolute.com
 * @licence: MIT
 * @desciption: jQuery page print plugin help you print your page in a better way
 */
 
(function( $ ){
  $.fn.printPage = function(options) {
    var pluginOptions = {
      attr : "href",
      url : false,
      message: "Please wait while we create your document" 
    };
    $.extend(pluginOptions, options);

    this.live("click", function(){  loadPrintDocument(this, pluginOptions); return false;  });
   
    function loadPrintDocument(el, pluginOptions){
      $("body").append(components.messageBox(pluginOptions.message));
      $("#printMessageBox").css("opacity", 0);
      $("#printMessageBox").animate({opacity:1}, 300, function() { addIframeToPage(el, pluginOptions); });
    }
    
    function addIframeToPage(el, pluginOptions){

        var url = (pluginOptions.url) ? pluginOptions.url : $(el).attr(pluginOptions.attr);

        if(!$('#printPage')[0]){
          $("body").append(components.iframe(url));
          $('#printPage').bind("load",function() {  printit();  })
        }else{
          $('#printPage').attr("src", url);
        }
    }
    
    function unloadMessage(){
      $("#printMessageBox").delay(1000).animate({opacity:0}, 700, function(){
        $(this).remove();
      });
    }
    
    function printit(){
      frames["printPage"].focus();
      frames["printPage"].print();
      unloadMessage();
    }
    
    var components = {
      iframe: function(url){
        return '<iframe id="printPage" name="printPage" src='+url+' style="position:absolute;top:0px; left:0px;width:0px; height:0px;border:0px;overfow:none; z-index:-1"></iframe>';
      },
      messageBox: function(message){
        return "<div id='printMessageBox' style='\
          position:fixed;\
          top:50%; left:50%;\
          text-align:center;\
          margin: -60px 0 0 -155px;\
          width:310px; height:120px; font-size:16px; padding:10px; color:#222; font-family:helvetica, arial;\
          opacity:0;\
          background:#fff url(images/print_icon.gif) center 40px no-repeat;\
          border: 6px solid #555;\
          border-radius:8px; -webkit-border-radius:8px; -moz-border-radius:8px;\
          box-shadow:0px 0px 10px #888; -webkit-box-shadow:0px 0px 10px #888; -moz-box-shadow:0px 0px 10px #888'>\
          "+message+"</div>";
      }
    }
  };
})( jQuery );
