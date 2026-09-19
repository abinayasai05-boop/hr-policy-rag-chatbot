const messages = document.getElementById("messages");
const questionInput = document.getElementById("question");
const sendButton = document.getElementById("sendButton");
const typing = document.getElementById("typing");


/* =========================================
   SEND MESSAGE
========================================= */

async function sendMessage() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addUserMessage(question);

    questionInput.value = "";

    questionInput.style.height = "auto";

    setLoading(true);

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.answer || "Server error"
            );

        }


        addBotMessage(data.answer);

    }

    catch (error) {

        console.error(error);

        addBotMessage(
            "Sorry, I couldn't connect to the HR Policy Assistant. Please try again."
        );

    }

    finally {

        setLoading(false);

    }
}


/* =========================================
   ADD USER MESSAGE
========================================= */

function addUserMessage(text) {

    const message = document.createElement("div");

    message.className = "message user-message";

    message.innerHTML = `

        <div class="avatar user-avatar">
            👤
        </div>

        <div class="message-content">

            <div class="sender">
                You
            </div>

            <div class="bubble">
                ${escapeHtml(text)}
            </div>

        </div>

    `;

    messages.appendChild(message);

    scrollToBottom();
}


/* =========================================
   ADD BOT MESSAGE
========================================= */

function addBotMessage(text) {

    const message = document.createElement("div");

    message.className = "message bot-message";

    message.innerHTML = `

        <div class="avatar bot-avatar">
            ✦
        </div>

        <div class="message-content">

            <div class="sender">
                HR Policy AI
            </div>

            <div class="bubble">
                ${formatAnswer(text)}
            </div>

        </div>

    `;

    messages.appendChild(message);

    scrollToBottom();
}


/* =========================================
   FORMAT BOT ANSWER
========================================= */

function formatAnswer(text) {

    return escapeHtml(text)
        .replace(/\n/g, "<br>");
}


/* =========================================
   ASK SUGGESTED QUESTION
========================================= */

function askQuestion(question) {

    questionInput.value = question;

    sendMessage();

}


/* =========================================
   LOADING
========================================= */

function setLoading(isLoading) {

    if (isLoading) {

        typing.style.display = "flex";

        sendButton.disabled = true;

    }

    else {

        typing.style.display = "none";

        sendButton.disabled = false;

    }

    scrollToBottom();
}


/* =========================================
   ENTER KEY
========================================= */

function handleKey(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();

    }
}


/* =========================================
   CLEAR CHAT
========================================= */

function clearChat() {

    messages.innerHTML = `

        <div class="message bot-message">

            <div class="avatar bot-avatar">
                ✦
            </div>

            <div class="message-content">

                <div class="sender">
                    HR Policy AI
                </div>

                <div class="bubble">

                    Hello! 👋<br><br>

                    I'm your HR Policy Assistant.
                    Ask me anything about the HR policies.

                </div>

            </div>

        </div>

    `;

}


/* =========================================
   SCROLL
========================================= */

function scrollToBottom() {

    messages.scrollTop = messages.scrollHeight;

}


/* =========================================
   SECURITY
========================================= */

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}


/* =========================================
   TEXTAREA AUTO RESIZE
========================================= */

questionInput.addEventListener(
    "input",
    function () {

        this.style.height = "auto";

        this.style.height =
            Math.min(this.scrollHeight, 100) + "px";

    }
);