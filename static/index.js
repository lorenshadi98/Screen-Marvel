//  Handles burger activation for navbar menu mobile
const burgerIcon = document.querySelector('#burger');
const navbarMenu = document.querySelector('#navbar-links');

burgerIcon.addEventListener('click', () => {
  navbarMenu.classList.toggle('is-active');
});
