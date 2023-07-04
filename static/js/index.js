document.addEventListener("DOMContentLoaded", function() {
  var chatInput = document.querySelector(".chat-input input");
  var chatMessages = document.querySelector(".chat-messages");
  var banner = document.querySelector(".banner");

  var sendButton = document.querySelector(".chat-input button");
  sendButton.addEventListener("click", sendMessage);
  chatInput.addEventListener('keyup', (event)=>{
    if (event.keyCode === 13) { // Tombol "Enter" memiliki keyCode 13
      event.preventDefault(); // Mencegah perilaku default
      sendMessage(); // Memanggil fungsi sendMessage() ketika tombol "Enter" ditekan
    }
  })

  function sendMessage() {
    // Display chat-messages and hide banner
    chatMessages.style.display = "block";
    chatMessages.style.width = "95%";
    banner.style.display = "none";
    var message = chatInput.value.trim();
    var chatContainer = document.getElementById("chat-container");

    if (message !== "") {
      // Create a new message element
      let newMessage = document.createElement("p");
      newMessage.classList.add("user-message")
      // Kalo make username
      // newMessage.innerText = `${username}: ${message}`;
      // Kalo make You
      newMessage.innerText = `${message}`;
      chatMessages.appendChild(newMessage);

      let chatbotMessageElement = document.createElement("p");
      chatbotMessageElement.classList.add("chatbot-message");
      fetch("http://127.0.0.1:5000/chatbot", {
      method: "POST",
      body: JSON.stringify({
          chat:`${message}`
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    })
      .then((response) => response.json())
      .then((json) => {
        let botRespone = json["response"];
        chatbotMessageElement.innerHTML = `${botRespone}`;
        chatMessages.appendChild(chatbotMessageElement);
      });
    } 
    chatInput.value = "";
  }
});