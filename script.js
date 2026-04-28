async function sendMessage() {
  const input = document.getElementById("inputMessage");
  const chat = document.getElementById("chatBody");

  if (input.value.trim() === "") return;

  const userText = input.value;

  const userMsg = document.createElement("div");
  userMsg.classList.add("message", "user");
  userMsg.textContent = userText;
  chat.appendChild(userMsg);

  input.value = "";
  chat.scrollTop = chat.scrollHeight;

  try {
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userText })
    });

    const data = await response.json();

    
    const botMsg = document.createElement("div");
    botMsg.classList.add("message", "bot");
    botMsg.textContent = data.response;

    chat.appendChild(botMsg);
    chat.scrollTop = chat.scrollHeight;

  } catch (error) {
    
    const erroMsg = document.createElement("div");
    erroMsg.classList.add("message", "bot");
    erroMsg.textContent = "Erro ao conectar com o servidor";

    chat.appendChild(erroMsg);
  }
}