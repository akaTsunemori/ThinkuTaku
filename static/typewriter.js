function printLetterByLetter(destination, message) {
    var i = 0;
    var speed = 60;
    function type() {
        document.getElementById(destination).innerHTML += message.charAt(i);
        if (speed > 60) {
            clearInterval(interval);
            speed = 60;
            interval = setInterval(type, speed);
        }
        if (",?!:;".includes(message.charAt(i))) {
            clearInterval(interval);
            speed = 600;
            interval = setInterval(type, speed);
        }
        if (message.charAt(i) == ".") {
            clearInterval(interval);
            speed = 1200;
            interval = setInterval(type, speed);
        }
        if (i > message.length) {
            clearInterval(interval);
        }
        i++;
    }
    var interval = setInterval(type, speed);
}