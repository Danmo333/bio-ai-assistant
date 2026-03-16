async function send() {
    const question = document.getElementById("question").value;

    const response = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question})
    });

    const data = await response.json();
    document.getElementById("answer").innerText = data.answer;
}

let history = [];

function addMessage(role, text){

    const chatBox = document.getElementById("chat-box");

    const message = document.createElement("div");
    message.className = "message " + role;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerText = text;

    message.appendChild(bubble);
    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage(){

    const input = document.getElementById("question");
    const question = input.value.trim();

    if(question === "") return;

    addMessage("user", question);

    history.push({
        role:"user",
        content:question
    });

    input.value = "";

    fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            messages:history
        })
    })
    .then(res => res.json())
    .then(data => {

        const answer = data.answer;

        addMessage("assistant", answer);

        history.push({
            role:"assistant",
            content:answer
        });

    });

}

document.getElementById("question").addEventListener("keypress", function(e){
    if(e.key === "Enter"){
        sendMessage();
    }
});