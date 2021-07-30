let testEntityButton = document.querySelector("#test-entity-button")
let testEntityModalLoading = document.querySelector("#test-entity-modal-loading")
let testEntityModal = document.querySelector("#test-entity-modal")

testEntityButton.addEventListener("click", () => {
    $("#test-entity-modal").modal()
});

document.querySelector("#test-entity-form").addEventListener("submit", (e)=>{
    e.preventDefault()
    let text = document.querySelector("#test-entity-text").value
    let language = document.querySelector("#test-entity-language").value
    let apiKey = testEntityAPIKeysSelect.value
    let scoreDiv = document.querySelector("#test-entity-model-score")
    fetch(`${window.apiHostName}/v4/${apiKey}/entities.json`,{
        method:"POST",
        body: new URLSearchParams({
            text: text,
            lang: language,
        })
    }).then((resp)=>resp.json())
    .then(resp=>{
        scoreDiv.innerHTML = ""
        tableHTML=
            `
            <div class="row">
                <div class="col-12 prject-card">
                    <div class="prject-card-inner">
                        <div class="data-table table-responsive">
                            <table class="mb-5 table table-striped table-borderless">
                                <thead>
                                    <tr>
                                        <th>Entity</th>
                                        <th>Classifications</th>
                                    </tr>
                                </thead>
                                <tbody id="entity-test-body-table">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            `
                scoreDiv.innerHTML = tableHTML
                let tableBody = document.querySelector("#entity-test-body-table")
                
                for(let element of resp.entities){
                    let classifications = []
                    for(let classification of element["classifications"]){
                        classifications.push(classification)
                    }
                    let row = document.createElement("tr")
                    row.innerHTML = 
                    `
                    <td>${element.title}</td>
                    <td>${classifications.join(", ")}</td>
                    `
                    tableBody.append(row)
                }
    })
    .catch((e)=>{alert("error testing entity");console.log(e)})
})
