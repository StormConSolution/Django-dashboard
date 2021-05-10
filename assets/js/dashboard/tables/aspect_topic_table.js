import {createPagination} from './utils/utils'
import {createTable as dataModalTable} from './data_table_modal_aspect_topic'
import {getFilters} from '../helpers/filters'
import {update} from '../helpers/helpers'
import wordCloud from '../graphs/word-cloud-modal'
export function createTable(page){
    update.startUpdate()
    makeTable(page)
}

let content = document.getElementById("aspect-topic-table-content");
function makeTable(page){
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("aspect-topic-table-pagination");
    let pageSize = document.getElementById("aspect-topic-table-page-size").value
    pagination.innerHTML = ""
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources,
        "sourcesID": filtersValues.sourcesID
    })
    document.getElementById("aspect-topic-table-csv").href= `/api/aspect-topic/project/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/aspect-topic/project/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = ""
        for (let element of data.data) {
            let tr = document.createElement("tr");
            let row = `
            <td>
            <a href="#" class="data-link">${element.topicLabel}</a>
           </td>
           <td>
             ${element.aspectLabel}
           </td>
           <td class="text-center">
            <a style="cursor:pointer" class="info-button green" data-aspect="${element.aspectLabel}" data-topic="${element.topicLabel}" data-sentiment="positive">${element.positivesCount}</a>
           </td>
           <td class="text-center">
            <a style="cursor:pointer" class="info-button red" data-aspect="${element.aspectLabel}" data-topic="${element.topicLabel}" data-sentiment="negative">${element.negativesCount}</a>
           </td>
            `;
                tr.innerHTML = row;
                content.append(tr);

            }
            let buttons =content.querySelectorAll("a[data-topic]")
            for(let button of buttons){
                button.addEventListener("click", (e)=>{
                    let dataAspectLabel = e.target.getAttribute("data-aspect")
                    let dataTopicLabel = e.target.getAttribute("data-topic")
                    let sentiment = e.target.getAttribute("data-sentiment")
                    document.querySelector("#data-table-modal").style.display = "block"
                    let filtersValues = getFilters()
                    let wordCloudURL = `/api/data-per-aspect-topic/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "aspect-label": encodeURIComponent(dataAspectLabel),
                        "topic-label": encodeURIComponent(dataTopicLabel),
                        "sentiment": sentiment,
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": encodeURIComponent(filtersValues.sources),
                        "sourcesID": filtersValues.sourcesID
                    })
                    wordCloud(wordCloudURL)
                    dataModalTable(1, {aspectLabel: dataAspectLabel, topicLabel: dataTopicLabel, sentiment: sentiment})
                })
            }
            let firstElement = data.pageSize * (data.currentPage - 1);
            let lastElement = firstElement + data.pageSize;
            createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
            update.finishUpdate()
    });
}

/* document.getElementById("aspect-topic-table-csv").addEventListener("click", ()=>{
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources)
    })
    fetch(`/api/aspect-topic/project/${window.project_id}/?format=csv&` + urlParams)
    .then(response => response.blob())
    .then(blob => {
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = "aspect_topic_breakdown.csv"
        document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
        a.click();    
        a.remove();
    })
}) */
//createTable(1);
/*
<div class="col-12 col-md-auto">
        <ul class="pagination">
        <li>
            <a href="#">
            <i class="fe fe-chevron-left"></i>
            </a>
        </li>
        <li class="active">
            <a href="#">01</a>
        </li>
        <li>
            <a href="#">02</a>
        </li>
        <li>
            <a href="#">03</a>
        </li>
        <li>
            <a href="#">04</a>
        </li>
        <li>
            <a href="#">..</a>
        </li>
        <li>
            <a href="#">25</a>
        </li>
        <li>
            <a href="#"> <i class="fe fe-chevron-right"></i></a>
        </li>
        
        </ul>
    </div>
*/