import {
    loadDashboard,
} from "./dashboard.js";

import {
    initializeIngestion,
} from "./ingestion.js";

import {
    initializeChat,
} from "./chat.js";


/* =========================================================
   APPLICATION BOOTSTRAP
========================================================= */

async function bootstrap() {

    try {

        initializeIngestion();

        initializeChat();


        await loadDashboard();


    } catch (error) {

        console.error(
            "Application initialization failed:",
            error
        );
    }
}


/* =========================================================
   START
========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        bootstrap
    );

} else {

    bootstrap();
}