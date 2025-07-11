"use strict";
var KTAppCalendar = function() {
    var e, t, n, a, o, r, i, l, d, c, s, m, u, v, f, p, y, D, k, _, b, g, S, h, T, Y, w, x, L, E = {
        id: "",
        eventName: "",
        eventDescription: "",
        eventLocation: "",
        startDate: "",
        endDate: "",
        allDay: !1
    };
    const M = () => {
            v.innerText = "Add a New Event", u.show();
            const o = f.querySelectorAll('[data-kt-calendar="datepicker"]'),
                i = f.querySelector("#kt_calendar_datepicker_allday");
            i.addEventListener("click", (e => {
                e.target.checked ? o.forEach((e => {
                    e.classList.add("d-none")
                })) : (l.setDate(E.startDate, !0, "Y-m-d"), o.forEach((e => {
                    e.classList.remove("d-none")
                })))
            })), C(E), 
            D.addEventListener("click", function(o) {
                o.preventDefault();
                p && p.validate().then(function(o) {
                    if ("Valid" == o) {
                        D.setAttribute("data-kt-indicator", "on");
                        D.disabled = !0;
                        setTimeout(function() {
                            D.removeAttribute("data-kt-indicator");
                            let allDay = i.checked;
                            let startDate = moment(r.selectedDates[0]).format();
                            let endDate = moment(l.selectedDates[l.selectedDates.length - 1]).format();
            
                            if (!allDay) {
                                const startDateFormat = moment(r.selectedDates[0]).format("YYYY-MM-DD");
                                const endDateFormat = startDateFormat;
                                startDate = startDateFormat + "T" + moment(c.selectedDates[0]).format("HH:mm:ss");
                                endDate = endDateFormat + "T" + moment(m.selectedDates[0]).format("HH:mm:ss");
                            }
            
                            $.ajax({
                                url: '/api/events/create/',
                                method: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({
                                    title: t.value,
                                    description: n.value,
                                    location: a.value,
                                    start: startDate,
                                    end: endDate,
                                    all_day: allDay
                                }),
                                success: function(response) {
                                    Swal.fire({
                                        text: "New event added to calendar!",
                                        icon: "success",
                                        buttonsStyling: !1,
                                        confirmButtonText: "Ok, got it!",
                                        customClass: {
                                            confirmButton: "btn btn-primary"
                                        }
                                    }).then(function(o) {
                                        if (o.isConfirmed) {
                                            u.hide();
                                            D.disabled = !1;
                                            e.addEvent({
                                                id: response.id,
                                                title: t.value,
                                                description: n.value,
                                                location: a.value,
                                                start: startDate,
                                                end: endDate,
                                                allDay: allDay
                                            });
                                            e.render();
                                            f.reset();
                                        }
                                    });
                                },
                                error: function() {
                                    Swal.fire({
                                        text: "There was an error adding the event. Please try again.",
                                        icon: "error",
                                        buttonsStyling: !1,
                                        confirmButtonText: "Ok, got it!",
                                        customClass: {
                                            confirmButton: "btn btn-primary"
                                        }
                                    });
                                    D.disabled = !1;
                                }
                            });
                        }, 2e3);
                    } else {
                        Swal.fire({
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            icon: "error",
                            buttonsStyling: !1,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn btn-primary"
                            }
                        });
                    }
                });
            });
            
        },
        B = () => {
            var e, t, n;
            w.show(), 
            E.allDay ? (e = "All Day", t = moment(E.startDate).format("Do MMM, YYYY"), 
            n = moment(E.endDate).format("Do MMM, YYYY")) : (e = "", t = moment(E.startDate).format("Do MMM, YYYY - h:mm a"), 
            n = moment(E.endDate).format("Do MMM, YYYY - h:mm a")), 
            b.innerText = E.eventName, g.innerText = e, 
            S.innerText = E.eventDescription ? E.eventDescription : "--", 
            h.innerText = E.eventLocation ? E.eventLocation : "--", 
            T.innerText = t, Y.innerText = n
        },
        q = () => {
            x.addEventListener("click", (o => {
                o.preventDefault(), w.hide(), (() => {
                    v.innerText = "Edit an Event", u.show();
                    const o = f.querySelectorAll('[data-kt-calendar="datepicker"]'),
                        i = f.querySelector("#kt_calendar_datepicker_allday");
                    i.addEventListener("click", (e => {
                        e.target.checked ? o.forEach((e => {
                            e.classList.add("d-none")
                        })) : (l.setDate(E.startDate, !0, "Y-m-d"), o.forEach((e => {
                            e.classList.remove("d-none")
                        })))
                    })), C(E), 
                    D.addEventListener("click", function(o) {
                        o.preventDefault();
                        p && p.validate().then(function(o) {
                            if ("Valid" == o) {
                                D.setAttribute("data-kt-indicator", "on");
                                D.disabled = !0;
                                setTimeout(function() {
                                    D.removeAttribute("data-kt-indicator");
                                    let allDay = i.checked;
                                    let startDate = moment(r.selectedDates[0]).format();
                                    let endDate = moment(l.selectedDates[l.selectedDates.length - 1]).format();
                    
                                    if (!allDay) {
                                        const startDateFormat = moment(r.selectedDates[0]).format("YYYY-MM-DD");
                                        const endDateFormat = startDateFormat;
                                        startDate = startDateFormat + "T" + moment(c.selectedDates[0]).format("HH:mm:ss");
                                        endDate = endDateFormat + "T" + moment(m.selectedDates[0]).format("HH:mm:ss");
                                    }
                    
                                    $.ajax({
                                        url: '/api/events/update/' + E.id + '/',
                                        method: 'PUT',
                                        contentType: 'application/json',
                                        data: JSON.stringify({
                                            title: t.value,
                                            description: n.value,
                                            location: a.value,
                                            start: startDate,
                                            end: endDate,
                                            all_day: allDay
                                        }),
                                        success: function() {
                                            e.getEventById(E.id).remove();
                                            e.addEvent({
                                                id: E.id,
                                                title: t.value,
                                                description: n.value,
                                                location: a.value,
                                                start: startDate,
                                                end: endDate,
                                                allDay: allDay
                                            });
                                            e.render();
                                            f.reset();
                                            Swal.fire({
                                                text: "Event updated successfully!",
                                                icon: "success",
                                                buttonsStyling: !1,
                                                confirmButtonText: "Ok, got it!",
                                                customClass: {
                                                    confirmButton: "btn btn-primary"
                                                }
                                            }).then(function(o) {
                                                if (o.isConfirmed) {
                                                    u.hide();
                                                    D.disabled = !1;
                                                }
                                            });
                                        },
                                        error: function() {
                                            Swal.fire({
                                                text: "There was an error updating the event. Please try again.",
                                                icon: "error",
                                                buttonsStyling: !1,
                                                confirmButtonText: "Ok, got it!",
                                                customClass: {
                                                    confirmButton: "btn btn-primary"
                                                }
                                            });
                                            D.disabled = !1;
                                        }
                                    });
                                }, 2e3);
                            } else {
                                Swal.fire({
                                    text: "Sorry, looks like there are some errors detected, please try again.",
                                    icon: "error",
                                    buttonsStyling: !1,
                                    confirmButtonText: "Ok, got it!",
                                    customClass: {
                                        confirmButton: "btn btn-primary"
                                    }
                                });
                            }
                        });
                    });                    
                })()
            }))
        },
        C = () => {
            t.value = E.eventName ? E.eventName : "", n.value = E.eventDescription ? E.eventDescription : "", a.value = E.eventLocation ? E.eventLocation : "", r.setDate(E.startDate, !0, "Y-m-d");
            const e = E.endDate ? E.endDate : moment(E.startDate).format();
            l.setDate(e, !0, "Y-m-d");
            const o = f.querySelector("#kt_calendar_datepicker_allday"),
                i = f.querySelectorAll('[data-kt-calendar="datepicker"]');
            E.allDay ? (o.checked = !0, i.forEach((e => {
                e.classList.add("d-none")
            }))) : (c.setDate(E.startDate, !0, "Y-m-d H:i"), m.setDate(E.endDate, !0, "Y-m-d H:i"), l.setDate(E.startDate, !0, "Y-m-d"), o.checked = !1, i.forEach((e => {
                e.classList.remove("d-none")
            })))
        },
        N = e => {
            E.id = e.id, E.eventName = e.title, E.eventDescription = e.description, E.eventLocation = e.location, E.startDate = e.startStr, E.endDate = e.endStr, E.allDay = e.allDay
        },
        A = () => Date.now().toString() + Math.floor(1e3 * Math.random()).toString();
    return {
        init: function() {
            if (e) {
                e.destroy();
            }
            const C = document.getElementById("kt_modal_add_event");
            f = C.querySelector("#kt_modal_add_event_form"), 
            t = f.querySelector('[name="calendar_event_name"]'), 
            n = f.querySelector('[name="calendar_event_description"]'), 
            a = f.querySelector('[name="calendar_event_location"]'), 
            o = f.querySelector("#kt_calendar_datepicker_start_date"), 
            i = f.querySelector("#kt_calendar_datepicker_end_date"), 
            d = f.querySelector("#kt_calendar_datepicker_start_time"), 
            s = f.querySelector("#kt_calendar_datepicker_end_time"), 
            y = document.querySelector('[data-kt-calendar="add"]'), 
            D = f.querySelector("#kt_modal_add_event_submit"), 
            k = f.querySelector("#kt_modal_add_event_cancel"), 
            _ = C.querySelector("#kt_modal_add_event_close"), 
            v = f.querySelector('[data-kt-calendar="title"]'), 
            u = new bootstrap.Modal(C);
            const H = document.getElementById("kt_modal_view_event");
            var F, O, I, R, V, P;
            w = new bootstrap.Modal(H), 
            b = H.querySelector('[data-kt-calendar="event_name"]'), 
            g = H.querySelector('[data-kt-calendar="all_day"]'), 
            S = H.querySelector('[data-kt-calendar="event_description"]'), 
            h = H.querySelector('[data-kt-calendar="event_location"]'), 
            T = H.querySelector('[data-kt-calendar="event_start_date"]'), 
            Y = H.querySelector('[data-kt-calendar="event_end_date"]'), 
            x = H.querySelector("#kt_modal_view_event_edit"), 
            L = H.querySelector("#kt_modal_view_event_delete"), 
            F = document.getElementById("kt_calendar_app"), 
            O = moment().startOf("day"), 
            I = O.format("YYYY-MM"), 
            R = O.clone().subtract(1, "day").format("YYYY-MM-DD"), 
            V = O.format("YYYY-MM-DD"), 
            P = O.clone().add(1, "day").format("YYYY-MM-DD"), 
            
            (e = new FullCalendar.Calendar(F, {
                headerToolbar: {
                    left: "prev,next today",
                    center: "title",
                    right: "dayGridMonth,timeGridWeek,timeGridDay"
                },
                initialDate: V,
                navLinks: !0,
                selectable: !0,
                selectMirror: !0,
                select: function(e) {
                    N(e), M()
                },
                eventClick: function(e) {
                    N({
                        id: e.event.id,
                        title: e.event.title,
                        description: e.event.extendedProps.description,
                        location: e.event.extendedProps.location,
                        startStr: e.event.startStr,
                        endStr: e.event.endStr,
                        allDay: e.event.allDay
                    }), B()
                },
                editable: !0,
                dayMaxEvents: !0,
                events: function(info, successCallback, failureCallback) {
                    // e.removeAllEvents(); // Clear any existing events
                    $.ajax({
                        url: '/api/events/',
                        method: 'GET',
                        success: function(data) {
                            successCallback(data);
                        },
                        error: function() {
                            failureCallback();
                        }
                    });
                },
                datesSet: function() {}
            })).render(), p = FormValidation.formValidation(f, {
                fields: {
                    calendar_event_name: {
                        validators: {
                            notEmpty: {
                                message: "Event name is required"
                            }
                        }
                    },
                    calendar_event_start_date: {
                        validators: {
                            notEmpty: {
                                message: "Start date is required"
                            }
                        }
                    },
                    calendar_event_end_date: {
                        validators: {
                            notEmpty: {
                                message: "End date is required"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            }), r = flatpickr(o, {
                enableTime: !1,
                dateFormat: "Y-m-d"
            }), l = flatpickr(i, {
                enableTime: !1,
                dateFormat: "Y-m-d"
            }), c = flatpickr(d, {
                enableTime: !0,
                noCalendar: !0,
                dateFormat: "H:i"
            }), m = flatpickr(s, {
                enableTime: !0,
                noCalendar: !0,
                dateFormat: "H:i"
            }), q(), y.addEventListener("click", (e => {
                E = {
                    id: "",
                    eventName: "",
                    eventDescription: "",
                    startDate: new Date,
                    endDate: new Date,
                    allDay: !1
                }, M()
            })), 
            // Delete
            L.addEventListener("click", function(t) {
                t.preventDefault();
                Swal.fire({
                    text: "Are you sure you would like to delete this event?",
                    icon: "warning",
                    showCancelButton: !0,
                    buttonsStyling: !1,
                    confirmButtonText: "Yes, delete it!",
                    cancelButtonText: "No, return",
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-active-light"
                    }
                }).then(function(t) {
                    if (t.value) {
                        $.ajax({
                            url: '/api/events/delete/' + E.id + '/',
                            method: 'DELETE',
                            success: function() {
                                e.getEventById(E.id).remove();
                                w.hide();
                                Swal.fire({
                                    text: "Your event has been deleted!.",
                                    icon: "success",
                                    buttonsStyling: !1,
                                    confirmButtonText: "Ok, got it!",
                                    customClass: {
                                        confirmButton: "btn btn-primary"
                                    }
                                });
                            },
                            error: function() {
                                Swal.fire({
                                    text: "There was an error deleting the event. Please try again.",
                                    icon: "error",
                                    buttonsStyling: !1,
                                    confirmButtonText: "Ok, got it!",
                                    customClass: {
                                        confirmButton: "btn btn-primary"
                                    }
                                });
                            }
                        });
                    } else if ("cancel" === t.dismiss) {
                        Swal.fire({
                            text: "Your event was not deleted!.",
                            icon: "error",
                            buttonsStyling: !1,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn btn-primary"
                            }
                        });
                    }
                });
            });
             
            k.addEventListener("click", (function(e) {
                e.preventDefault(), Swal.fire({
                    text: "Are you sure you would like to cancel?",
                    icon: "warning",
                    showCancelButton: !0,
                    buttonsStyling: !1,
                    confirmButtonText: "Yes, cancel it!",
                    cancelButtonText: "No, return",
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-active-light"
                    }
                }).then((function(e) {
                    e.value ? (f.reset(), u.hide()) : "cancel" === e.dismiss && Swal.fire({
                        text: "Your form has not been cancelled!.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn btn-primary"
                        }
                    })
                }))
            })), _.addEventListener("click", (function(e) {
                e.preventDefault(), Swal.fire({
                    text: "Are you sure you would like to cancel?",
                    icon: "warning",
                    showCancelButton: !0,
                    buttonsStyling: !1,
                    confirmButtonText: "Yes, cancel it!",
                    cancelButtonText: "No, return",
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-active-light"
                    }
                }).then((function(e) {
                    e.value ? (f.reset(), u.hide()) : "cancel" === e.dismiss && Swal.fire({
                        text: "Your form has not been cancelled!.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Ok, got it!",
                        customClass: {
                            confirmButton: "btn btn-primary"
                        }
                    })
                }))
            })), (e => {
                e.addEventListener("hidden.bs.modal", (e => {
                    p && p.resetForm(!0)
                }))
            })(C)
        }
    }
}();
KTUtil.onDOMContentLoaded((function() {
    KTAppCalendar.init()
}));