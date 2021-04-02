import {createPagination} from './utils/utils'
import {createTable as dataModalTable} from './data_table_modal_aspect_topic'
function createTable(page){
    let content = document.getElementById("aspect-topic-table-content");
    content.innerHTML = "";
    let pagination = document.getElementById("aspect-topic-table-pagination");
    let pageSize = document.getElementById("aspect-topic-table-page-size").value
    pagination.innerHTML = ""
    fetch(`/api/aspect-topic/project/${window.project_id}/?page=${page}&page-size=${pageSize}`)
    .then((response) => response.json())
    .then((data) => {
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
                    console.log(dataAspectLabel)
                    let dataTopicLabel = e.target.getAttribute("data-topic")
                    console.log(dataTopicLabel)
                    let sentiment = e.target.getAttribute("data-sentiment")
                    document.querySelector("#data-table-modal").style.display = "block"
                    dataModalTable(1, dataAspectLabel, dataTopicLabel, sentiment)
                })
            }
            let firstElement = data.pageSize * (data.currentPage - 1);
            let lastElement = firstElement + data.pageSize;
            createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
    });
}
createTable(1);
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