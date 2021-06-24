let createAspectButton = document.querySelector(
    "#create-aspect-model"
);
let createAspectAPIKeysSelect = document.querySelector(
    "#create-aspect-model-api-key-select"
);
let createAspectModalLoading = document.querySelector(
    "#create-aspect-model-modal-loading"
);
let createAspectFirstRun = true;
createAspectButton.addEventListener("click", () => {
    if (createAspectFirstRun) {
        createAspectModalLoading.innerHTML = "Loading...";
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
                    createAspectAPIKeysSelect.append(option);
                }
                createAspectFirstRun = false;
                createAspectModalLoading.innerHTML = "";
            });
    }
});


// Test sentiment modal
let testAspectButton = document.querySelector(
    "#test-aspect-button"
);
let testAspectAPIKeysSelect = document.querySelector(
    "#test-aspect-api-key-select"
);
let testAspectModalLoading = document.querySelector(
    "#test-aspect-modal-loading"
);
let testAspectFirstRun = true;
testAspectButton.addEventListener("click", () => {
    if (testAspectFirstRun) {
        testAspectModalLoading.innerHTML = "Loading...";
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
                    testAspectAPIKeysSelect.append(option);
                }
                createAspectFirstRun = false;
                testAspectModalLoading.innerHTML = "";
            });
    }
});