async function sendMessage() {

    const input = document.getElementById("inputMessage");
    const mensagem = input.value.trim();
    const statusBot = document.getElementById("statusBot");

    if (!mensagem) return;

    const chatBody = document.getElementById("chatBody");

    // Mensagem do usuário
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.textContent = mensagem;

    chatBody.appendChild(userMessage);

    input.value = "";

    chatBody.scrollTop = chatBody.scrollHeight;

    // Status no cabeçalho
    statusBot.textContent = "Digitando...";
    statusBot.classList.add("typing-status");

    // Bolinha digitando no chat
    const typing = document.createElement("div");

    typing.className = "typing";

    typing.innerHTML = `
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatBody.appendChild(typing);

    chatBody.scrollTop = chatBody.scrollHeight;

    try {

       const response = await fetch(
    "/chat",
    {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: mensagem
        })
    }
);

        const data = await response.json();

        // Apenas para mostrar a animação por mais tempo
        await new Promise(resolve =>
            setTimeout(resolve, 1000)
        );

        typing.remove();

        statusBot.textContent = "● Online";
        statusBot.classList.remove("typing-status");

        const botMessage = document.createElement("div");

        botMessage.classList.add(
            "message",
            "bot"
        );

        botMessage.innerHTML =
            data.response.replace(/\n/g, "<br>");

        chatBody.appendChild(botMessage);

        chatBody.scrollTop =
            chatBody.scrollHeight;

    } catch (error) {

        typing.remove();

        statusBot.textContent = "● Online";
        statusBot.classList.remove("typing-status");

        console.error(error);

        const botMessage =
            document.createElement("div");

        botMessage.classList.add(
            "message",
            "bot"
        );

        botMessage.textContent =
            "Erro ao conectar com o servidor.";

        chatBody.appendChild(botMessage);

        chatBody.scrollTop =
            chatBody.scrollHeight;
    }
}


// Enter envia mensagem
document
    .getElementById("inputMessage")
    .addEventListener(
        "keypress",
        function(event) {

            if (event.key === "Enter") {
                sendMessage();
            }

        }
    );