import * as d3 from 'd3'
import cloud from 'd3-cloud'
import React from 'react';
import ReactDOM from 'react-dom'
import ReactWordCloud from 'react-wordcloud';

let words = []
let wordsContainer = document.querySelector("#word-cloud-modal-container")
export default function word_cloud(url) {
    words = []
    ReactDOM.unmountComponentAtNode(wordsContainer)
    fetch(url).then(response => response.json()).then(data => {
        for(let element of data){
            words.push({text: element.keyword, value: element.keywordCount})
        }

		const options = {
		  colors: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
		  enableTooltip: false,
		  deterministic: false,
		  fontFamily: "impact",
		  fontSizes: [18, 80],
		  fontStyle: "normal",
		  fontWeight: "normal",
		  padding: 1,
		  rotations: 3,
		  rotationAngles: [0, 90],
		  scale: "sqrt",
		  spiral: "archimedean",
		  transitionDuration: 1000
		};
            let component = () => {
                return <ReactWordCloud words={words} options={options} maxWords={50}/>
            }
            ReactDOM.render(component(), wordsContainer)

        /*let width = window.innerWidth * 0.8
        let height = window.innerHeight * 0.7
        console.log(data)
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
                return {text: d.keyword, size: 180*(d.keywordCount/maxCount), keyCount:d.keywordCount};
                }))
                .padding(5)
                .rotate(function() { return ~~(Math.random() * 2) * 90; })
                .font("Impact")
                .fontSize(function(d) { return d.size; })
                .on("end", draw);
        
            layout.start();
        } else {
            document.querySelector("#word-cloud-modal-container").innerHTML = "No keywords available"
        }*/
    })
    .catch(()=>{
        ReactDOM.unmountComponentAtNode(wordsContainer)
        document.querySelector("#word-cloud-modal-container").innerHTML = "No keywords available"
    })
}

function renderWordCloud(){

    if(words.length){
        const options = {
            rotations: 0,
            fontSizes: [25, 50],
        }
        let component = () => {
            return <ReactWordCloud words={words} options={options} maxWords={50}/>
        }
        ReactDOM.render(component(), wordsContainer)
    }
}

document.querySelector("#show-word-cloud-modal").addEventListener("click", renderWordCloud)
