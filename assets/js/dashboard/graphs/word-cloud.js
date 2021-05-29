import * as d3 from 'd3'
import cloud from 'd3-cloud'

let wordsContainer = document.querySelector("#word-cloud-container")
let width = wordsContainer.offsetWidth
let height = wordsContainer.offsetHeight
fetch(`/api/keywords/${window.project_id}/`)
    .then(response => {
        if(response.status != 200){
            document.querySelector("#word-cloud-container").innerHTML = "No keywords available"
        } else {

            response.json()
        }
    }).then(data => {
    wordsContainer.innerHTML = ""
    if(data[0]){
        let maxCount = data[0].keywordCount
        var layout = cloud()
            .size([width, height])
            .words(data.map(function(d) {
            return {text: d.keyword, size: 90*(d.keywordCount/maxCount)};
            }))
            .padding(5)
            .rotate(function() { return ~~(Math.random() * 2) * 90; })
            .font("Impact")
            .fontSize(function(d) { return d.size; })
            .on("end", draw);
    
        layout.start();
    
        function draw(words) {
        d3.select("#word-cloud-container").append("svg")
            .attr("width", layout.size()[0])
            .attr("height", layout.size()[1])
            .append("g")
            .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", function(d) { return d.size + "px"; })
            .style("font-family", "Impact")
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
                return "translate(" + [d.x, d.y] + ")";
            })
            .text(function(d) { return d.text; });
        }
    } else {
        document.querySelector("#word-cloud-container").innerHTML = "No keywords available"
    }

})
