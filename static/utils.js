/**
* Delay for a number of milliseconds
*/
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Appear function to fade in
function appear(elm, i, step, speed, sleeptime){
    var t_o;
    //initial opacity
    i = i || 0;
    //opacity increment
    step = step || 5;
    //time waited between two opacity increments in msec
    speed = speed || 50;
    elm.style.opacity = 0;

    sleep(sleeptime);
    t_o = setInterval(function(){
        //get opacity in decimals
        var opacity = i / 100;
        //set the next opacity step
        i = i + step;
        if(opacity > 1 || opacity < 0){
            clearInterval(t_o);
            //if 1-opaque or 0-transparent, stop
            return;
        }
        //modern browsers
        elm.style.opacity = opacity;
        //older IE
        elm.style.filter = 'alpha(opacity=' + opacity*100 + ')';
    }, speed);
}



