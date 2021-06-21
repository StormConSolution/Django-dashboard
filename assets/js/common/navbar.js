let openCreateProjectModal = document.querySelector(
    "#open-create-project-modal"
);
let createProjectModal = document.querySelector("#createproject");
let createProjectAPIKeysSelect = document.querySelector(
    "#create-project-api-key-select"
);
let createProjectModalLoading = document.querySelector(
    "#create-project-modal-loading"
);
let firstRun = true;
openCreateProjectModal.addEventListener("click", () => {
    if (firstRun) {
        createProjectModalLoading.innerHTML = "Loading...";
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
                    createProjectAPIKeysSelect.append(option);
                }
                firstRun = false;
                createProjectModalLoading.innerHTML = "";
            });
    }
});
