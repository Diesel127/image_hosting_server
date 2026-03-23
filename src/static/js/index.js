// Frontend logic for the home page (`/`).
// - Randomly shows one of the `.hero__img` images.
// - Redirects to `/upload` when the CTA button is clicked.
document.addEventListener('DOMContentLoaded', function () {
    const allImgBlocks = document.querySelectorAll('.hero__img');
    if (allImgBlocks.length > 0) {
        // Pick a random hero image and make it visible.
        const randomIndex = Math.floor(Math.random() * allImgBlocks.length);
        allImgBlocks[randomIndex].classList.add('is-visible');
    }

    if (window.location.pathname === '/') {
        // The rest of the CSS uses a light background; the home page
        // switches to a darker background for contrast.
        document.body.style.setProperty('background-color', '#151515');
    }

    const showcaseButton = document.querySelector('.header__button-btn');
    if (showcaseButton) {
        // CTA button navigates to the upload screen.
        showcaseButton.addEventListener('click', function () {
            window.location.href = '/upload';
        });
    }
});
