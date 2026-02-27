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