"use strict";


document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);


async function initializeApplication() {

    await checkBackend();

    configureButtons();
}


async function checkBackend() {

    const backendStatus =
        document.getElementById("backendStatus");

    const moduleStatus =
        document.getElementById("moduleStatus");

    const questionTreeStatus =
        document.getElementById("questionTreeStatus");


    try {

        const response =
            await fetch("/api/health");


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


function setSuccess(element, message) {

    element.textContent = message;

    element.classList.remove(
        "pending",
        "error"
    );
}


function setError(element, message) {

    element.textContent = message;

    element.classList.remove(
        "pending"
    );

    element.classList.add(
        "error"
    );
}


function configureButtons() {

    const button =
        document.getElementById(
            "startWizardButton"
        );


    button.addEventListener(
        "click",
        function () {

            const message =
                document.getElementById(
                    "lessonMessage"
                );


            message.classList.remove(
                "hidden"
            );


            message.scrollIntoView(
                {
                    behavior: "smooth"
                }
            );
        }
    );
}