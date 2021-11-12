//  Handles burger activation for navbar menu mobile
const burgerIcon = document.querySelector('#burger');
const navbarMenu = document.querySelector('#navbar-links');

burgerIcon.addEventListener('click', () => {
  navbarMenu.classList.toggle('is-active');
});

$(function () {
  $('a').each(function () {
    if ($(this).prop('href') == window.location.href) {
      $(this).addClass('is-active');
      $(this).parents('li').addClass('is-active');
    }
  });
});
