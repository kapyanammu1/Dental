"use strict";

var NotifModalForm = function() {
    var 
    submitButton, 
    cancelButton, 
    closeButton, 
    formValidation, 
    modalInstance, 
    formElement;

    return {
        init: function(modalName, formName) {
            modalInstance = new bootstrap.Modal(document.querySelector(`#${modalName}`)); // Initialize modal
            formElement = document.querySelector(`#${formName}`); // Get form element
            submitButton = formElement.querySelector("#btn-notif-submit"); // Submit button
            cancelButton = formElement.querySelector("#btn-notif-cancel"); // Cancel button
            closeButton = formElement.querySelector("#btn-close"); // Close button

            formValidation = FormValidation.formValidation(formElement, {
                fields: {
                    first_name: {
                        validators: {
                            notEmpty: {
                                message: "First name is required"
                            }
                        }
                    },
                    last_name: {
                        validators: {
                            notEmpty: {
                                message: "Last name is required"
                            }
                        }
                    },
                    email: {
                        validators: {
                            notEmpty: {
                                message: "Email is required"
                            }
                        }
                    },
                    date_of_birth: {
                        validators: {
                            notEmpty: {
                                message: "Birthdate is required"
                            }
                        }
                    },
                    contact_number: {
                        validators: {
                            notEmpty: {
                                message: "Contact number is required"
                            }
                        }
                    },
                    address: {
                        validators: {
                            notEmpty: {
                                message: "Address is required"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger(),
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            });

            // Submit button event listener
            submitButton.addEventListener("click", function(event) {
                event.preventDefault();

                if (formValidation) {
                    formValidation.validate().then(function(status) {
                        console.log("Validation completed!");

                        if (status === "Valid") {
                            Swal.fire({
                                text: "Form has been successfully submitted!",
                                icon: "success",
                                buttonsStyling: false,
                                confirmButtonText: "Ok, got it!",
                                customClass: {
                                    confirmButton: "btn btn-primary"
                                }
                            }).then(function(result) {
                                if (result.isConfirmed) {
                                    modalInstance.hide(); // Close the modal
                                    submitButton.disabled = false; // Re-enable submit button
                                    formElement.submit(); // Submit the form
                                }
                            });
                        } else {
                            Swal.fire({
                                text: "Sorry, looks like there are some required fields empty, please try again.",
                                icon: "error",
                                buttonsStyling: false,
                                confirmButtonText: "Ok, got it!",
                                customClass: {
                                    confirmButton: "btn btn-primary"
                                }
                            });
                        }
                    });
                }
            });

            // Cancel button event listener
            cancelButton.addEventListener("click", function(event) {
                event.preventDefault();

                Swal.fire({
                    text: "Are you sure you would like to cancel?",
                    icon: "warning",
                    showCancelButton: true,
                    buttonsStyling: false,
                    confirmButtonText: "Yes, cancel it!",
                    cancelButtonText: "No, return",
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-active-light"
                    }
                }).then(function(result) {
                    if (result.value) {
                        formElement.reset(); // Reset the form
                        modalInstance.hide(); // Hide the modal
                    } else if (result.dismiss === "cancel") {
                        Swal.fire({
                            text: "Your form has not been cancelled!",
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn btn-primary"
                            }
                        });
                    }
                });
            });

            // Close button event listener
            closeButton.addEventListener("click", function(event) {
                event.preventDefault();

                Swal.fire({
                    text: "Are you sure you would like to cancel?",
                    icon: "warning",
                    showCancelButton: true,
                    buttonsStyling: false,
                    confirmButtonText: "Yes, cancel it!",
                    cancelButtonText: "No, return",
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-active-light"
                    }
                }).then(function(result) {
                    if (result.value) {
                        formElement.reset(); // Reset the form
                        modalInstance.hide(); // Hide the modal
                    } else if (result.dismiss === "cancel") {
                        Swal.fire({
                            text: "Your form has not been cancelled!",
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn btn-primary"
                            }
                        });
                    }
                });
            });
        }
    };
}();

KTUtil.onDOMContentLoaded(function() {
    NotifModalForm.init("view_modal", "notif_form");
});
