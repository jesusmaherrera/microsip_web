 $(window).scroll(function(event) {
      
      var y = $(this).scrollTop();
      if (y >= 52) {
          $('#tools-module-bar').addClass('navbar-fixed-top');
      } else {
          $('#tools-module-bar').removeClass('navbar-fixed-top');
      }
});