"use strict";


/*
============================================================
LESSON 2B
Dynamic Sales Wizard
============================================================
*/


const wizardState = {

    tree: null,

    questionsById: new Map(),

    questionOrder: [],

    currentQuestionId: null,

    answers: []
};


document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);


/*
============================================================
APPLICATION STARTUP
============================================================
*/

async function initializeApplication() {

    await checkBackend();

    configureButtons();
}


/*
============================================================
BACKEND HEALTH CHECK
============================================================
*/

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
                "Backend returned HTTP " +
                response.status
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
            "Application initialization failed:",
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


/*
============================================================
STATUS HELPERS
============================================================
*/

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


/*
============================================================
BUTTON CONFIGURATION
============================================================
*/

function configureButtons() {

    const button =
        document.getElementById(
            "startWizardButton"
        );


    button.addEventListener(
        "click",
        startWizard
    );
}


/*
============================================================
LOAD QUESTION TREE
============================================================
*/

async function startWizard() {

    const button =
        document.getElementById(
            "startWizardButton"
        );


    const wizardPanel =
        document.getElementById(
            "wizardPanel"
        );


    hideWizardError();


    button.disabled = true;

    button.textContent =
        "Loading Sales Wizard...";


    try {

        const response =
            await fetch(
                "/api/question-tree"
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                (
                    "Unable to load question tree. " +
                    "HTTP " +
                    response.status
                )
            );
        }


        if (data.status !== "ok") {

            throw new Error(
                data.error ||
                "Question tree returned an error"
            );
        }


        initializeWizardState(
            data
        );


        wizardPanel.classList.remove(
            "hidden"
        );


        renderQuestion(
            wizardState.currentQuestionId
        );


        wizardPanel.scrollIntoView(
            {
                behavior: "smooth",
                block: "start"
            }
        );


        button.textContent =
            "Sales Wizard Running";

    }

    catch (error) {

        console.error(
            "Unable to start Sales Wizard:",
            error
        );


        wizardPanel.classList.remove(
            "hidden"
        );


        showWizardError(
            error.message
        );


        button.disabled = false;

        button.textContent =
            "Start Sales Wizard";
    }
}


/*
============================================================
INITIALIZE WIZARD STATE
============================================================
*/

function initializeWizardState(
    tree
) {

    if (!Array.isArray(
        tree.questions
    )) {

        throw new Error(
            "Question API did not return a question list"
        );
    }


    if (
        tree.questions.length === 0
    ) {

        throw new Error(
            "Question tree contains no questions"
        );
    }


    wizardState.tree =
        tree;


    wizardState.questionsById =
        new Map();


    wizardState.questionOrder =
        [];


    wizardState.answers =
        [];


    for (
        const question
        of tree.questions
    ) {

        const id =
            String(
                question.id
            );


        wizardState.questionsById.set(
            id,
            question
        );


        wizardState.questionOrder.push(
            id
        );
    }


    const startId =
        String(
            tree.start_question_id
        );


    if (
        !wizardState.questionsById.has(
            startId
        )
    ) {

        throw new Error(
            "Start question '" +
            startId +
            "' does not exist"
        );
    }


    wizardState.currentQuestionId =
        startId;


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
            "wizardComplete"
        )
        .classList
        .add(
            "hidden"
        );
}


/*
============================================================
RENDER QUESTION
============================================================
*/

function renderQuestion(
    questionId
) {

    const question =
        wizardState.questionsById.get(
            String(
                questionId
            )
        );


    if (!question) {

        completeWizard();

        return;
    }


    wizardState.currentQuestionId =
        String(
            questionId
        );


    const questionIdElement =
        document.getElementById(
            "questionId"
        );


    const questionTextElement =
        document.getElementById(
            "questionText"
        );


    const optionsContainer =
        document.getElementById(
            "optionsContainer"
        );


    questionIdElement.textContent =
        "Requirement Question";


    questionTextElement.textContent =
        question.text;


    optionsContainer.replaceChildren();


    updateProgress(
        question.id
    );


    if (
        !Array.isArray(
            question.options
        )
        ||
        question.options.length === 0
    ) {

        showWizardError(
            "Question '" +
            question.id +
            "' has no selectable options."
        );

        return;
    }


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

                selectOption(
                    question,
                    option
                );
            }
        );


        optionsContainer.appendChild(
            button
        );
    }
}


/*
============================================================
SELECT ANSWER
============================================================
*/

function selectOption(
    question,
    option
) {

    wizardState.answers.push(
        {
            question_id:
                question.id,

            question:
                question.text,

            value:
                option.value,

            label:
                option.label
        }
    );


    const nextQuestionId =
        option.next_question_id;


    /*
    --------------------------------------------------------
    No next question = questionnaire finished.
    --------------------------------------------------------
    */

    if (
        nextQuestionId === null
        ||
        nextQuestionId === undefined
        ||
        nextQuestionId === ""
    ) {

        completeWizard();

        return;
    }


    /*
    --------------------------------------------------------
    A next value may represent a terminal node such as:

        END
        COMPLETE
        RESULT
        recommendation

    If it does not correspond to another question, Lesson 2B
    treats it as questionnaire completion.

    Lesson 2C will let the Python decision engine own this
    behavior.
    --------------------------------------------------------
    */

    if (
        !wizardState.questionsById.has(
            String(
                nextQuestionId
            )
        )
    ) {

        completeWizard();

        return;
    }


    renderQuestion(
        String(
            nextQuestionId
        )
    );
}


/*
============================================================
PROGRESS INDICATOR
============================================================
*/

function updateProgress(
    questionId
) {

    const position =
        wizardState
            .questionOrder
            .indexOf(
                String(
                    questionId
                )
            );


    const progressElement =
        document.getElementById(
            "progressText"
        );


    if (position >= 0) {

        progressElement.textContent =
            "Question " +
            (position + 1) +
            " of " +
            wizardState.questionOrder.length;

    } else {

        progressElement.textContent =
            "Sales Wizard";
    }
}


/*
============================================================
QUESTIONNAIRE COMPLETE
============================================================
*/

function completeWizard() {

    const questionArea =
        document.getElementById(
            "questionArea"
        );


    const completeArea =
        document.getElementById(
            "wizardComplete"
        );


    questionArea.classList.add(
        "hidden"
    );


    completeArea.classList.remove(
        "hidden"
    );


    document.getElementById(
        "progressText"
    ).textContent =
        "Requirements captured";


    renderAnswerSummary();
}


/*
============================================================
ANSWER SUMMARY
============================================================
*/

function renderAnswerSummary() {

    const container =
        document.getElementById(
            "answerSummary"
        );


    container.replaceChildren();


    for (
        const answer
        of wizardState.answers
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


        row.appendChild(
            question
        );


        row.appendChild(
            value
        );


        container.appendChild(
            row
        );
    }
}


/*
============================================================
ERROR HANDLING
============================================================
*/

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