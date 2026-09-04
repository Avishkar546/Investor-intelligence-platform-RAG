const API_BASE_URL = "http://localhost:8000";


/* =========================================================
   Generic HTTP client
========================================================= */

async function request(endpoint, options = {}) {

    let response;

    try {
        response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,

                headers: {
                    Accept: "application/json",

                    ...(options.body instanceof FormData
                        ? {}
                        : {
                            "Content-Type": "application/json",
                        }),

                    ...(options.headers || {}),
                },
            }
        );

    } catch (error) {

        throw new Error(
            "Unable to connect to backend."
        );
    }


    const contentType =
        response.headers.get("content-type") || "";


    let data;

    if (contentType.includes("application/json")) {

        data = await response.json();

    } else {

        data = await response.text();
    }


    if (!response.ok) {

        const message =
            typeof data === "object"
                ? (
                    data.detail ||
                    data.message ||
                    "Request failed."
                )
                : data;

        throw new Error(
            message ||
            `Request failed with status ${response.status}`
        );
    }


    return data;
}


/* =========================================================
   METRICS
========================================================= */

export async function fetchMetrics() {

    return request(
        "/metrics"
    );
}


/* =========================================================
   UPLOAD
========================================================= */

export async function uploadReport({
    file,
    company,
    year,
    onProgress,
}) {

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
        "company",
        company
    );

    formData.append(
        "fiscal_year",
        year
    );


    return new Promise(
        (resolve, reject) => {

            const xhr =
                new XMLHttpRequest();


            xhr.open(
                "POST",
                `${API_BASE_URL}/documents/upload`
            );


            xhr.setRequestHeader(
                "Accept",
                "application/json"
            );


            xhr.upload.onprogress =
                event => {

                    if (!event.lengthComputable) {
                        return;
                    }

                    const percent =
                        Math.round(
                            (event.loaded / event.total) * 100
                        );

                    onProgress?.(
                        percent
                    );
                };


            xhr.onload = () => {

                let data;

                try {

                    data =
                        JSON.parse(
                            xhr.responseText
                        );

                } catch {

                    data =
                        xhr.responseText;
                }


                if (
                    xhr.status >= 200 &&
                    xhr.status < 300
                ) {

                    resolve(data);

                    return;
                }


                reject(
                    new Error(
                        data?.detail ||
                        data?.message ||
                        "Upload failed."
                    )
                );
            };


            xhr.onerror = () => {

                reject(
                    new Error(
                        "Network error during upload."
                    )
                );
            };


            xhr.send(formData);
        }
    );
}


/* =========================================================
   CHAT
========================================================= */

export async function askFinancialQuestion({
    question,
    company,
    year,
}) {

    return request(
        "/query",
        {
            method: "POST",

            body: JSON.stringify({

                question,

                company:
                    company || null,

                fiscal_year:
                    year
                        ? Number(year)
                        : null,
            }),
        }
    );
}