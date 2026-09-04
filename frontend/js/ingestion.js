import {
    uploadReport,
} from "./api.js";

import {
    state,
} from "./state.js";

import {
    loadDashboard,
} from "./dashboard.js";


/* =========================================================
   DOM
========================================================= */

const dropzone =
    document.getElementById(
        "dropzone"
    );

const fileInput =
    document.getElementById(
        "fileInput"
    );

const companyInput =
    document.getElementById(
        "companyInput"
    );

const yearInput =
    document.getElementById(
        "yearInput"
    );

const uploadButton =
    document.getElementById(
        "uploadButton"
    );


/* =========================================================
   INITIALIZE
========================================================= */

export function initializeIngestion() {

    dropzone.addEventListener(
        "click",
        () => fileInput.click()
    );


    fileInput.addEventListener(
        "change",
        event => {

            const file =
                event.target.files?.[0];


            if (file) {

                setSelectedFile(
                    file
                );
            }
        }
    );


    dropzone.addEventListener(
        "dragover",
        event => {

            event.preventDefault();

            dropzone.classList.add(
                "dragover"
            );
        }
    );


    dropzone.addEventListener(
        "dragleave",
        () => {

            dropzone.classList.remove(
                "dragover"
            );
        }
    );


    dropzone.addEventListener(
        "drop",
        event => {

            event.preventDefault();

            dropzone.classList.remove(
                "dragover"
            );


            const file =
                event.dataTransfer.files?.[0];


            if (file) {

                setSelectedFile(
                    file
                );
            }
        }
    );


    uploadButton.addEventListener(
        "click",
        handleUpload
    );
}


/* =========================================================
   FILE VALIDATION
========================================================= */

function setSelectedFile(
    file
) {

    if (
        file.type !==
        "application/pdf"
    ) {

        showToast(
            "Invalid file",
            "Only PDF annual reports are supported.",
            "error"
        );

        return;
    }


    state.selectedFile =
        file;


    const title =
        dropzone.querySelector(
            "strong"
        );


    title.textContent =
        file.name;
}


/* =========================================================
   UPLOAD
========================================================= */

async function handleUpload() {

    const file =
        state.selectedFile;


    const company =
        companyInput.value.trim();


    const year =
        yearInput.value.trim();


    if (!file) {

        showToast(
            "Missing file",
            "Select a PDF annual report first.",
            "error"
        );

        return;
    }


    if (!company) {

        showToast(
            "Missing company",
            "Enter the company name.",
            "error"
        );

        companyInput.focus();

        return;
    }


    if (
        !year ||
        Number(year) < 1900 ||
        Number(year) > 2100
    ) {

        showToast(
            "Invalid fiscal year",
            "Enter a valid fiscal year.",
            "error"
        );

        yearInput.focus();

        return;
    }


    try {

        state.isUploading =
            true;


        setUploadState(
            true
        );


        updateProgress(
            0,
            "Uploading..."
        );


        await uploadReport({

            file,

            company,

            year,

            onProgress:
                percent => {

                    updateProgress(
                        percent,
                        percent >= 100
                            ? "Processing..."
                            : "Uploading..."
                    );
                },
        });


        updateProgress(
            100,
            "Complete"
        );


        showToast(
            "Report processed",
            `${company} FY ${year} was ingested successfully.`,
            "success"
        );


        /*
         * Refresh dashboard data from PostgreSQL.
         */

        await loadDashboard();


        resetForm();


    } catch (error) {

        console.error(
            "Ingestion failed:",
            error
        );


        updateProgress(
            0,
            "Failed"
        );


        showToast(
            "Ingestion failed",
            error.message,
            "error"
        );


    } finally {

        state.isUploading =
            false;


        setUploadState(
            false
        );
    }
}


/* =========================================================
   UI STATE
========================================================= */

function setUploadState(
    uploading
) {

    uploadButton.disabled =
        uploading;

    companyInput.disabled =
        uploading;

    yearInput.disabled =
        uploading;
}


function updateProgress(
    percent,
    status
) {

    const wrapper =
        document.getElementById(
            "uploadProgress"
        );


    const fill =
        document.getElementById(
            "progressFill"
        );


    const statusElement =
        document.getElementById(
            "progressStatus"
        );


    const percentElement =
        document.getElementById(
            "progressPercent"
        );


    wrapper.classList.remove(
        "hidden"
    );


    fill.style.width =
        `${percent}%`;


    statusElement.textContent =
        status;


    percentElement.textContent =
        `${percent}%`;
}


function resetForm() {

    state.selectedFile =
        null;


    fileInput.value =
        "";


    companyInput.value =
        "";


    yearInput.value =
        "";


    const title =
        dropzone.querySelector(
            "strong"
        );


    title.textContent =
        "Upload Annual Report";
}


/* =========================================================
   TOAST
========================================================= */

function showToast(
    title,
    message,
    type = "success"
) {

    const container =
        document.getElementById(
            "toastContainer"
        );


    const toast =
        document.createElement(
            "div"
        );


    toast.className =
        `toast ${type}`;


    toast.innerHTML = `

        <div class="toast-title">
            ${escapeHtml(title)}
        </div>

        <div class="toast-message">
            ${escapeHtml(message)}
        </div>
    `;


    container.appendChild(
        toast
    );


    setTimeout(
        () => toast.remove(),
        4500
    );
}


function escapeHtml(
    value
) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}