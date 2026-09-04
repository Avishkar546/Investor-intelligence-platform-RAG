import {
    askFinancialQuestion,
} from "./api.js";

import {
    state,
} from "./state.js";


/* =========================================================
   DOM
========================================================= */

const chatInput =
    document.getElementById(
        "chatInput"
    );

const sendButton =
    document.getElementById(
        "sendButton"
    );

const chatMessages =
    document.getElementById(
        "chatMessages"
    );

const chatCompany =
    document.getElementById(
        "chatCompany"
    );

const chatYear =
    document.getElementById(
        "chatYear"
    );


/* =========================================================
   INITIALIZE
========================================================= */

export function initializeChat() {

    sendButton.addEventListener(
        "click",
        sendMessage
    );


    chatInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }
        }
    );


    chatInput.addEventListener(
        "input",
        resizeInput
    );


    document
        .querySelectorAll(
            ".suggestions button"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        chatInput.value =
                            button.dataset.query;

                        resizeInput();

                        sendMessage();
                    }
                );
            }
        );
}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    if (
        state.isQuerying
    ) {

        return;
    }


    const question =
        chatInput.value.trim();


    if (!question) {

        return;
    }


    const company =
        chatCompany.value.trim() ||
        null;


    const year =
        chatYear.value.trim() ||
        null;


    /*
     * Add user message.
     */

    addMessage(
        question,
        "user"
    );


    chatInput.value =
        "";

    resizeInput();


    state.isQuerying =
        true;


    sendButton.disabled =
        true;


    const loading =
        addMessage(
            "Analyzing financial data...",
            "assistant",
            true
        );


    const startedAt =
        performance.now();


    try {

        const response =
            await askFinancialQuestion({

                question,

                company,

                year,
            });


        loading.remove();


        const answer =
            response?.answer ??
            response?.response ??
            "No answer was returned by the analyst.";


        addMessage(
            answer,
            "assistant"
        );


        /*
         * Current backend returns only answer,
         * but support query_type when it is added.
         */

        const queryType =
            response?.query_type ??
            response?.queryType ??
            "completed";


        document.getElementById(
            "queryType"
        ).textContent =
            queryType;


        console.debug(
            `Query completed in ${Math.round(
                performance.now() - startedAt
            )} ms`
        );


    } catch (error) {

        loading.remove();


        addMessage(
            `Unable to answer the question.\n\n${error.message}`,
            "assistant"
        );


        console.error(
            "Chat request failed:",
            error
        );


    } finally {

        state.isQuerying =
            false;


        sendButton.disabled =
            false;


        chatInput.focus();
    }
}


/* =========================================================
   ADD MESSAGE
========================================================= */

function addMessage(
    text,
    role,
    loading = false
) {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        `chat-message ${role}`;


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "chat-bubble";


    if (loading) {

        bubble.classList.add(
            "chat-loading"
        );
    }


    /*
     * textContent is intentional.
     *
     * Never inject LLM output using innerHTML.
     */

    bubble.textContent =
        text;


    wrapper.appendChild(
        bubble
    );


    chatMessages.appendChild(
        wrapper
    );


    /*
     * Only chat-messages scrolls.
     */

    requestAnimationFrame(
        () => {

            chatMessages.scrollTop =
                chatMessages.scrollHeight;
        }
    );


    return wrapper;
}


/* =========================================================
   TEXTAREA
========================================================= */

function resizeInput() {

    chatInput.style.height =
        "auto";


    chatInput.style.height =
        `${Math.min(
            chatInput.scrollHeight,
            100
        )}px`;
}