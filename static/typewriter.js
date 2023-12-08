function printLetterByLetter(destination, message) {
    var i = 0;
    var speed = 100;
    function type() {
        document.getElementById(destination).innerHTML += message.charAt(i);
        if (speed > 50) {
            clearInterval(interval);
            speed = 50;
            interval = setInterval(type, speed);
        }
        if (",?!".includes(message.charAt(i))) {
            clearInterval(interval);
            speed = 750;
            interval = setInterval(type, speed);
        }
        if (message.charAt(i) == ".") {
            clearInterval(interval);
            speed = 1250;
            interval = setInterval(type, speed);
        }
        if (i > message.length) {
            clearInterval(interval);
        }
        i++;
    }
    var interval = setInterval(type, speed);
}