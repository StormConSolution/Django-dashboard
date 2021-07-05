let createEntityModal = document.querySelector("#create-entity")
document.querySelector('#create-entity-button').addEventListener('click',()=>{
    $('#create-entity').modal()
})

let createEntityButton = document.querySelector(
    "#create-entity-button"
);
let createEntityAPIKeysSelect = document.querySelector(
    "#create-entity-api-key-select"
);
let createEntityModalLoading = document.querySelector(
    "#create-entity-modal-loading"
);
let createEntityFirstRun = true;
createEntityButton.addEventListener("click", () => {
    if (createEntityFirstRun) {
        createEntityModalLoading.innerHTML = "Loading...";
        fetch("/api/user-api-keys/")
            .then((data) => data.json())
            .then((data) => {
                let firstAPIKey = true
                for (let APIKey of data["apikeys"]) {
                    let option = document.createElement("option");
                    option.innerHTML = APIKey;
                    option.value = APIKey;
                    if(firstAPIKey){
                        option.selected = firstAPIKey
                        firstAPIKey = false
                    }
                    createEntityAPIKeysSelect.append(option);
                }
                createEntityFirstRun = false;
                createEntityModalLoading.innerHTML = "";
            });
    }
});

