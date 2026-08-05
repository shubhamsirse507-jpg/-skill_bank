function send() {

    let msg = document.getElementById("msg").value;

    fetch("/chatbot/?message=" + encodeURIComponent(msg))
        .then(response => response.json())
        .then(data => {
            document.getElementById("reply").innerHTML = data.reply;
        });

}