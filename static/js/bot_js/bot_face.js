document.addEventListener('DOMContentLoaded', function () {
    const mouth = document.querySelector('.mouth');
    const eyes = document.querySelectorAll('.eye');

    function animateMouth() {
        mouth.style.animationPlayState = 'running';

        setTimeout(() => {
            mouth.style.animationPlayState = 'paused';

            setTimeout(animateMouth, 1000);
        }, 1000);
    }

    function moveEyes() {
        eyes.forEach(eye => {
            const x = Math.random() * 10 - 5;
            const y = Math.random() * 10 - 5;
            eye.style.transform = `translate(${x}px, ${y}px)`;
        });

        setTimeout(moveEyes, Math.random() * 1000 + 1000);
    }

    function blinkEyes() {
        eyes.forEach(eye => {
            eye.classList.add('blinking');
            setTimeout(() => {
                eye.classList.remove('blinking');
            }, 200);
        });

        setTimeout(blinkEyes, Math.random() * 5000 + 2000);
    }

    animateMouth();
    moveEyes();
    blinkEyes();
});