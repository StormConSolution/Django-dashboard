import * as d3 from 'd3'
import cloud from 'd3-cloud'

export default function word_cloud(url) {
    let wordsContainer = document.querySelector("#word-cloud-modal-container")
    wordsContainer.innerHTML = "Loading..."
    fetch(url).then(response => response.json()).then(data => {
        let width = window.innerWidth * 0.7
        let height = window.innerHeight * 0.5
  
        wordsContainer.innerHTML = ""
        if(data[0]){

            let maxCount = data[0].keywordCount
            var mycolor = d3.scaleLinear()
            .domain([10, maxCount])
            .range(["lightblue", "steelblue"]);
            function draw(words) {
                d3.select("#word-cloud-modal-container").append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .append("g")
                    .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
                    .selectAll("text")
                    .data(words)
                    .enter().append("text")
                    .style("font-size", function(d) { return d.size + "px"; })
                    .style("font-family", "Impact")
                    .style("fill", function(d){
                        return mycolor(d.keyCount)
                    })
                    .attr("text-anchor", "middle")
                    .attr("transform", function(d) {
                        return "translate(" + [d.x, d.y] + ")";
                    })
                    .text(function(d) { return d.text; });
                }
            var layout = cloud()
                .size([width, height])
                .words(data.map(function(d) {
                return {text: d.keyword, size: 90*(d.keywordCount/maxCount), keyCount:d.keywordCount};
                }))
                .padding(5)
                .rotate(function() { return ~~(Math.random() * 2) * 90; })
                .font("Impact")
                .fontSize(function(d) { return d.size; })
                .on("end", draw);
        
            layout.start();
        } else {
            document.querySelector("#word-cloud-modal-container").innerHTML = "No keywords available"
        }
    })
}