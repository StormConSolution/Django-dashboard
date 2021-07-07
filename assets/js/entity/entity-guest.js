import {openGuestModal, openGuestModalWithID} from "../guest/modal"
let createEntityModal = document.querySelector("#create-entity")

document.querySelector('#create-entity-button').addEventListener('click',()=>{
    openGuestModal()
})


document.querySelectorAll('[data-role="delete-entity"]').forEach((e) => {
    e.addEventListener("click", (e) => {
        openGuestModal()
    })
});

let testEntityButton = document.querySelector("#test-entity-button")
let testEntityModalLoading = document.querySelector("#test-entity-modal-loading")
let testEntityFirstRun = true;
let testEntityModal = document.querySelector("#test-entity-modal")
let testEntityAPIKeysSelect = document.querySelector("#test-entity-api-key-select")
testEntityButton.addEventListener("click", () => {
    openGuestModal()
});