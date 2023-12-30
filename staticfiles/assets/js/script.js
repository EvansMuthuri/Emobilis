
$(document).ready(function() {
    // Initialize the slider using jQuery
    $('.slider').slick({
        slidesToShow: 3, // Show 3 slides at a time
        slidesToScroll: 1, // Scroll 1 slide at a time
        autoplay: true, // Autoplay the slider
        autoplaySpeed: 2000, // Set autoplay speed in milliseconds
        prevArrow: '<button type="button" class="slick-prev">Previous</button>', // Customize previous button
        nextArrow: '<button type="button" class="slick-next">Next</button>', // Customize next button
        responsive: [
            {
                breakpoint: 768, // Adjust settings for smaller screens if needed
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 480, // Adjust settings for even smaller screens if needed
                settings: {
                    slidesToShow: 1,
                }
            }
        ]
    });
});
