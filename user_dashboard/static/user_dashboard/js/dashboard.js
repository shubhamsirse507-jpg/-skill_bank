// Skill Bank Dashboard Interactivity
document.addEventListener('DOMContentLoaded', function () {
    console.log('Skill Bank Dashboard JS loaded.');
});

function sendChatbotMsg() {
    let msgInput = document.getElementById("msg");
    if (!msgInput) return;
    let msg = msgInput.value.trim();
    if (!msg) return;

    fetch("/user/chatbot/?message=" + encodeURIComponent(msg))
        .then(response => response.json())
        .then(data => {
            let replyBox = document.getElementById("reply");
            if (replyBox) {
                replyBox.innerHTML = data.reply || data.response || "Message sent!";
            }
        }).catch(err => console.log(err));
}
