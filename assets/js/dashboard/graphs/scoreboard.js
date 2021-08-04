import { update } from "../helpers/helpers";
import {
    showLoadingScreen,
    hideLoadingScreen,
} from "../../common/loading-screen";
export function createGraph() {
    update.startUpdate();
    fetch(`/api/aspects-per-project/${window.project_id}/`)
        .then((response) => response.json())
        .then((data) => {
            let weightsDiv = document.querySelector("#scoreboard-weight");
            for (let aspect of data) {
                let html = `<div class="row col-12"><label class="form-label">${aspect.rule_name}</label>
                <div class="row col-12">
                <input class="col-10" type="range" class="form-range" min="0" max="10" data-aspect-rule-id="${aspect.id}" data-aspect-rule-weight="${aspect.weight}" value="${aspect.weight}" oninput="this.nextElementSibling.value = this.value" step="1"><output class="col-2">${aspect.weight}</output>
                </div>
            </div>`;
                weightsDiv.innerHTML += html;
            }
            document
                .querySelectorAll("#scoreboard-weight input[type='range']")
                .forEach((element) => {
                    element.addEventListener("change", (e) => {
                        let input = e.currentTarget
                        let aspect_rule_id = input.getAttribute("data-aspect-rule-id")
                        showLoadingScreen();
                        fetch(`/api/update-aspect-rule-weight/${aspect_rule_id}/?weight=${input.value}`, {
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
            ).innerHTML = `Maximum score = ${data.length * 100}`;
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
            totalScore += parseInt(e.value/10*100);
        });
    document.querySelector("#scoreboard-score").innerHTML = totalScore;
}
