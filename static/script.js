document.addEventListener("DOMContentLoaded", function(){
    var width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    if (height < 800) {
        // document.getElementById("img").remove();
        document.getElementById("gradient").style.height = height - 73;
        initTerm();
    } else {
	setTimeout(function() {
            initTerm();
        }, 1);
    }
});

function initTerm() {
    this.term = rTerm({
        height: document.getElementById("gradient").offsetHeight * 0.85,
        username: "jiwidi",
        hostname: "earth",
        file: "/static/contacts.json",
        saveStrings: true,
        url:document.URL
    });
};

