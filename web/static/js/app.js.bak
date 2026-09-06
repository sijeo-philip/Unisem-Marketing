"use strict";


const wizardState = {

    engineAnswers: [],

    displayAnswers: [],

    currentQuestion: null
};


document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);


/* ========================================================
   APPLICATION STARTUP
   ======================================================== */

async function initializeApplication() {

    await checkBackend();

    configureButtons();
}


/* ========================================================
   HEALTH CHECK
   ======================================================== */

async function checkBackend() {

    const backendStatus =
        document.getElementById(
            "backendStatus"
        );

    const moduleStatus =
        document.getElementById(
            "moduleStatus"
        );

    const questionTreeStatus =
        document.getElementById(
            "questionTreeStatus"
        );


    try {

        const response =
            await fetch(
                "/api/health"
            );


        if (!response.ok) {
            throw new Error(
                "Health API failed"
            );
        }


        const data =
            await response.json();


        if (data.status === "ok") {

            setSuccess(
                backendStatus,
                "Connected"
            );

        } else {

            setError(
                backendStatus,
                "Error"
            );
        }


        if (data.modules_database) {

            setSuccess(
                moduleStatus,
                "Available"
            );

        } else {

            setError(
                moduleStatus,
                "Not Found"
            );
        }


        if (data.question_tree) {

            setSuccess(
                questionTreeStatus,
                "Available"
            );

        } else {

            setError(
                questionTreeStatus,
                "Not Found"
            );
        }

    }

    catch (error) {

        console.error(
            error
        );


        setError(
            backendStatus,
            "Disconnected"
        );


        setError(
            moduleStatus,
            "Unknown"
        );


        setError(
            questionTreeStatus,
            "Unknown"
        );
    }
}


function setSuccess(
    element,
    message
) {

    element.textContent =
        message;

    element.classList.remove(
        "pending",
        "error"
    );
}


function setError(
    element,
    message
) {

    element.textContent =
        message;

    element.classList.remove(
        "pending"
    );

    element.classList.add(
        "error"
    );
}


/* ========================================================
   START BUTTON
   ======================================================== */

function configureButtons() {

    document
        .getElementById(
            "startWizardButton"
        )
        .addEventListener(
            "click",
            startWizard
        );
}


async function startWizard() {

    wizardState.engineAnswers =
        [];

    wizardState.displayAnswers =
        [];

    wizardState.currentQuestion =
        null;


    hideWizardError();


    document
        .getElementById(
            "wizardComplete"
        )
        .classList
        .add(
            "hidden"
        );


    document
        .getElementById(
            "questionArea"
        )
        .classList
        .remove(
            "hidden"
        );


    document
        .getElementById(
            "wizardPanel"
        )
        .classList
        .remove(
            "hidden"
        );


    await requestWizardState();


    document
        .getElementById(
            "wizardPanel"
        )
        .scrollIntoView(
            {
                behavior: "smooth"
            }
        );
}


/* ========================================================
   COMMUNICATE WITH QUESTIONSESSION
   ======================================================== */

async function requestWizardState() {

    hideWizardError();


    document.getElementById(
        "progressText"
    ).textContent =
        "Evaluating...";


    try {

        const response =
            await fetch(
                "/api/wizard",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                answers:
                                    wizardState
                                        .engineAnswers
                            }
                        )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                (
                    "Wizard API returned HTTP " +
                    response.status
                )
            );
        }


        if (data.status !== "ok") {

            throw new Error(
                data.error ||
                "Recommendation engine error"
            );
        }


        if (
            data.state ===
            "question"
        ) {

            renderQuestion(
                data.question,
                data.step
            );

            return;
        }


        if (
            data.state ===
            "complete"
        ) {

            completeWizard(
                data
            );

            return;
        }


        throw new Error(
            "Unknown wizard state"
        );

    }

    catch (error) {

        console.error(
            "Wizard error:",
            error
        );


        showWizardError(
            error.message
        );
    }
}


/* ========================================================
   QUESTION RENDERING
   ======================================================== */

function renderQuestion(
    question,
    step
) {

    wizardState.currentQuestion =
        question;


    const questionArea =
        document.getElementById(
            "questionArea"
        );


    questionArea.classList.remove(
        "hidden"
    );


    document.getElementById(
        "questionId"
    ).textContent =
        "Requirement Question";


    document.getElementById(
        "questionText"
    ).textContent =
        question.text;


    document.getElementById(
        "progressText"
    ).textContent =
        "Question " + step;


    const container =
        document.getElementById(
            "optionsContainer"
        );


    const actions =
        document.getElementById(
            "questionActions"
        );


    container.replaceChildren();

    actions.replaceChildren();

    actions.classList.add(
        "hidden"
    );


    if (
        isMultipleChoice(
            question
        )
    ) {

        renderMultipleChoice(
            question,
            container,
            actions
        );

    } else {

        renderSingleChoice(
            question,
            container
        );
    }
}


function isMultipleChoice(
    question
) {

    const type =
        String(
            question.type || ""
        )
        .toLowerCase()
        .replaceAll(
            "-",
            "_"
        );


    return (
        type.includes(
            "multiple"
        )
        ||
        type.includes(
            "multi_select"
        )
    );
}


/* ========================================================
   SINGLE CHOICE
   ======================================================== */

function renderSingleChoice(
    question,
    container
) {

    for (
        const option
        of question.options
    ) {

        const button =
            document.createElement(
                "button"
            );


        button.type =
            "button";

        button.className =
            "option-button";

        button.textContent =
            option.label;


        button.addEventListener(
            "click",
            async function () {

                await submitAnswer(
                    option.value,
                    option.label
                );
            }
        );


        container.appendChild(
            button
        );
    }
}


/* ========================================================
   MULTIPLE CHOICE
   ======================================================== */

function renderMultipleChoice(
    question,
    container,
    actions
) {

    const selected =
        new Map();


    for (
        const option
        of question.options
    ) {

        const button =
            document.createElement(
                "button"
            );


        button.type =
            "button";

        button.className =
            "option-button";

        button.textContent =
            option.label;


        button.addEventListener(
            "click",
            function () {

                const key =
                    String(
                        option.value
                    );


                const isUnknown =
                    key
                    .toLowerCase()
                    === "unknown";


                if (isUnknown) {

                    selected.clear();


                    for (
                        const child
                        of container.children
                    ) {

                        child.classList.remove(
                            "selected"
                        );
                    }
                }


                if (
                    !isUnknown
                    &&
                    selected.has(
                        "unknown"
                    )
                ) {

                    selected.delete(
                        "unknown"
                    );


                    for (
                        const child
                        of container.children
                    ) {

                        if (
                            child.dataset.value
                            === "unknown"
                        ) {

                            child.classList.remove(
                                "selected"
                            );
                        }
                    }
                }


                if (
                    selected.has(
                        key
                    )
                ) {

                    selected.delete(
                        key
                    );

                    button.classList.remove(
                        "selected"
                    );

                } else {

                    selected.set(
                        key,
                        option
                    );

                    button.classList.add(
                        "selected"
                    );
                }


                continueButton.disabled =
                    selected.size === 0;
            }
        );


        button.dataset.value =
            String(
                option.value
            );


        container.appendChild(
            button
        );
    }


    const continueButton =
        document.createElement(
            "button"
        );


    continueButton.type =
        "button";

    continueButton.className =
        "continue-button";

    continueButton.textContent =
        "Continue";

    continueButton.disabled =
        true;


    continueButton.addEventListener(
        "click",
        async function () {

            const options =
                Array.from(
                    selected.values()
                );


            const values =
                options.map(
                    option =>
                        option.value
                );


            const labels =
                options.map(
                    option =>
                        option.label
                );


            await submitAnswer(
                values,
                labels.join(", ")
            );
        }
    );


    actions.appendChild(
        continueButton
    );


    actions.classList.remove(
        "hidden"
    );
}


/* ========================================================
   SUBMIT ANSWER
   ======================================================== */

async function submitAnswer(
    engineValue,
    displayLabel
) {

    const question =
        wizardState.currentQuestion;


    wizardState.engineAnswers.push(
        engineValue
    );


    wizardState.displayAnswers.push(
        {
            question:
                question.text,

            label:
                displayLabel
        }
    );


    await requestWizardState();
}


/* ========================================================
   COMPLETION
   ======================================================== */

function completeWizard(
    data
) {

    document
        .getElementById(
            "questionArea"
        )
        .classList
        .add(
            "hidden"
        );


    document
        .getElementById(
            "wizardComplete"
        )
        .classList
        .remove(
            "hidden"
        );


    document.getElementById(
        "progressText"
    ).textContent =
        "Evaluation complete";


    renderAnswerSummary();

    renderRecommendation(
        data
    );
}


function renderAnswerSummary() {

    const container =
        document.getElementById(
            "answerSummary"
        );


    container.replaceChildren();


    for (
        const answer
        of wizardState.displayAnswers
    ) {

        const row =
            document.createElement(
                "div"
            );


        row.className =
            "answer-row";


        const question =
            document.createElement(
                "div"
            );


        question.className =
            "answer-question";

        question.textContent =
            answer.question;


        const value =
            document.createElement(
                "div"
            );


        value.className =
            "answer-value";

        value.textContent =
            answer.label;


        row.append(
            question,
            value
        );


        container.appendChild(
            row
        );
    }
}


/* ========================================================
   RECOMMENDATION DISPLAY
   ======================================================== */

function renderRecommendation(
    data
) {

    const panel =
        document.getElementById(
            "recommendationPanel"
        );


    panel.classList.remove(
        "hidden"
    );


    const badge =
        document.getElementById(
            "decisionBadge"
        );


    const moduleElement =
        document.getElementById(
            "recommendedModule"
        );


    const nameElement =
        document.getElementById(
            "recommendedModuleName"
        );


    const chooseWhenElement =
        document.getElementById(
            "chooseWhen"
        );


    const details =
        document.getElementById(
            "recommendationDetails"
        );


    details.replaceChildren();


    const candidate =
        data.recommendation
        ||
        data.top_candidate;


    badge.className =
        "decision-badge";


    if (
        data.decision ===
        "recommended"
    ) {

        badge.textContent =
            "Compatible";

        badge.classList.add(
            "compatible"
        );


    } else if (
        data.decision ===
        "clarification_required"
    ) {

        badge.textContent =
            "Needs Clarification";

        badge.classList.add(
            "clarification"
        );


    } else {

        badge.textContent =
            "No Suitable Module";

        badge.classList.add(
            "not-suitable"
        );
    }


    if (!candidate) {

        moduleElement.textContent =
            "No module available";

        nameElement.textContent =
            "";

        chooseWhenElement.textContent =
            "";

        return;
    }


    moduleElement.textContent =
        candidate.module_id
        || "Candidate Module";


    nameElement.textContent =
        candidate.module_name
        || "";


    chooseWhenElement.textContent =
        candidate.choose_when
        || "";


    addDetailSection(
        details,
        "Clarifications",
        candidate.clarifications
    );


    addDetailSection(
        details,
        "Requirements satisfied",
        candidate.passed_requirements
    );


    addDetailSection(
        details,
        "Conflicts",
        candidate.hard_failures
    );


    addDetailSection(
        details,
        "Preference notes",
        candidate.preference_notes
    );
}


function addDetailSection(
    parent,
    title,
    items
) {

    if (
        !Array.isArray(
            items
        )
        ||
        items.length === 0
    ) {

        return;
    }


    const section =
        document.createElement(
            "div"
        );


    section.className =
        "detail-section";


    const heading =
        document.createElement(
            "h4"
        );


    heading.textContent =
        title;


    const list =
        document.createElement(
            "ul"
        );


    for (
        const item
        of items
    ) {

        const listItem =
            document.createElement(
                "li"
            );


        listItem.textContent =
            String(
                item
            );


        list.appendChild(
            listItem
        );
    }


    section.append(
        heading,
        list
    );


    parent.appendChild(
        section
    );
}


/* ========================================================
   ERRORS
   ======================================================== */

function showWizardError(
    message
) {

    const element =
        document.getElementById(
            "wizardError"
        );


    element.textContent =
        message;


    element.classList.remove(
        "hidden"
    );


    document.getElementById(
        "progressText"
    ).textContent =
        "Engine error";
}


function hideWizardError() {

    const element =
        document.getElementById(
            "wizardError"
        );


    element.textContent =
        "";


    element.classList.add(
        "hidden"
    );
}