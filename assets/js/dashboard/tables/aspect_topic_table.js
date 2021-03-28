import {createPagination} from './utils/utils'

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
            <a href="#" class="info-button green">${element.positivesCount}</a>
           </td>
           <td class="text-center">
            <a href="#" class="info-button red">${element.negativesCount}</a>
           </td>
            `;
                tr.innerHTML = row;
                content.append(tr);
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