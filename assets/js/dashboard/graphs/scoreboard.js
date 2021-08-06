import { update } from "../helpers/helpers";
import {
    showLoadingScreen,
    hideLoadingScreen,
} from "../../common/loading-screen";
let total_data = 0

export function createGraph() {
    update.startUpdate();
    fetch(`/api/aspect-weight-scoreboard/${window.project_id}/`)
        .then((response) => response.json())
        .then((data) => {
            let weightsDiv = document.querySelector("#scoreboard-weight");
            total_data = parseInt(data.data.total_aspects_data)
            for (let aspect of data.data.aspect_weights) {
                let html = `<div class="row col-12"><label class="form-label">${aspect.rule_name}</label>
                <div class="row col-12">
                <input class="col-10" type="range" class="form-range" min="0" max="10" data-aspect-weigth-id="${aspect.id}" data-total-aspect-positives="${aspect.total_positives}" data-total-aspect-data="${aspect.total_aspect_data}" data-aspect-weight="${aspect.weight}" value="${aspect.weight}" oninput="this.nextElementSibling.value = this.value" step="1"><output class="col-2">${aspect.weight}</output>
                </div>
            </div>`;
                weightsDiv.innerHTML += html;
            }
            document
                .querySelectorAll("#scoreboard-weight input[type='range']")
                .forEach((element) => {
                    element.addEventListener("change", (e) => {
                        let input = e.currentTarget
                        let aspect_weight_id = input.getAttribute("data-aspect-weigth-id")
                        showLoadingScreen();
                        fetch(`/api/update-aspect-rule-weight/${aspect_weight_id}/?weight=${input.value}`, {
                            method:"POST",
                        })
                        .then(resp => {})
                        .catch(e=> {
                            alert("error updating weight")
                            location.reload()
                        })
                        .finally(e=>{
                            hideLoadingScreen()
                            scoreboardScore();
                        })
                    });
                });
            document.querySelector(
                "#scoreboard-max-score"
            ).innerHTML = `Maximum score = ${data.data.aspect_weights.length * 100}`;
            scoreboardScore();
            update.finishUpdate();
        })
        .catch(() => {
            update.finishUpdate();
        });
}

// calculates score and put it on screen
function scoreboardScore() {
    let totalScore = 0;
    document
        .querySelectorAll("#scoreboard-weight input[type='range']")
        .forEach((e) => {
            let total_aspect_positives = parseInt(e.getAttribute("data-total-aspect-positives"))
            let total_aspect_data = parseInt(e.getAttribute("data-total-aspect-data"))
            totalScore += (total_aspect_positives/total_aspect_data*parseInt(e.value)/10*100);
        });
    document.querySelector("#scoreboard-score").innerHTML = totalScore.toFixed(2);
}
