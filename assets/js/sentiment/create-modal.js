// Create sentiment modal
let createSentimentButton = document.querySelector(
    "#create-sentiment-button"
);
let createSentimentRuleAPIKeysSelect = document.querySelector(
    "#create-sentiment-rule-api-key-select"
);
let createSentimentRuleModalLoading = document.querySelector(
    "#create-sentiment-rule-modal-loading"
);
let firstRun = true;
createSentimentButton.addEventListener("click", () => {
    if (firstRun) {
        createSentimentRuleModalLoading.innerHTML = "Loading...";
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
                    createSentimentRuleAPIKeysSelect.append(option);
                }
                firstRun = false;
                createSentimentRuleModalLoading.innerHTML = "";
            });
    }
});


// Test sentiment modal
let testSentimentButton = document.querySelector(
    "#show-test-sentiment-modal"
);
let testSentimentAPIKeysSelect = document.querySelector(
    "#test-sentiment-api-key-select"
);
let testSentimentModalLoading = document.querySelector(
    "#test-sentiment-modal-loading"
);
let testSentimentFirstRun = true;
testSentimentButton.addEventListener("click", () => {
    console.log("test")
    if (testSentimentFirstRun) {
        testSentimentModalLoading.innerHTML = "Loading...";
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
                    testSentimentAPIKeysSelect.append(option);
                }
                testSentimentFirstRun = false;
                testSentimentModalLoading.innerHTML = "";
            });
    }
});