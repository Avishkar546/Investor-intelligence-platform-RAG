import {
    fetchMetrics,
} from "./api.js";

import {
    state,
} from "./state.js";


/* =========================================================
   DOM
========================================================= */

const companyGrid =
    document.getElementById(
        "companyGrid"
    );


/* =========================================================
   LOAD DASHBOARD
========================================================= */

export async function loadDashboard() {

    try {

        const response =
            await fetchMetrics();


        state.companies =
            normalizeMetrics(
                response
            );


        updateSummary();

        renderCompanies();


        /*
         * Automatically select the first
         * company when available.
         */

        if (
            state.companies.length > 0 &&
            !state.selectedCompany
        ) {

            const first =
                state.companies[0];


            await selectCompany(
                first.company,
                first.year
            );
        }


    } catch (error) {

        console.error(
            "Dashboard load failed:",
            error
        );


        showDashboardError(
            error.message
        );
    }
}


/* =========================================================
   NORMALIZE BACKEND RESPONSE
========================================================= */

function normalizeMetrics(
    data
) {

    if (
        !Array.isArray(data)
    ) {

        return [];
    }


    return data
        .map(row => ({

            company:
                row.company ??
                row.name ??
                "Unknown Company",

            year:
                row.year ??
                row.fiscal_year ??
                null,

            revenue:
                row.revenue ??
                null,

            net_income:
                row.net_income ??
                null,

            operating_income:
                row.operating_income ??
                null,

            cash_flow:
                row.cash_flow ??
                row.operating_cash_flow ??
                null,

            total_assets:
                row.total_assets ??
                null,

            total_liabilities:
                row.total_liabilities ??
                null,

            raw:
                row,

        }))

        .filter(
            row =>
                row.company &&
                row.year
        );
}


/* =========================================================
   SUMMARY
========================================================= */

function updateSummary() {

    const companies =
        state.companies;


    const uniqueCompanies =
        new Set(
            companies.map(
                item => item.company
            )
        );


    const years =
        companies
            .map(
                item => Number(item.year)
            )
            .filter(
                Number.isFinite
            );


    const latestYear =
        years.length
            ? Math.max(...years)
            : null;


    document.getElementById(
        "totalCompanies"
    ).textContent =
        uniqueCompanies.size;


    document.getElementById(
        "totalReports"
    ).textContent =
        companies.length;


    document.getElementById(
        "latestYear"
    ).textContent =
        latestYear ?? "—";


    document.getElementById(
        "companyCounter"
    ).textContent =
        uniqueCompanies.size;
}


/* =========================================================
   COMPANY CARDS
========================================================= */

export function renderCompanies() {

    companyGrid.innerHTML = "";


    const companies =
        state.companies.slice(
            0,
            6
        );


    companies.forEach(
        company => {

            companyGrid.appendChild(
                createCompanyCard(
                    company
                )
            );
        }
    );


    /*
     * Always keep six dashboard slots.
     */

    const remaining =
        Math.max(
            0,
            6 - companies.length
        );


    for (
        let index = 0;
        index < remaining;
        index++
    ) {

        companyGrid.appendChild(
            createUploadCard()
        );
    }
}


/* =========================================================
   COMPANY CARD
========================================================= */

function createCompanyCard(
    company
) {

    const card =
        document.createElement(
            "article"
        );


    card.className =
        "company-card";


    if (
        state.selectedCompany ===
        company.company &&
        Number(state.selectedYear) ===
        Number(company.year)
    ) {

        card.classList.add(
            "active"
        );
    }


    const initials =
        getInitials(
            company.company
        );


    card.innerHTML = `

        <div class="company-header">

            <div class="company-avatar">
                ${escapeHtml(initials)}
            </div>

            <div>

                <div class="company-name">
                    ${escapeHtml(
        company.company
    )}
                </div>

                <div class="company-year">
                    FY ${escapeHtml(
        company.year
    )}
                </div>

            </div>

        </div>


        <div class="company-revenue">
            ${escapeHtml(
        formatValue(
            company.revenue
        )
    )}
        </div>

        <div class="company-revenue-label">
            Revenue
        </div>
    `;


    card.addEventListener(
        "click",
        () => {

            selectCompany(
                company.company,
                company.year
            );
        }
    );


    return card;
}


/* =========================================================
   UPLOAD CARD
========================================================= */

function createUploadCard() {

    const card =
        document.createElement(
            "article"
        );


    card.className =
        "company-card add-card";


    card.innerHTML = `

        <div>

            <div class="add-icon">
                +
            </div>

            <div class="add-title">
                Upload Annual Report
            </div>

            <div class="add-description">
                Add company data
            </div>

        </div>
    `;


    card.addEventListener(
        "click",
        () => {

            document
                .getElementById(
                    "fileInput"
                )
                .click();

        }
    );


    return card;
}


/* =========================================================
   SELECT COMPANY
========================================================= */

export async function selectCompany(
    company,
    year
) {

    state.selectedCompany =
        company;

    state.selectedYear =
        year;


    renderCompanies();


    const row =
        state.companies.find(
            item =>
                item.company === company &&
                Number(item.year) ===
                Number(year)
        );


    renderSelectedCompany(
        row
    );


    /*
     * Keep chat context synchronized.
     */

    document.getElementById(
        "chatCompany"
    ).value =
        company;


    document.getElementById(
        "chatYear"
    ).value =
        year;
}


/* =========================================================
   SELECTED COMPANY
========================================================= */

function renderSelectedCompany(
    company
) {

    if (!company) {

        return;
    }


    document.getElementById(
        "selectedCompany"
    ).textContent =
        company.company;


    document.getElementById(
        "selectedCompanyYear"
    ).textContent =
        `Fiscal Year ${company.year}`;


    setMetric(
        "metricRevenue",
        company.revenue
    );


    setMetric(
        "metricNetIncome",
        company.net_income
    );


    setMetric(
        "metricOperatingIncome",
        company.operating_income
    );


    setMetric(
        "metricCashFlow",
        company.cash_flow
    );


    setMetric(
        "metricAssets",
        company.total_assets
    );


    setMetric(
        "metricLiabilities",
        company.total_liabilities
    );
}


/* =========================================================
   HELPERS
========================================================= */

function setMetric(
    id,
    value
) {

    document.getElementById(
        id
    ).textContent =
        formatValue(value);
}


function formatValue(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "—";
    }


    if (
        typeof value === "number"
    ) {

        return value.toLocaleString(
            "en-IN"
        );
    }


    return String(value);
}


function getInitials(
    name
) {

    return String(name)
        .trim()
        .split(/\s+/)
        .map(
            word =>
                word[0]
        )
        .join("")
        .slice(0, 2)
        .toUpperCase();
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


function showDashboardError(
    message
) {

    companyGrid.innerHTML = `

        <div
            class="company-card"
            style="grid-column: 1 / -1;"
        >

            <div class="company-name">
                Unable to load dashboard data
            </div>

            <div class="company-year">
                ${escapeHtml(message)}
            </div>

        </div>
    `;
}