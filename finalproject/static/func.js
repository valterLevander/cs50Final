

$('document').ready(function(){
    // Select all links with hashes
    $('a[href*="#"]')
      // Remove links that don't actually link to anything
      .not('[href="#"]')
      .not('[href="#0"]')
      .click(function(event) {
        // On-page links
        if (
          location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') 
          && 
          location.hostname == this.hostname
        ) {
          // Figure out element to scroll to
          var target = $(this.hash);
          target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
          // Does a scroll target exist?
          if (target.length) {
            // Only prevent default if animation is actually gonna happen
            event.preventDefault();
            $('html, body').animate({
              scrollTop: target.offset().top
            }, 1000, function() {
              // Callback after animation
              // Must change focus!
              var $target = $(target);
              $target.focus();
              if ($target.is(":focus")) { // Checking if the target was focused
                return false;
              } else {
                $target.attr('tabindex','-1'); // Adding tabindex for elements not focusable
                $target.focus(); // Set focus again
              };
            });
          }
        }
  });
    
    $("#before").delay(500).fadeOut(2000);
    
    if ($(window).width() < 601) {
       $("button").removeClass("btn-lg");
    } else {
        $("button").addClass("btn-lg");
    }
  
    $(".jqb").click(function(){
        var title = document.getElementById("instruct");
        var instruct = document.getElementById("instructions");
        if(title.value == ""){
            $("#error").css("color", "red").text("Missing title");
        } else if(instruct.value == ""){
             $("#error").css("color", "yellow").text("Missing instructions");
        } else {
            $("#error").css("color", "green").text("Uploaded");
        }
    });
    $("#option").click(function(){
        $("#opt").slideToggle();
    })
    if($(window).width() > 0){
        $(".feed:odd ").css("margin-bottom", "75px");
        $(".feed:even ").css("margin-bottom", "25px").css("border-top", "2px dashed #f48642").css("padding-top", "25px");
    }
    if($(window).width() > 660){
            $("button").removeClass("btn-sm");
            $("button").addClass("btn-md");
        }
    $(".header_text:odd ").css("color", "black").css("font-size", "25px").css("text-align", "center");
    $(".header_text:even").css("border-bottom", "2px dashed #f48642").css("padding-bottom", "100px");
    $("#menu").click(function(){
        $("#dropdown").slideDown()
    })
    $("#menu2").click(function(){
        $("#dropdown").slideUp()
    })
    $("#loga").mouseover(function(){
        $("#loga").fadeOut(300).delay(1600).fadeIn(300);
        $("#e-design").delay(300).fadeIn(300).delay(1000).fadeOut(300);
    })
    $("#uploadwindow").click(function(){
        $("#ppfile").fadeToggle()
    })
})